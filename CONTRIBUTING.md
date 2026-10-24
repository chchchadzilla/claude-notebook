# Contributing

Thanks for wanting to help! Small, focused changes are the easiest to review.

## Set up

Follow **Install** in [README.md](README.md), then install the test tools too:

```powershell
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest -q
```

All tests must pass before you open a pull request. They run without a browser or network.

## Ground rules

1. **Redaction can't be bypassed.** Anything a tool returns goes through `redact(...)`. A PR that adds an
   unredacted path won't be merged.
2. **No personal data in commits.** Use made-up notebook ids (`00000000-0000-0000-0000-000000000000`) in
   tests. Never commit anything from `~/.claude-notebook/`.
3. **Stay on `notebook.google.com` and stay read-only** unless an issue agrees otherwise first.
4. **Add a test** for any bug fix or new behaviour.
5. Match the existing style: small functions, short comments explaining *why*, not *what*.

## Reporting bugs

Open an issue with: what you ran, what you expected, what happened, your OS, Python and Chrome versions.
**Remove any notebook text, ids or names before pasting output.**

## Pull requests

1. Fork the repo and create a branch: `git checkout -b fix/short-description`.
2. Make the change, add or update tests, run `pytest`.
3. Open a PR explaining the *why*. Link the issue if there is one.

By contributing you agree your work is released under the [MIT License](LICENSE).
