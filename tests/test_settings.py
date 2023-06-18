from dynaconf.vendor.tomllib import TOMLDecodeError
from pytest import raises
from platyrhynchos.commons.settings import load_settings_from_string

def test_load_settings_from_string_with_valid_input():
    settings_text = """
    [DEFAULT]
    debug = true
    """
    settings = load_settings_from_string(settings_text)
    assert settings['DEFAULT'].debug == True

def test_load_settings_from_string_with_invalid_input():
    settings_text = """
    [DEFA
    """
    with raises(TOMLDecodeError):
        load_settings_from_string(settings_text)

def test_load_settings_from_string_1():
    settings_text = """
    [DEFAULT]
    debug = true
    db_name = "test_db"
    db_host = "localhost"
    db_port = 5432
    """
    settings = load_settings_from_string(settings_text)["DEFAULT"]
    assert settings.debug == True
    assert settings.db_name == "test_db"
    assert settings.db_host == "localhost"
    assert settings.db_port == 5432

def test_load_settings_from_string_2():
    settings_text = """
    [DEFAULT]
    debug = false
    db_name = "prod_db"
    db_host = "example.com"
    db_port = 5433
    """
    settings = load_settings_from_string(settings_text)["DEFAULT"]
    assert settings.debug == False
    assert settings.db_name == "prod_db"
    assert settings.db_host == "example.com"
    assert settings.db_port == 5433