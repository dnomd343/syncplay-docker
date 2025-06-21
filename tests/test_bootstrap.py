#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pytest
from unittest.mock import patch
import src.syncplay_boot.boot as boot


@pytest.fixture(autouse=True)
def init_opts():
    boot.init_opts()
    yield


@patch('syncplay.ep_server.main')
@patch('src.syncplay_boot.boot.sp_convert')
@patch('src.syncplay_boot.boot.load_opts')
@patch('src.syncplay_boot.boot.init_opts')
def test_bootstrap_with_opts(mock_init_opts, mock_load_opts, mock_sp_convert, mock_ep_server) -> None:
    mock_ep_server.return_value = 0
    mock_sp_convert.return_value = ['--port', '12345']

    with pytest.raises(SystemExit) as exec_info:
        boot.bootstrap({'port': 12345})
    assert exec_info.value.code == 0
    assert sys.argv == ['syncplay', '--port', '12345']

    mock_init_opts.assert_not_called()
    mock_load_opts.assert_not_called()
    mock_ep_server.assert_called_once()
    mock_sp_convert.assert_called_once_with({'port': 12345})


@patch('syncplay.ep_server.main')
@patch('src.syncplay_boot.boot.sp_convert')
@patch('src.syncplay_boot.boot.load_opts')
@patch('src.syncplay_boot.boot.init_opts')
def test_bootstrap_without_opts(mock_init_opts, mock_load_opts, mock_sp_convert, mock_ep_server) -> None:
    mock_ep_server.return_value = 0
    mock_load_opts.return_value = {'port': 12345}
    mock_sp_convert.return_value = ['--port', '12345']

    with pytest.raises(SystemExit) as exec_info:
        boot.bootstrap()
    assert exec_info.value.code == 0
    assert sys.argv == ['syncplay', '--port', '12345']

    mock_init_opts.assert_called_once()
    mock_load_opts.assert_called_once()
    mock_ep_server.assert_called_once()
    mock_sp_convert.assert_called_once_with({'port': 12345})
