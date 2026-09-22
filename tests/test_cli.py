import sys
from pathlib import Path

import pytest

from tender_scout.cli import main


def _write_config(tmp_path: Path) -> Path:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        'cpv_codes: ["71351000"]\n'
        'company_profile: "we survey things"\n'
    )
    return config_file


def _arrange_failing_run(tmp_path: Path, monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise RuntimeError("mark_seen exploded")

    config_file = _write_config(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("tender_scout.cli.run", boom)
    monkeypatch.setattr(sys, "argv", ["tender-scout", "--config",
str(config_file)])


def test_exits_1_when_the_run_fails(tmp_path: Path, monkeypatch) -> None:
    _arrange_failing_run(tmp_path, monkeypatch)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1


def test_prints_a_traceback_when_the_run_fails(tmp_path: Path,
monkeypatch, capsys) -> None:
    _arrange_failing_run(tmp_path, monkeypatch)

    with pytest.raises(SystemExit):
        main()

    assert "Traceback" in capsys.readouterr().err