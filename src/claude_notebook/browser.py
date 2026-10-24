"""Drive the user's installed Chrome against notebook.google.com with a dedicated, persistent profile.

The user signs in once in a visible window (`login`); every later call reuses that profile headlessly.
Extraction is deliberately DOM-agnostic (visible text + links) so a page redesign degrades output
instead of breaking it.
"""
import asyncio
import os
import re
from pathlib import Path
from urllib.parse import urlparse

HOST = "notebook.google.com"
HOME = f"https://{HOST}/"
PROFILE_DIR = Path(os.environ.get("CLAUDE_NOTEBOOK_PROFILE") or Path.home() / ".claude-notebook" / "chrome-profile")
NOTEBOOK_ID = re.compile(r"/notebook/([0-9a-fA-F-]{8,})")
UUID = re.compile(r"^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")


class NotSignedIn(Exception):
    pass


def notebook_url(ref):
    """A notebook URL or bare id → its canonical URL. Refuses anything that isn't on notebook.google.com."""
    ref = (ref or "").strip()
    if UUID.match(ref):
        return f"{HOME}notebook/{ref}"
    u = urlparse(ref)
    if u.scheme == "https" and u.hostname == HOST:
        m = NOTEBOOK_ID.search(u.path)
        if m:
            return f"{HOME}notebook/{m.group(1)}"
    raise ValueError(f"not a notebook link or id: {ref!r} (expected https://{HOST}/notebook/<id>)")


SIGNED_OUT_PATHS = ("/login", "/trynow")  # signed out, the home page redirects to the /trynow landing page


def signed_in(url):
    u = urlparse(url or "")
    return u.hostname == HOST and not u.path.startswith(SIGNED_OUT_PATHS)


# Material Symbols render as ligature words in innerText ("add_2", "drive_pdf", "more_vert").
ICON_WORDS = {"markdown", "article", "image", "settings", "sort", "close", "language", "share", "search"}
ICON_TOKEN = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")


def clean_text(raw, max_chars=50_000):
    """Visible page text → compact text: trimmed lines, no icon words, no blank runs, no consecutive repeats."""
    out, prev = [], None
    for line in (raw or "").splitlines():
        line = re.sub(r"[ \t ]+", " ", line).strip()
        if line in ICON_WORDS or ICON_TOKEN.match(line):
            continue
        if line == prev or (not line and (not out or not out[-1])):
            continue
        out.append(line)
        prev = line
    text = "\n".join(out).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + f"\n\n[… truncated at {max_chars:,} characters]"
    return text


def notebooks_from_links(links):
    """[(href, text)] from the home page → [{"id", "title", "url"}], deduped by id, page order kept."""
    seen, out = set(), []
    for href, text in links:
        m = NOTEBOOK_ID.search(urlparse(href or "").path)
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        title = clean_text(text, 200).split("\n")[0] or "(untitled)"
        out.append({"id": m.group(1), "title": title, "url": f"{HOME}notebook/{m.group(1)}"})
    return out


class Browser:
    """One Chrome profile can only be open once, so every call takes the lock and closes when done."""

    def __init__(self, profile_dir=PROFILE_DIR):
        self.profile_dir = Path(profile_dir)
        self.lock = asyncio.Lock()

    async def _context(self, pw, headless):
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        # Google refuses sign-in in browsers that announce automation; this is the user's own account in
        # their own Chrome, so drop that banner/flag rather than make them sign in somewhere else.
        return await pw.chromium.launch_persistent_context(
            str(self.profile_dir), channel="chrome", headless=headless, viewport={"width": 1400, "height": 1000},
            ignore_default_args=["--enable-automation"], args=["--disable-blink-features=AutomationControlled"])

    async def _open(self, pw, url, headless=True):
        ctx = await self._context(pw, headless)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        try:
            await page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass  # chatty apps never go idle; what's rendered is enough
        if not signed_in(page.url):
            await ctx.close()
            raise NotSignedIn("not signed in to notebook.google.com — run the notebook_login tool first")
        return ctx, page

    async def login(self, timeout_s=300):
        from playwright.async_api import async_playwright
        async with self.lock, async_playwright() as pw:
            ctx = await self._context(pw, headless=False)
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            await page.goto(HOME, wait_until="domcontentloaded", timeout=60_000)
            try:
                for _ in range(int(timeout_s)):
                    if signed_in(page.url):
                        await asyncio.sleep(2)  # let the session cookies settle before closing
                        return True
                    await asyncio.sleep(1)
                return False
            finally:
                await ctx.close()

    async def status(self):
        from playwright.async_api import async_playwright
        async with self.lock, async_playwright() as pw:
            try:
                ctx, _ = await self._open(pw, HOME)
            except NotSignedIn:
                return False
            await ctx.close()
            return True

    async def list_notebooks(self):
        from playwright.async_api import async_playwright
        async with self.lock, async_playwright() as pw:
            ctx, page = await self._open(pw, HOME)
            try:
                links = await page.eval_on_selector_all(
                    'a[href*="/notebook/"]', "els => els.map(e => [e.href, e.innerText || e.getAttribute('aria-label') || ''])")
                found = notebooks_from_links(links)
                fallback = "" if found else clean_text(await page.inner_text("body"), 8_000)
                return found, fallback
            finally:
                await ctx.close()

    async def read_notebook(self, ref, max_chars=50_000):
        from playwright.async_api import async_playwright
        url = notebook_url(ref)
        async with self.lock, async_playwright() as pw:
            ctx, page = await self._open(pw, url)
            try:
                await asyncio.sleep(2)  # notebook panels render after the shell
                root = "main" if await page.query_selector("main") else "body"
                text = clean_text(await page.inner_text(root), max_chars)
                return {"title": await page.title(), "url": page.url, "text": text}
            finally:
                await ctx.close()
