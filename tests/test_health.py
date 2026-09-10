from project_zysec import app_name


def test_app_name() -> None:
    assert app_name() == "ZySec AI"
