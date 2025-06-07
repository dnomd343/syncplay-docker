#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import toml
import yaml
import pytest
import tempfile
import syncplay_boot.boot as boot


@pytest.fixture(autouse=True)
def config_init():
    boot.init_opts()
    yield


def verify_config(data: dict, excepted: dict) -> None:
    """
    Verify configure loading from different sequence formats.
    """
    data |= {
        'unknown': 'unknown_value',
        'another_unknown': 'another_unknown_value',
    }
    files = {
        '.json': json.dumps(data),
        '.toml': toml.dumps(data),
        '.yaml': (tmp := yaml.dump(data)),
        '.unknown': tmp,  # YAML format in default
    }
    for suffix, content in files.items():
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix) as fp:
            fp.write(content)
            fp.flush()
            assert boot.load_from_config(fp.name) == excepted


def test_config_empty() -> None:
    """
    Test configuration file in the empty case.
    """
    verify_config({}, {})


@pytest.mark.parametrize(
    'name, cfg_tag',
    [
        ('port', 'port'),
        ('max_username', 'max-username'),
        ('max_chat_message', 'max-chat-message'),
    ],
)
def test_config_single_int(name: str, cfg_tag: str) -> None:
    """
    Test configuration file of single integer option.
    """
    verify_config({cfg_tag: 0}, {name: 0})
    verify_config({cfg_tag: 42}, {name: 42})


@pytest.mark.parametrize(
    'name, cfg_tag',
    [
        ('config', 'config'),
        ('password', 'password'),
        ('motd', 'motd'),
        ('salt', 'salt'),
        ('listen_ipv4', 'listen-ipv4'),
        ('listen_ipv6', 'listen-ipv6'),
    ],
)
def test_config_single_str(name: str, cfg_tag: str) -> None:
    """
    Test configuration file of single string option.
    """
    verify_config({cfg_tag: ''}, {name: ''})
    verify_config({cfg_tag: 'TeSt \n0123456789\t'}, {name: 'TeSt \n0123456789\t'})


@pytest.mark.parametrize(
    'name, cfg_tag',
    [
        ('random_salt', 'random-salt'),
        ('isolate_rooms', 'isolate-rooms'),
        ('disable_chat', 'disable-chat'),
        ('disable_ready', 'disable-ready'),
        ('enable_stats', 'enable-stats'),
        ('enable_tls', 'enable-tls'),
        ('persistent', 'persistent'),
    ],
)
def test_config_single_bool(name: str, cfg_tag: str) -> None:
    """
    Test configuration file of single boolean option.
    """
    verify_config({cfg_tag: True}, {name: True})
    verify_config({cfg_tag: False}, {name: False})


@pytest.mark.parametrize(
    'name, cfg_tag',
    [
        ('permanent_rooms', 'permanent-rooms'),
    ],
)
def test_config_str_list(name: str, cfg_tag: str) -> None:
    """
    Test configuration file of string list option.
    """
    verify_config({cfg_tag: []}, {name: []})
    verify_config({cfg_tag: ['VALUE']}, {name: ['VALUE']})
    verify_config({cfg_tag: ['V1', 'V2', 'V3']}, {name: ['V1', 'V2', 'V3']})


def test_config_full():
    """
    Test all configuration file options.
    """
    cfg_data = {
        'config': 'config.yml',
        'port': 8999,
        'password': 'PASSWD',
        'motd': 'MESSAGE',
        'salt': 'SALT',
        'random-salt': False,
        'isolate-rooms': True,
        'disable-chat': False,
        'disable-ready': True,
        'enable-stats': False,
        'enable-tls': True,
        'persistent': False,
        'max-username': 120,
        'max-chat-message': 240,
        'listen-ipv4': '127.0.0.1',
        'listen-ipv6': '::1',
    }
    excepted_opts = {
        'config': 'config.yml',
        'port': 8999,
        'password': 'PASSWD',
        'motd': 'MESSAGE',
        'salt': 'SALT',
        'random_salt': False,
        'isolate_rooms': True,
        'disable_chat': False,
        'disable_ready': True,
        'enable_stats': False,
        'enable_tls': True,
        'persistent': False,
        'max_username': 120,
        'max_chat_message': 240,
        'listen_ipv4': '127.0.0.1',
        'listen_ipv6': '::1',
    }
    verify_config(cfg_data, excepted_opts)
