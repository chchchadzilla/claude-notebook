# claude-notebook

**Let Claude read your Gemini Notebooks** (`notebook.google.com`), with your client names blacked out
before Claude ever sees them.

You ask Claude Code things like *"read my portfolio notebook and list what I've built"*, and it opens the
notebook in your own Chrome (signed in as you), reads it, and answers. No copy-pasting, no API keys.

> **New to all this?** Perfect — this guide assumes you've never used a terminal or git. Every step says
> exactly what to type and what you should see. Skim the [glossary](#glossary) if a word is unfamiliar.

---

## Contents

1. [What you need](#1-what-you-need)
2. [Open PowerShell](#2-open-powershell)
3. [Install the tools](#3-install-the-tools-one-time)
4. [Download claude-notebook](#4-download-claude-notebook)
5. [Set it up](#5-set-it-up)
6. [Connect it to Claude Code](#6-connect-it-to-claude-code)
7. [Sign in to Google (once)](#7-sign-in-to-google-once)
8. [Hide your client names](#8-hide-your-client-names-recommended)
9. [Use it](#9-use-it)
10. [Troubleshooting](#10-troubleshooting)
11. [Updating and uninstalling](#11-updating-and-uninstalling)
12. [How it works](#how-it-works) · [Privacy](#privacy--safety) · [Glossary](#glossary)

---

## 1. What you need

| Thing | Why | Free? |
| --- | --- | --- |
| A **Windows 10 or 11** PC | These steps are written for Windows (Mac/Linux: see the note in step 5) | — |
| **Google Chrome** | claude-notebook drives your Chrome to read the notebook | ✅ |
| **Python 3.10 or newer** | claude-notebook is written in Python | ✅ |
| **Claude Code** | The Claude app that will use these tools | Needs a Claude plan |
| A **Google account** with Gemini Notebook | Where your notebooks live | ✅ |
| **Git** *(optional)* | Only if you'd rather download with git than as a ZIP | ✅ |

Time needed: about **15 minutes** the first time.

## 2. Open PowerShell

PowerShell is the window where you type commands. Every gray box below is something you type there.

1. Press the **Windows key**, type `PowerShell`, press **Enter**.
2. A blue or black window opens with a line ending in `>`. That's it — you're ready.

**How to run a command:** click in the window, paste (right-click or `Ctrl+V`) the command from a gray
box, press **Enter**, and wait until the `>` line comes back.

## 3. Install the tools (one time)

Skip any you already have. To check, run the "check" command — if it prints a version, you have it.

### Python

```powershell
python --version
```

If you see `Python 3.10` or higher, skip ahead. Otherwise:

```powershell
winget install -e --id Python.Python.3.12
```

Then **close PowerShell and open a new one** (so it notices Python), and run `python --version` again.

> No `winget`? Download Python from <https://www.python.org/downloads/>, run the installer, and
> **tick "Add python.exe to PATH"** on the first screen before clicking *Install Now*.

### Google Chrome

If you don't have it: `winget install -e --id Google.Chrome` (or download from <https://www.google.com/chrome/>).

### Claude Code

```powershell
claude --version
```

No version? Install it by following <https://docs.anthropic.com/en/docs/claude-code/setup>, then run
`claude` once and sign in when it asks.

## 4. Download claude-notebook

Pick **one** option.

**Option A — ZIP (easiest, no git needed)**

1. Go to <https://github.com/chchchadzilla/claude-notebook>.
2. Click the green **Code** button → **Download ZIP**.
3. Open your Downloads folder, right-click the ZIP → **Extract All…** → change the destination to `C:\`
   → **Extract**.
4. Rename the new folder from `claude-notebook-main` to `claude-notebook`, so it's at `C:\claude-notebook`.

**Option B — git**

```powershell
git clone https://github.com/chchchadzilla/claude-notebook C:\claude-notebook
```

## 5. Set it up

Run these three commands, one at a time:

```powershell
cd C:\claude-notebook
python -m venv .venv
.venv\Scripts\python -m pip install -e .
```

What they do: move into the folder · create a private Python space (`.venv`) just for this project ·
install claude-notebook and its two dependencies into it:

- [`mcp`](https://pypi.org/project/mcp/) — the protocol Claude Code uses to talk to tools
- [`playwright`](https://pypi.org/project/playwright/) — lets Python control Chrome

The last one takes a minute and prints a lot. It's done when you see `Successfully installed …`.

> **Mac / Linux:** use `python3` instead of `python`, and `.venv/bin/python` instead of
> `.venv\Scripts\python` everywhere. Not yet tested there.

## 6. Connect it to Claude Code

Still in `C:\claude-notebook`, run:

```powershell
claude mcp add --scope user notebook "$PWD\.venv\Scripts\claude-notebook.exe"
```

This tells Claude Code: *"there's a tool server called `notebook`; start it with this program."*
`--scope user` makes it available in every folder you use Claude Code in.

> **Why the `.exe` and not `python -m …`?** In PowerShell, `claude` is a script wrapper that silently
> eats the `--` separator, so `claude mcp add … -- python -m claude_notebook` fails with
> `unknown option '-m'`. The `claude-notebook.exe` launcher (created in step 5) needs no extra arguments.
> Mac/Linux: use `"$PWD/.venv/bin/claude-notebook"`.

Check it worked:

```powershell
claude mcp list
```

You should see a line starting with `notebook:` that ends in **✓ Connected**.

## 7. Sign in to Google (once)

1. Start Claude Code: type `claude` and press Enter.
2. Type: **`sign me in to my notebook`**
3. A Chrome window opens on Gemini Notebook. Click **Sign in** and log in with your Google account.
4. When your notebooks appear, the window closes by itself (you have 5 minutes). Claude says
   *"Signed in"*.

You won't need to do this again unless you sign out or Google expires the session.

## 8. Hide your client names (recommended)

If your notebooks mention clients or other people, list their names so they're replaced with
`[Client A]`, `[Client B]`… **before Claude sees anything**.

1. Open the list in Notepad (it's created if it doesn't exist):

   ```powershell
   mkdir "$HOME\.claude-notebook" -Force | Out-Null; notepad "$HOME\.claude-notebook\redact.txt"
   ```

2. Type one name per line, save, close:

   ```text
   # lines starting with # are notes
   Acme Corp
   Jane Doe = [Client A lead]
   Doe
   ```

   - Matching ignores upper/lower case and only matches **whole words** (`Acme` won't touch `Acmeville`).
   - It also catches names inside filenames like `Acme-01-Invoice.pdf`.
   - Put full names *and* last names if both appear. Longer names are matched first.
   - `Name = [label]` picks your own label; otherwise labels are assigned in order.
3. Changes apply to the very next request — no restart needed.

Ask Claude **`how many names are redacted?`** to confirm (it reports the count, never the names).

> ⚠️ Only names on the list are hidden. Skim a notebook's output once and add anything that slipped through.

## 9. Use it

In Claude Code, just ask in plain English:

| You type | What happens |
| --- | --- |
| `list my notebooks` | Lists your notebooks with their links |
| `read my notebook https://notebook.google.com/notebook/…` | Reads that notebook's visible text |
| `summarize what's in that notebook` | Claude reads, then summarizes |
| `am I signed in to my notebook?` | Checks the saved session |

The tools behind those requests:

| Tool | Does |
| --- | --- |
| `notebook_login` | Opens Chrome so you can sign in; waits until you have |
| `notebook_status` | Is the saved session still signed in? |
| `list_notebooks` | Your notebooks: title + link |
| `read_notebook` | The visible text of one notebook (link or id) |
| `redaction_status` | How many names are being hidden, and where the list is |

## 10. Troubleshooting

| Problem | Fix |
| --- | --- |
| `python` is not recognized | Python isn't installed or not on PATH. Redo step 3, then **open a new PowerShell window**. |
| `claude` is not recognized | Install Claude Code (step 3), then open a new PowerShell window. |
| `claude mcp list` shows `notebook` ✗ Failed | Re-run step 5, then step 6 from inside `C:\claude-notebook`. |
| "not signed in — run the notebook_login tool first" | Ask Claude `sign me in to my notebook` (step 7). |
| Chrome says "This browser or app may not be secure" | Close all claude-notebook Chrome windows and try again; make sure Chrome is up to date. |
| Error mentioning `chrome` not found | Install Google Chrome (step 3). |
| A tool seems stuck | A sign-in window may be open — finish or close it. Only one tool runs at a time. |
| Notebook titles say `(untitled)` | Known limitation — use the link to tell them apart. |
| A client name still shows | Add it to `redact.txt` (step 8). |

Still stuck? [Open an issue](https://github.com/chchchadzilla/claude-notebook/issues) — remove any
notebook text and names before pasting.

## 11. Updating and uninstalling

**Update (ZIP):** download the ZIP again, replace the folder, re-run step 5.
**Update (git):** `cd C:\claude-notebook; git pull; .venv\Scripts\python -m pip install -e .`

**Uninstall:**

```powershell
claude mcp remove notebook --scope user
Remove-Item -Recurse -Force C:\claude-notebook
Remove-Item -Recurse -Force "$HOME\.claude-notebook"   # also deletes your sign-in and redaction list
```

---

## How it works

```
Claude Code ──MCP──▶ claude-notebook ──Playwright──▶ your Chrome (own profile) ──▶ notebook.google.com
     ▲                     │
     └── redacted text ◀───┘  (names on your redact.txt replaced on your PC)
```

1. Claude Code starts `claude-notebook` in the background when it needs it.
2. When asked to read, it starts Chrome invisibly with a separate profile in
   `~/.claude-notebook/chrome-profile`, opens the notebook, and grabs the visible text.
3. The text is cleaned up, client names are replaced, and only then returned to Claude.

Quirks and the story behind the project: [ABOUT.md](ABOUT.md).

## Privacy & safety

- **Read-only.** It never edits, deletes or shares your notebooks.
- **Only `notebook.google.com`.** It refuses to open any other site.
- **Separate Chrome profile.** Your normal browsing, passwords and tabs aren't touched.
- **Your sign-in stays on your PC** in `~/.claude-notebook/chrome-profile`. Treat that folder like a
  password; delete it to sign out.
- **Redaction happens locally**, before Claude sees the text. The redaction list never leaves your PC.
- The text Claude *does* see is sent to Claude like anything else you discuss with it.

## For developers

```powershell
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest -q
```

Code map and rules for contributors (and AI agents): [AGENTS.md](AGENTS.md) · [CONTRIBUTING.md](CONTRIBUTING.md).

## Glossary

- **Terminal / PowerShell** — a window where you type commands instead of clicking.
- **Repository (repo)** — a project folder stored on GitHub, with its full history.
- **Git** — a tool that downloads and tracks changes to repos. Optional here.
- **Python** — the programming language this is written in.
- **Virtual environment (`.venv`)** — a private copy of Python packages for one project, so nothing
  else on your PC is affected.
- **MCP (Model Context Protocol)** — the standard way Claude connects to outside tools.
- **Playwright** — a library that lets a program control a web browser.
- **Redaction** — replacing sensitive words (here, names) with placeholders.

## License

[MIT](LICENSE) © 2026 Chad Keith — use it, change it, share it; keep the copyright notice.
