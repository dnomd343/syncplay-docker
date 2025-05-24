#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import src.boot as boot
from unittest.mock import patch


@pytest.fixture(autouse=True)
def init_opts():
    boot.init_opts()
    yield


@patch('src.boot.load_from_config')
@patch('src.boot.load_from_args')
@patch('src.boot.load_from_env')
def test_config_priority(mock_env, mock_arg, mock_cfg) -> None:
    """
    Test configure file loading priority order.
    """
    mock_env.return_value = {}
    mock_arg.return_value = {}
    boot.load_opts()
    mock_cfg.assert_called_with('config.yml')  # default value

    mock_env.return_value = {'config': 'env_config.yml'}
    mock_arg.return_value = {}
    boot.load_opts()
    mock_cfg.assert_called_with('env_config.yml')  # select from env

    mock_env.return_value = {'config': 'env_config.yml'}
    mock_arg.return_value = {'config': 'arg_config.yml'}
    boot.load_opts()
    mock_cfg.assert_called_with('arg_config.yml')  # higher priority than env


@patch('src.boot.load_from_config')
@patch('src.boot.load_from_args')
@patch('src.boot.load_from_env')
def test_merge_priority(mock_env, mock_arg, mock_cfg) -> None:
    """
    Test the merge priority order among env, cli and config options.
    """
    low_opts = {
        'config': 'LOW',
        'motd': 'LOW',
        'port': 12345,
        'max_username': 12345,
        'persistent': False,
        'enable_tls': True,
        'permanent_rooms': ['LOW_1', 'LOW_2'],
    }
    high_opts = {
        'config': 'HIGH',
        'salt': 'HIGH',
        'port': 23456,
        'max_chat_message': 23456,
        'persistent': True,
        'enable_stats': True,
        'permanent_rooms': ['HIGH_1', 'HIGH_2'],
    }
    expected_opts = {
        'config': 'HIGH',
        'motd': 'LOW',
        'salt': 'HIGH',
        'port': 23456,
        'max_username': 12345,
        'max_chat_message': 23456,
        'persistent': True,
        'enable_tls': True,
        'enable_stats': True,
        'permanent_rooms': ['HIGH_1', 'HIGH_2'],
    }

    mock_env.return_value = low_opts
    mock_cfg.return_value = high_opts
    mock_arg.return_value = {}
    assert boot.load_opts() == expected_opts  # env < cfg

    mock_env.return_value = low_opts
    mock_cfg.return_value = {}
    mock_arg.return_value = high_opts
    assert boot.load_opts() == expected_opts  # env < arg

    mock_env.return_value = {}
    mock_cfg.return_value = low_opts
    mock_arg.return_value = high_opts
    assert boot.load_opts() == expected_opts  # cfg < arg


@patch('src.boot.load_from_config')
@patch('src.boot.load_from_args')
@patch('src.boot.load_from_env')
def test_bool_options(mock_env, mock_arg, mock_cfg) -> None:
    """
    Test bool options handling and non-bool retention.
    """
    mock_env.return_value = {}
    mock_cfg.return_value = {}

    bool_opts = [
        'random_salt',
        'isolate_rooms',
        'disable_chat',
        'disable_ready',
        'enable_stats',
        'enable_tls',
        'persistent',
    ]
    mock_arg.return_value = {x: True for x in bool_opts}
    assert boot.load_opts() == mock_arg.return_value  # bool options kept on True

    mock_arg.return_value = {x: False for x in bool_opts}
    assert boot.load_opts() == {}  # bool options ignored on False

    mock_arg.return_value = {'port': 0, 'salt': '', 'permanent_rooms': []}
    assert boot.load_opts() == mock_arg.return_value  # non-bool options should be kept
