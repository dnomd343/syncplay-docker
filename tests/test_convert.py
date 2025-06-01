#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pytest
import tempfile
from typing import Callable
import syncplay_boot.boot as boot
from unittest.mock import patch, mock_open


@pytest.fixture(autouse=True)
def init_opts():
    boot.init_opts()
    yield


@pytest.fixture
def temp_dir_setup():
    env_backup = os.environ.copy()
    os.environ['CERT_DIR'] = (cert_dir := tempfile.mkdtemp())
    os.environ['TEMP_DIR'] = (temp_dir := tempfile.mkdtemp())
    os.environ['WORK_DIR'] = (work_dir := tempfile.mkdtemp())

    yield cert_dir, temp_dir, work_dir

    os.environ.clear()
    os.environ.update(env_backup)


def convert_builder(keep_port: bool = False, keep_salt: bool = False) -> Callable[[boot.SyncplayOptions], list[str]]:
    def convert(opts: boot.SyncplayOptions) -> list[str]:
        output = boot.sp_convert(opts)

        if not keep_port:
            if '--port' in output and '8999' in output:
                if (index := output.index('--port')) + 1 == output.index('8999'):
                    output = output[:index] + output[index + 2 :]

        if not keep_salt:
            if '--salt' in output and '' in output:
                if (index := output.index('--salt')) + 1 == output.index(''):
                    output = output[:index] + output[index + 2 :]

        return output

    return convert


def test_port() -> None:
    """
    Test port field of options conversion.
    """
    convert = convert_builder(keep_port=True)
    assert convert({}) == ['--port', '8999']  # default port
    assert convert({'port': 12345}) == ['--port', '12345']  # custom port


def test_password() -> None:
    """
    Test password field of options conversion.
    """
    convert = convert_builder()
    assert convert({}) == []
    assert convert({'password': 'PWD'}) == ['--password', 'PWD']  # custom password


@patch('syncplay_boot.boot.open', new_callable=mock_open)
def test_motd(mock_file) -> None:
    """
    Test motd field of options conversion.
    """
    convert = convert_builder()
    assert convert({}) == []
    assert convert({'motd': 'MSG'}) == ['--motd-file', '/tmp/motd.data']
    mock_file.assert_called_with('/tmp/motd.data', 'w', encoding='utf-8')
    mock_file().write.assert_called_with('MSG')


def test_salt_handling() -> None:
    """
    Test salt related handling of options conversion.
    """
    convert = convert_builder(keep_salt=True)
    assert convert({}) == ['--salt', '']
    assert convert({'salt': ''}) == ['--salt', '']
    assert convert({'salt': 'SALT'}) == ['--salt', 'SALT']

    assert convert({'random_salt': True}) == []
    assert convert({'salt': '', 'random_salt': True}) == ['--salt', '']
    assert convert({'salt': 'SALT', 'random_salt': True}) == ['--salt', 'SALT']


def test_boolean_flags() -> None:
    """
    Test boolean flags handling of options conversion.
    """
    convert = convert_builder()
    assert convert({'isolate_rooms': True}) == ['--isolate-rooms']
    assert convert({'disable_chat': True}) == ['--disable-chat']
    assert convert({'disable_ready': True}) == ['--disable-ready']

    assert convert({'enable_stats': True}) == ['--stats-db-file', '/data/stats.db']
    assert convert({'enable_tls': True}) == ['--tls', '/certs/']
    assert convert({'persistent': True}) == ['--rooms-db-file', '/data/rooms.db']


def test_limited_values() -> None:
    """
    Test limited values handling of options conversion.
    """
    convert = convert_builder()
    assert convert({'max_username': 20}) == ['--max-username-length', '20']
    assert convert({'max_chat_message': 500}) == ['--max-chat-message-length', '500']


@patch('syncplay_boot.boot.open', new_callable=mock_open)
def test_permanent_rooms(mock_file) -> None:
    """
    Test permanent rooms field of options conversion.
    """
    convert = convert_builder()
    assert convert({'permanent_rooms': ['R1', 'R2', 'R3']}) == ['--permanent-rooms-file', '/tmp/rooms.list']
    mock_file.assert_called_with('/tmp/rooms.list', 'w', encoding='utf-8')
    mock_file().write.assert_called_with('R1\nR2\nR3')


def test_ip_configure() -> None:
    """
    Test IP configure handling of options conversion.
    """
    convert = convert_builder()
    assert convert({}) == []
    assert convert({'listen_ipv4': '0.0.0.0'}) == ['--ipv4-only', '--interface-ipv4', '0.0.0.0']
    assert convert({'listen_ipv6': 'fc00::1'}) == ['--ipv6-only', '--interface-ipv6', 'fc00::1']
    # fmt: off
    assert convert({'listen_ipv4': '0.0.0.0', 'listen_ipv6': 'fc00::1'}) == [
        '--interface-ipv4', '0.0.0.0',
        '--interface-ipv6', 'fc00::1',
    ]  # fmt: on


def test_path_env(temp_dir_setup) -> None:
    """
    Test path env variables of options conversion.
    """
    convert = convert_builder()
    cert_dir, temp_dir, work_dir = temp_dir_setup

    assert convert({'enable_tls': True}) == ['--tls', cert_dir]  # tls using CERT_DIR

    path = os.path.join(temp_dir, 'motd.data')  # motd using TEMP_DIR
    assert convert({'motd': 'MESSAGE'}) == ['--motd-file', path]

    path = os.path.join(work_dir, 'stats.db')  # stats-db using WORK_DIR
    assert convert({'enable_stats': True}) == ['--stats-db-file', path]


def test_full_options() -> None:
    """
    Test full options conversion.
    """
    convert = convert_builder(keep_port=True, keep_salt=True)
    opts: boot.SyncplayOptions = {
        'port': 12345,
        'password': 'secret',
        'motd': 'Welcome to Syncplay',
        'salt': 'mysalt',
        'random_salt': True,
        'isolate_rooms': True,
        'disable_chat': True,
        'disable_ready': True,
        'enable_stats': True,
        'enable_tls': True,
        'persistent': True,
        'max_username': 20,
        'max_chat_message': 500,
        'permanent_rooms': ['room1', 'room2', 'room3'],
        'listen_ipv4': '0.0.0.0',
        'listen_ipv6': '::',
    }
    # fmt: off
    expected = [
        '--port', '12345',
        '--password', 'secret',
        '--motd-file', '/tmp/motd.data',
        '--salt', 'mysalt',
        '--isolate-rooms',
        '--disable-chat',
        '--disable-ready',
        '--stats-db-file', '/data/stats.db',
        '--tls', '/certs/',
        '--rooms-db-file', '/data/rooms.db',
        '--max-username-length', '20',
        '--max-chat-message-length', '500',
        '--permanent-rooms-file', '/tmp/rooms.list',
        '--interface-ipv4', '0.0.0.0',
        '--interface-ipv6', '::'
    ]  # fmt: on

    assert convert(opts) == expected
