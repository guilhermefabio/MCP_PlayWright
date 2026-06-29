"""Parse LLM output and write generated files to disk."""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def write_generated_files(text: str, output_dir: Path = Path(".")) -> None:
    """Extract file blocks from LLM output and write them to *output_dir*.

    Supports two formats:
    - Primary:  ``<file path="pages/foo.py">...</file>``
    - Fallback: Markdown fenced block whose first line is ``# pages/foo.py``
    """
    saved = False

    for rel_path, content in re.findall(r'<file path="([^"]+)">(.*?)</file>', text, re.DOTALL):
        _save(rel_path, content, output_dir)
        saved = True

    if not saved:
        for block in re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL):
            lines = block.splitlines()
            if lines and lines[0].strip().startswith("#"):
                candidate = lines[0].strip().lstrip("# ").strip()
                if "/" in candidate and candidate.endswith(".py"):
                    _save(candidate, "\n".join(lines[1:]), output_dir)
                    saved = True

    if not saved:
        logger.warning("Nenhum arquivo gerado — o LLM não usou o formato <file path=...>")


def _save(rel_path: str, content: str, output_dir: Path) -> None:
    target = output_dir / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    logger.info("Arquivo salvo: %s", target)
