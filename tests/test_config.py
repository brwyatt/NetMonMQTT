import pytest

from netmonmqtt.config import CheckConfig


def test_CheckConfig_defaults():
    # All of these should reult in the same data
    no_defaults = CheckConfig(
        check_type = "ping",
        name = "test",
        args = ["123.123.123.123"],
        kwargs = {"timeout": 2, "count": 3},
        interval = 10,
        jitter = 1,
        expire = 55,
    )
    only_defaults = CheckConfig(
        check_type = "ping",
        name = "test",
        defaults = {
            "args": ["123.123.123.123"],
            "kwargs": {
                "timeout": 2,
                "count": 3,
            },
            "interval": 10,
            "jitter": 1,
            "expire": 55,
        }
    )
    defaults_with_overrides = CheckConfig(
        check_type = "ping",
        name = "test",
        args = ["123.123.123.123"],
        kwargs = {"timeout": 2,},
        interval = 10,
        defaults = {
            "args": ["13.123.13.123"],
            "kwargs": {
                "timeout": 1,
                "count": 3,
            },
            "interval": 15,
            "jitter": 1,
            "expire": 55,
        }
    )

    assert only_defaults.args == no_defaults.args
    assert only_defaults.kwargs == no_defaults.kwargs
    assert only_defaults.interval == no_defaults.interval
    assert only_defaults.jitter == no_defaults.jitter
    assert only_defaults.expire == no_defaults.expire

    assert defaults_with_overrides.args == no_defaults.args
    assert defaults_with_overrides.kwargs == no_defaults.kwargs
    assert defaults_with_overrides.interval == no_defaults.interval
    assert defaults_with_overrides.jitter == no_defaults.jitter
    assert defaults_with_overrides.expire == no_defaults.expire
