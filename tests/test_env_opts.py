#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pytest
from src import boot


@pytest.fixture(autouse=True)
def env_cleanup():
    """
    Clean up the environment variables before each test.
    """
    boot.init_opts()
    env_backup = os.environ.copy()
    os.environ.clear()
    os.environ['UNKNOWN'] = 'unknown_value'
    os.environ['ANOTHER_UNKNOWN'] = 'something'

    yield

    os.environ.clear()
    os.environ.update(env_backup)


def test_env_empty():
    """
    Test environment variables in the empty case.
    """
    options = boot.load_from_env()
    assert isinstance(options, dict) and not options


@pytest.mark.parametrize(
    'name, env_tag',
    [
        ('port', 'PORT'),
        ('max_username', 'MAX_USERNAME'),
        ('max_chat_message', 'MAX_CHAT_MESSAGE'),
    ],
)
def test_env_single_int(name: str, env_tag: str):
    """
    Test environment variables for single integer option.
    """
    os.environ[env_tag] = '0'
    assert boot.load_from_env() == {name: 0}

    os.environ[env_tag] = '42'
    assert boot.load_from_env() == {name: 42}


@pytest.mark.parametrize(
    'name, env_tag',
    [
        ('config', 'CONFIG'),
        ('password', 'PASSWORD'),
        ('motd', 'MOTD'),
        ('salt', 'SALT'),
        ('listen_ipv4', 'LISTEN_IPV4'),
        ('listen_ipv6', 'LISTEN_IPV6'),
    ],
)
def test_env_single_str(name: str, env_tag: str):
    """
    Test environment variables for single string option.
    """
    os.environ[env_tag] = ''
    assert boot.load_from_env() == {name: ''}

    os.environ[env_tag] = 'TeSt \n0123456789\t'
    assert boot.load_from_env() == {name: 'TeSt \n0123456789\t'}


@pytest.mark.parametrize(
    'name, env_tag',
    [
        ('random_salt', 'RANDOM_SALT'),
        ('isolate_rooms', 'ISOLATE_ROOMS'),
        ('disable_chat', 'DISABLE_CHAT'),
        ('disable_ready', 'DISABLE_READY'),
        ('enable_stats', 'ENABLE_STATS'),
        ('enable_tls', 'ENABLE_TLS'),
        ('persistent', 'PERSISTENT'),
    ],
)
def test_env_single_bool(name: str, env_tag: str):
    """
    Test environment variables for single boolean option.
    """
    for val in ['TRUE', 'TrUe', 'true', 'ON', 'on']:  # TODO: allow `1`
        os.environ[env_tag] = val
        assert boot.load_from_env() == {name: True}

    for val in ['FALSE', 'FaLsE', 'false', 'OFF', 'off', '0']:
        os.environ[env_tag] = val
        assert boot.load_from_env() == {name: False}


def test_env_full():
    """
    Test all environment variable options.
    """
    env_data = {
        'CONFIG': 'config.yml',
        'PORT': '8999',
        'PASSWORD': 'PASSWD',
        'MOTD': 'MESSAGE',
        'SALT': 'SALT',
        'RANDOM_SALT': 'OFF',
        'ISOLATE_ROOMS': 'ON',
        'DISABLE_CHAT': 'OFF',
        'DISABLE_READY': 'ON',
        'ENABLE_STATS': 'OFF',
        'ENABLE_TLS': 'ON',
        'PERSISTENT': 'OFF',
        'MAX_USERNAME': '120',
        'MAX_CHAT_MESSAGE': '240',
        'LISTEN_IPV4': '127.0.0.1',
        'LISTEN_IPV6': '::1',
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
    os.environ.update(env_data)
    assert boot.load_from_env() == excepted_opts
