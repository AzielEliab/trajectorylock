from trajectorylock.doctor import format_plain, run_doctor


def test_doctor_passes(capsys) -> None:
    assert run_doctor(as_json=True) == 0
    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["certified_instrument"] is False
    plain = payload["plain"]
    assert "not a certified forensic instrument" in plain.lower()
    assert "shooter" in plain.lower()
    assert "intent" in plain.lower()
    assert "guilt" in plain.lower()
    assert "Aziel Eliab" in plain


def test_format_plain_refuses_overclaim() -> None:
    text = format_plain({"ok": True, "checks": [{"name": "guardrail", "ok": True, "detail": "refuses overclaim"}]})
    assert "research prototype" in text.lower()
    assert "not a certified forensic instrument" in text.lower()
    assert "shooter" in text.lower()
