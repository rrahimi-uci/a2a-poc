"""Tests for the configuration defaults."""

import allure

import config


@allure.feature("Configuration")
@allure.story("Defaults")
@allure.title("Default ports and protocol parameters are exposed")
def test_config_defaults():
    assert config.DEFAULT_MATH_AGENT_PORT == 8001
    assert config.DEFAULT_DATA_AGENT_PORT == 8002
    assert config.DEFAULT_TIMEOUT == 30
    assert config.DEFAULT_MAX_RETRIES == 3
