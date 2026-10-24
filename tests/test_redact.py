from claude_notebook.redact import Redactor, parse


def test_parse_labels_and_longest_first():
    rules = parse("# clients\nAcme\nJane Roe = [Client X lead]\n\nRoe\n")
    assert rules[0] == ("Jane Roe", "[Client X lead]")
    assert dict(rules) == {"Jane Roe": "[Client X lead]", "Acme": "[Client A]", "Roe": "[Client B]"}


def test_redacts_whole_words_case_insensitively_including_filenames(tmp_path):
    f = tmp_path / "redact.txt"
    f.write_text("Acme\nJane Roe = [Client X lead]\nRoe\n", encoding="utf-8")
    r = Redactor(f)
    assert r("Built the ACME portal for Jane Roe; Roe signed off.") == \
        "Built the [Client A] portal for [Client X lead]; [Client B] signed off."
    assert r("Acme-01-Filing.pdf · acme_summary.md") == "[Client A]-01-Filing.pdf · [Client A]_summary.md"
    assert r("Acmeville and Roebuck stay") == "Acmeville and Roebuck stay"


def test_no_file_means_no_redaction_and_edits_reload(tmp_path):
    f = tmp_path / "redact.txt"
    r = Redactor(f)
    assert r("Acme") == "Acme" and r.count() == 0
    f.write_text("Acme\n", encoding="utf-8")
    assert r("Acme") == "[Client A]" and r.count() == 1
