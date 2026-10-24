# About claude-notebook

## Why it exists

I keep a Gemini Notebook that's a running record of everything I've built and who I built it for —
resumes, READMEs, project write-ups, client deliverables. I wanted Claude to *know* that history
(so it stops asking what I've made) without me copy-pasting a 235-source notebook into chat.

Gemini Notebook has no API. So this does the next most honest thing: it opens the notebook in my own
Chrome, signed in as me, reads what's on the screen, and hands that text to Claude through MCP (the
standard way Claude Code plugs into outside tools).

The second reason is privacy. A lot of that notebook names clients. So every word passes through a
redaction list on my own machine *before* Claude sees it — client names become `[Client A]`,
`[Client B]`, and the list itself never leaves the computer.

## Interesting quirks

- **It uses your real Chrome, not a bundled browser.** Playwright can download its own Chromium, but
  Google often refuses to sign in to "automated" browsers. Driving the Chrome you already have, with a
  separate profile, avoids both the 150 MB download and the sign-in wall.
- **Its own profile, not your everyday one.** The session lives in `~/.claude-notebook/chrome-profile`.
  Your normal Chrome tabs, history and passwords are never touched. Delete that folder and it's signed out.
- **"Signed out" doesn't look like signed out.** Visit the home page without an account and Google
  doesn't show a login page — it quietly sends you to a marketing page at `/trynow`. The code treats
  that as signed out (an early version didn't, and cheerfully reported "signed in").
- **Icons leak into the text.** Google's icon font renders words like `add_2` and `more_vert` as
  pictures; read the page as text and you get the words. They're filtered out.
- **Redaction catches names hiding in filenames.** `Acme-01-Filing.pdf` and `acme_summary.md` both
  become `[Client A]…` — the matcher treats `-` and `_` as word breaks, but leaves `Acmeville` alone.
- **It reads what's visible, on purpose.** No fragile CSS selectors. If Google redesigns the page,
  you get messier text, not a crash.
- **One at a time.** Chrome only lets one program use a profile, so tool calls queue up while a
  sign-in window is open.

## What it doesn't do (yet)

- Notebook titles in the list come back as `(untitled)` — the home page links carry no text.
- It reads the notebook page (source list, chat history, Studio panel), not the full contents of
  each source document.
- It never writes to your notebooks.
