#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pytest
from src import boot


@pytest.fixture(autouse=True)
def argv_cleanup():
    """
    Clean up the command line arguments before each test.
    """
    boot.init_opts()
    argv_backup = sys.argv
    sys.argv = ['syncplay']
    yield
    sys.argv = argv_backup


def test_args_empty():
    """
    Test command line arguments in the empty case.
    """
    options = boot.load_from_args()
    assert isinstance(options, dict) and not options


@pytest.mark.parametrize(
    'name, arg_tag',
    [
        ('port', '--port'),
        ('max_username', '--max-username'),
        ('max_chat_message', '--max-chat-message'),
    ],
)
def test_args_single_int(name: str, arg_tag: str):
    """
    Test command line arguments of single integer option.
    """
    sys.argv += [arg_tag, '0']
    assert boot.load_from_args() == {name: 0}

    sys.argv += [arg_tag, '42']
    assert boot.load_from_args() == {name: 42}


@pytest.mark.parametrize(
    'name, arg_tag',
    [
        ('config', '--config'),
        ('password', '--password'),
        ('motd', '--motd'),
        ('salt', '--salt'),
        ('listen_ipv4', '--listen-ipv4'),
        ('listen_ipv6', '--listen-ipv6'),
    ],
)
def test_args_single_str(name: str, arg_tag: str):
    """
    Test command line arguments of single string option.
    """
    sys.argv += [arg_tag, '']
    assert boot.load_from_args() == {name: ''}

    sys.argv += [arg_tag, 'TeSt \n0123456789\t']
    assert boot.load_from_args() == {name: 'TeSt \n0123456789\t'}


@pytest.mark.parametrize(
    'name, arg_tag',
    [
        ('random_salt', '--random-salt'),
        ('isolate_rooms', '--isolate-rooms'),
        ('disable_chat', '--disable-chat'),
        ('disable_ready', '--disable-ready'),
        ('enable_stats', '--enable-stats'),
        ('enable_tls', '--enable-tls'),
        ('persistent', '--persistent'),
    ],
)
def test_args_single_bool(name: str, arg_tag: str):
    """
    Test command line arguments of single boolean option.
    """
    sys.argv += [arg_tag]
    assert boot.load_from_args() == {name: True}


def test_args_full():
    """
    Test all command line arguments options.
    """
    # fmt: off
    sys.argv += [
        '--config', 'config.yml',
        '--port', '8999',
        '--password', 'PASSWD',
        '--motd', 'MESSAGE',
        '--salt', 'SALT',
        '--random-salt',
        '--isolate-rooms',
        '--disable-chat',
        '--disable-ready',
        '--enable-stats',
        '--enable-tls',
        '--persistent',
        '--max-username', '120',
        '--max-chat-message', '240',
        '--listen-ipv4', '127.0.0.1',
        '--listen-ipv6', '::1',
    ]  # fmt: on
    excepted_opts = {
        'config': 'config.yml',
        'port': 8999,
        'password': 'PASSWD',
        'motd': 'MESSAGE',
        'salt': 'SALT',
        'random_salt': True,
        'isolate_rooms': True,
        'disable_chat': True,
        'disable_ready': True,
        'enable_stats': True,
        'enable_tls': True,
        'persistent': True,
        'max_username': 120,
        'max_chat_message': 240,
        'listen_ipv4': '127.0.0.1',
        'listen_ipv6': '::1',
    }
    assert boot.load_from_args() == excepted_opts
