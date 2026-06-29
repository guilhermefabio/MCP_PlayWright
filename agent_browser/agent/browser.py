"""Thin async wrapper around Playwright exposing the tools the agent needs."""

import asyncio
import json

from playwright.async_api import async_playwright, Page

# Timeouts (ms)
_TIMEOUT_NAVIGATE = 30_000
_TIMEOUT_CLICK = 10_000
_TIMEOUT_LOAD = 15_000

# Content limits (chars) — keeps LLM context manageable
_SNAPSHOT_LIMIT = 8_000
_TEXT_LIMIT = 4_000
_HTML_LIMIT = 6_000


class Browser:
    """Chromium browser controlled by Playwright for the agent to inspect and interact with."""

    def __init__(self, headless: bool = False) -> None:
        self._headless = headless
        self._pw = None
        self._browser = None
        self._page: Page | None = None

    async def start(self) -> None:
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self._headless)
        self._page = await self._browser.new_page()

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

    async def navigate(self, url: str) -> str:
        await self._page.goto(url, wait_until="networkidle", timeout=_TIMEOUT_NAVIGATE)
        return f"Página: {await self._page.title()} | URL: {self._page.url}"

    async def snapshot(self) -> str:
        tree = await self._page.accessibility.snapshot()
        return json.dumps(tree, indent=2, ensure_ascii=False)[:_SNAPSHOT_LIMIT]

    async def get_inputs(self) -> str:
        inputs = await self._page.evaluate("""
            () => Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                placeholder: el.placeholder || '',
                label: (() => {
                    if (el.id) {
                        const lbl = document.querySelector('label[for="' + el.id + '"]');
                        return lbl ? lbl.innerText.trim() : '';
                    }
                    return '';
                })(),
                visible: el.offsetParent !== null && el.type !== 'hidden',
            })).filter(el => el.visible)
        """)
        return json.dumps(inputs, indent=2, ensure_ascii=False)

    async def click(self, selector: str) -> str:
        await self._page.locator(selector).first.click(timeout=_TIMEOUT_CLICK)
        await self._page.wait_for_load_state("networkidle", timeout=_TIMEOUT_LOAD)
        return f"Clicou: {selector} | Página: {await self._page.title()}"

    async def fill(self, selector: str, value: str) -> str:
        loc = self._page.locator(selector).first
        await loc.wait_for(state="visible", timeout=_TIMEOUT_CLICK)
        await loc.fill(value)
        return f"Preencheu '{selector}'"

    async def press_key(self, key: str) -> str:
        await self._page.keyboard.press(key)
        await self._page.wait_for_load_state("networkidle", timeout=_TIMEOUT_LOAD)
        return f"Pressionou: {key} | Página: {await self._page.title()}"

    async def get_text(self) -> str:
        return (await self._page.inner_text("body"))[:_TEXT_LIMIT]

    async def get_html(self, selector: str = "body") -> str:
        return (await self._page.inner_html(selector))[:_HTML_LIMIT]

    async def wait(self, milliseconds: int = 1000) -> str:
        await asyncio.sleep(milliseconds / 1000)
        return f"Aguardou {milliseconds}ms"
