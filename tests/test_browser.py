import pytest

from claude_notebook.browser import clean_text, notebook_url, notebooks_from_links, signed_in

NB = "0a1b2c3d-1111-4222-8333-444455556666"


def test_notebook_url_accepts_links_and_ids_only_on_the_real_host():
    assert notebook_url(NB) == f"https://notebook.google.com/notebook/{NB}"
    assert notebook_url(f"https://notebook.google.com/notebook/{NB}?authuser=0") == f"https://notebook.google.com/notebook/{NB}"
    for bad in ("", "hello", f"https://evil.example/notebook/{NB}", f"http://notebook.google.com/notebook/{NB}",
                f"https://notebook.google.com.evil.example/notebook/{NB}"):
        with pytest.raises(ValueError):
            notebook_url(bad)


def test_signed_in():
    assert signed_in(f"https://notebook.google.com/notebook/{NB}")
    assert not signed_in("https://notebook.google.com/login?continue=x")
    assert not signed_in("https://notebook.google.com/trynow")
    assert not signed_in("https://accounts.google.com/ServiceLogin")


def test_clean_text():
    raw = "  Title  \n\n\n\nSources\nSources\n  a  b \n\n"
    assert clean_text(raw) == "Title\n\nSources\na b"
    assert clean_text("Sources\nadd_2\nAdd sources\nmarkdown\nabout.md\ndrive_pdf\nresume.pdf\nmore_vert") == \
        "Sources\nAdd sources\nabout.md\nresume.pdf"
    assert clean_text("x" * 50, max_chars=10).startswith("xxxxxxxxxx\n\n[… truncated")


def test_notebooks_from_links_dedupes_and_ignores_other_links():
    links = [(f"https://notebook.google.com/notebook/{NB}", "About me\n3 sources"),
             (f"https://notebook.google.com/notebook/{NB}#share", "About me"),
             ("https://notebook.google.com/settings", "Settings"),
             ("https://notebook.google.com/notebook/1234abcd-0000-0000-0000-000000000000", "")]
    out = notebooks_from_links(links)
    assert [n["title"] for n in out] == ["About me", "(untitled)"]
    assert out[0]["url"].endswith(NB)
