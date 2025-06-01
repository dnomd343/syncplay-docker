#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from types import GenericAlias
from typing import NotRequired
import syncplay_boot.boot as boot


def test_options():
    """
    Verify types and structure of SyncplayOptions and DESC.
    """
    assert len(boot.SyncplayOptions.__annotations__) == len(boot.DESC)
    assert set(boot.SyncplayOptions.__annotations__) == set(boot.DESC)

    for tag, desc in boot.DESC.values():
        assert tag is None or type(tag) is str
        assert type(desc) is str

    for field in boot.SyncplayOptions.__annotations__.values():
        assert field.__origin__ is NotRequired
        assert len(field.__args__) == 1

        if type(field_t := field.__args__[0]) is GenericAlias:
            assert field_t.__origin__ is list
            assert len(field_t.__args__) == 1
            field_t = field_t.__args__[0]

        assert field_t in (int, str, bool)


def verify_env_opts():
    """
    Verify the ENV_OPTS with expected environment variable options.
    """
    expected_opts = {
        'config': str,  # only non-list options
        'port': int,
        'password': str,
        'motd': str,
        'salt': str,
        'random_salt': bool,
        'isolate_rooms': bool,
        'disable_chat': bool,
        'disable_ready': bool,
        'enable_stats': bool,
        'enable_tls': bool,
        'persistent': bool,
        'max_username': int,
        'max_chat_message': int,
        'listen_ipv4': str,
        'listen_ipv6': str,
    }
    assert boot.ENV_OPTS == expected_opts


def verify_cfg_opts():
    """
    Verify the CFG_OPTS with expected configure file options.
    """
    expected_opts = {
        'config': (str, False),  # (type, is_list)
        'port': (int, False),
        'password': (str, False),
        'motd': (str, False),
        'salt': (str, False),
        'random_salt': (bool, False),
        'isolate_rooms': (bool, False),
        'disable_chat': (bool, False),
        'disable_ready': (bool, False),
        'enable_stats': (bool, False),
        'enable_tls': (bool, False),
        'persistent': (bool, False),
        'max_username': (int, False),
        'max_chat_message': (int, False),
        'permanent_rooms': (str, True),
        'listen_ipv4': (str, False),
        'listen_ipv6': (str, False),
    }
    assert boot.CFG_OPTS == expected_opts


def verify_arg_opts():
    """
    Verify the ARG_OPTS with expected command line options.
    """
    expected_opts = {
        'config': {'type': str, 'metavar': 'FILE'},  # argparse options
        'port': {'type': int, 'metavar': 'PORT'},
        'password': {'type': str, 'metavar': 'PASSWD'},
        'motd': {'type': str, 'metavar': 'MESSAGE'},
        'salt': {'type': str, 'metavar': 'TEXT'},
        'random_salt': {'action': 'store_true'},
        'isolate_rooms': {'action': 'store_true'},
        'disable_chat': {'action': 'store_true'},
        'disable_ready': {'action': 'store_true'},
        'enable_stats': {'action': 'store_true'},
        'enable_tls': {'action': 'store_true'},
        'persistent': {'action': 'store_true'},
        'max_username': {'type': int, 'metavar': 'NUM'},
        'max_chat_message': {'type': int, 'metavar': 'NUM'},
        'permanent_rooms': {'type': str, 'metavar': 'ROOM', 'nargs': '*'},
        'listen_ipv4': {'type': str, 'metavar': 'ADDR'},
        'listen_ipv6': {'type': str, 'metavar': 'ADDR'},
    }
    for tag, opts in expected_opts.items():
        _, opts['help'] = boot.DESC[tag]  # help message from DESC

    assert boot.ARG_OPTS == expected_opts


def test_init_opts():
    """
    Test initialization and idempotency of the init_opts function.
    """
    boot.ARG_OPTS.clear()
    boot.ENV_OPTS.clear()
    boot.CFG_OPTS.clear()

    for _ in range(2):
        boot.init_opts()  # run twice to verify idempotency
        verify_arg_opts()
        verify_env_opts()
        verify_cfg_opts()
