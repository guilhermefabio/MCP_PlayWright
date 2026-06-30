#!/usr/bin/env python3
"""
Playwright test generator powered by LLM.

Usage:
    python main.py "Describe the flow" [--url URL] [--user USER] [--password PASS]
                   [--provider PROV] [--model MODEL] [--headless] [--output DIR]
                   [--context TEXT]

Examples:
    python main.py "Login and navigate to Auditoria" --url https://app.com --user admin --password 123
    python main.py "Test checkout" --url https://shop.com --headless --provider claude
    python main.py "Create report" --url https://erp.com --user ops --password x \\
        --context "After login redirects to /dashboard. Sidebar has 'Relatórios'."

LLM provider (--provider or LLM_PROVIDER in .env):
    openai  — OpenAI GPT  (default; requires OPENAI_API_KEY)
    claude  — Anthropic   (requires ANTHROPIC_API_KEY)
    ollama  — Local Ollama (requires OLLAMA_BASE_URL and LLM_MODEL)
"""

import argparse
import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from agent.runner import TaskConfig, run_agent

BASE_DIR = Path(__file__).parent


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def main() -> None:
    _configure_logging()
    load_dotenv(BASE_DIR.parent / ".env")

    parser = argparse.ArgumentParser(
        description="Playwright test generator powered by LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="Natural language description of the flow to generate")
    parser.add_argument("--url", help="Base URL of the application (overrides BASE_URL in .env)")
    parser.add_argument("--user", help="Login username (overrides LOGIN_USER in .env)")
    parser.add_argument("--password", help="Login password (overrides LOGIN_PASSWORD in .env)")
    parser.add_argument(
        "--provider",
        choices=["openai", "claude", "ollama"],
        help="LLM provider (overrides LLM_PROVIDER in .env)",
    )
    parser.add_argument("--model", help="LLM model name (overrides LLM_MODEL in .env)")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser without a visible window",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory for generated files (default: current directory)",
    )
    parser.add_argument(
        "--context",
        "-c",
        default="",
        help="Extra context about the site (e.g. 'uses React, login at /auth')",
    )

    args = parser.parse_args()

    config = TaskConfig(
        prompt=args.prompt,
        url=args.url or os.getenv("BASE_URL", ""),
        user=args.user or os.getenv("LOGIN_USER", ""),
        password=args.password or os.getenv("LOGIN_PASSWORD", ""),
        provider=(args.provider or os.getenv("LLM_PROVIDER", "openai")).lower(),
        model=args.model or os.getenv("LLM_MODEL", ""),
        headless=args.headless,
        output_dir=Path(args.output),
        extra_context=args.context,
    )

    asyncio.run(run_agent(config))


if __name__ == "__main__":
    main()
