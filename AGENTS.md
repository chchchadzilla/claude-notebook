# AGENTS.md — instructions for AI coding agents

This file tells AI assistants (Claude Code, Codex, Cursor, Gemini CLI, …) how to work in this repo.
`CLAUDE.md` just points here, so there is one source of truth.

## What this is

`claude-notebook` is an MCP server that lets Claude read the owner's notebooks on **Gemini Notebook**
(`notebook.google.com`). There is no public API, so it drives the user's own installed Chrome (via
Playwright) with a dedicated, persistent profile that the user signs in to once.

## Layout

| Path | What lives there |
| --- | --- |
| `src/claude_notebook/server.py` | MCP tools (`notebook_login`, `notebook_status`, `list_notebooks`, `read_notebook`, `redaction_status`) |
| `src/claude_notebook/browser.py` | Chrome/Playwright driving, URL validation, text cleanup |
| `src/claude_notebook/redact.py` | Client-name redaction applied to every tool result |
| `tests/` | pytest unit tests — no network, no browser |

## Commands

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest -q
```

## Rules

1. **Redaction is a hard guarantee.** Every string a tool returns must pass through `redact(...)` in
   `server.py`. Never add a tool or error path that returns notebook text unredacted.
2. **Never commit personal data.** No real notebook ids, Google account details, client names, or
   anything from `~/.claude-notebook/` (the Chrome profile and `redact.txt` live there on purpose).
   Tests use made-up ids.
3. **Only `notebook.google.com`.** `notebook_url()` refuses every other host; keep it that way.
4. **Read-only.** Nothing writes to the user's notebooks unless the owner explicitly asks for it.
5. **DOM-agnostic extraction.** Prefer visible text and links over brittle CSS selectors, so a Google
   redesign degrades output instead of breaking it.
6. **One browser at a time.** Chrome locks a profile; every browser operation goes through `Browser.lock`.
7. This uses the **mcp 2.x** SDK: `from mcp.server.mcpserver import MCPServer` (FastMCP was renamed).

## Known quirks (keep in mind when changing things)

- Signed out, `https://notebook.google.com/` redirects to `/trynow` (a landing page), not to a login page.
- Material icon names (`add_2`, `drive_pdf`) appear in `innerText`; `clean_text` filters them.
- Home-page notebook links have no text, so `list_notebooks` titles show as `(untitled)` (open issue).
- Windows editors write `redact.txt` with a BOM; it's read as `utf-8-sig`.
