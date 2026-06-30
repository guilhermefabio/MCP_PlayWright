"""Agent orchestration — TaskConfig and per-provider agentic loops."""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.browser import Browser
from agent.prompts import build_system_prompt
from agent.tools import TOOLS_ANTHROPIC, TOOLS_OPENAI, call_tool
from agent.writer import write_generated_files

logger = logging.getLogger(__name__)

_MAX_TOKENS = 8_096
_MAX_ITERATIONS = 30


@dataclass
class TaskConfig:
    """All parameters needed to run the agent for a single task."""

    prompt: str
    url: str = ""
    user: str = ""
    password: str = ""
    provider: str = "openai"
    model: str = ""
    headless: bool = False
    output_dir: Path = field(default_factory=Path)
    extra_context: str = ""

    _DEFAULTS: dict[str, str] = field(
        default_factory=lambda: {
            "openai": "gpt-4o",
            "claude": "claude-sonnet-4-6",
            "ollama": "llama3.2",
        },
        init=False,
        repr=False,
    )

    def effective_model(self) -> str:
        if self.model:
            return self.model
        return self._DEFAULTS.get(self.provider, "gpt-4o")

    def full_prompt(self) -> str:
        parts = [self.prompt]
        if self.url:
            parts.append(f"URL base: {self.url}")
        if self.user:
            parts.append(f"Usuário: {self.user}")
        if self.password:
            parts.append(f"Senha: {self.password}")
        if self.extra_context:
            parts.append(f"Contexto adicional: {self.extra_context}")
        return "\n".join(parts)


async def run_agent(config: TaskConfig) -> None:
    """Launch browser, run the agentic loop for the given provider, write output files."""
    model = config.effective_model()
    system_prompt = build_system_prompt(config)

    logger.info("Provedor : %s", config.provider)
    logger.info("Modelo   : %s", model)
    logger.info("URL      : %s", config.url or "(não informada)")
    logger.info("Headless : %s", config.headless)
    logger.info("Saída    : %s", config.output_dir.resolve())
    logger.info("Prompt   : %s", config.prompt)

    browser = Browser(headless=config.headless)
    await browser.start()
    try:
        if config.provider in ("openai", "ollama"):
            from openai import OpenAI

            if config.provider == "openai":
                client: Any = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            else:
                client = OpenAI(
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                    api_key="ollama",
                )
            await _run_openai_compat(client, model, config, system_prompt, browser)

        elif config.provider == "claude":
            from anthropic import Anthropic

            client = Anthropic()
            await _run_anthropic(client, model, config, system_prompt, browser)

        else:
            raise ValueError(
                f"Provedor desconhecido: '{config.provider}'. Use: openai, claude ou ollama"
            )
    finally:
        await browser.stop()


_CODEGEN_PROMPT = (
    "Fluxo executado com sucesso. "
    'Agora gere os arquivos de código no formato <file path="...">. '
    'Não chame nenhuma ferramenta — responda APENAS com os blocos <file path="...">.'
)


async def _run_openai_compat(
    client: Any,
    model: str,
    config: TaskConfig,
    system_prompt: str,
    browser: Browser,
) -> None:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": config.full_prompt()},
    ]
    for iteration in range(_MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=model,
            max_tokens=_MAX_TOKENS,
            tools=TOOLS_OPENAI,
            messages=messages,
        )
        choice = response.choices[0]

        if choice.finish_reason == "stop":
            text = choice.message.content or ""
            write_generated_files(text, config.output_dir)
            break

        if choice.finish_reason == "tool_calls":
            text = choice.message.content or ""
            if '<file path="' in text:
                write_generated_files(text, config.output_dir)
                break

            tool_names = [tc.function.name for tc in (choice.message.tool_calls or [])]
            messages.append(choice.message)
            for tc in choice.message.tool_calls or []:
                args = json.loads(tc.function.arguments or "{}")
                logger.info("  -> %s(%s)", tc.function.name, json.dumps(args)[:100])
                result = await call_tool(browser, tc.function.name, args, config.output_dir)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

            if "task_complete" in tool_names:
                logger.info("task_complete — gerando código...")
                messages.append({"role": "user", "content": _CODEGEN_PROMPT})
                codegen = client.chat.completions.create(
                    model=model,
                    max_tokens=_MAX_TOKENS,
                    messages=messages,
                )
                write_generated_files(codegen.choices[0].message.content or "", config.output_dir)
                break
            continue

        logger.warning(
            "finish_reason inesperado '%s' na iteração %d — encerrando",
            choice.finish_reason,
            iteration,
        )
        text = choice.message.content or ""
        if text:
            write_generated_files(text, config.output_dir)
        break
    else:
        logger.warning("Limite de %d iterações atingido — encerrando loop OpenAI", _MAX_ITERATIONS)


async def _run_anthropic(
    client: Any,
    model: str,
    config: TaskConfig,
    system_prompt: str,
    browser: Browser,
) -> None:
    messages: list[dict[str, Any]] = [{"role": "user", "content": config.full_prompt()}]
    for iteration in range(_MAX_ITERATIONS):
        response = client.messages.create(
            model=model,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            tools=TOOLS_ANTHROPIC,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    write_generated_files(block.text, config.output_dir)
            break

        if response.stop_reason == "tool_use":
            for block in response.content:
                if hasattr(block, "text") and '<file path="' in block.text:
                    write_generated_files(block.text, config.output_dir)
                    return

            tool_names = [b.name for b in response.content if b.type == "tool_use"]
            tool_results: list[dict[str, Any]] = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("  -> %s(%s)", block.name, json.dumps(block.input)[:100])
                    result = await call_tool(browser, block.name, block.input, config.output_dir)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            if "task_complete" in tool_names:
                logger.info("task_complete — gerando código...")
                messages.append({"role": "user", "content": _CODEGEN_PROMPT})
                codegen = client.messages.create(
                    model=model,
                    max_tokens=_MAX_TOKENS,
                    system=system_prompt,
                    messages=messages,
                )
                for block in codegen.content:
                    if hasattr(block, "text"):
                        write_generated_files(block.text, config.output_dir)
                return
            continue

        logger.warning(
            "stop_reason inesperado '%s' na iteração %d — encerrando",
            response.stop_reason,
            iteration,
        )
        for block in response.content:
            if hasattr(block, "text"):
                write_generated_files(block.text, config.output_dir)
        break
    else:
        logger.warning(
            "Limite de %d iterações atingido — encerrando loop Anthropic", _MAX_ITERATIONS
        )
