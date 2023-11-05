#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import argparse
from typing import Any
from syncplay import ep_server

WorkDir = '/data/'
CertDir = '/certs/'
ConfigFile = 'config.yml'


def debug(msg: str) -> None:
    """ Print out debug information. """
    if 'DEBUG' in os.environ and os.environ['DEBUG'] in ['ON', 'TRUE']:
        print(f'\033[90m{msg}\033[0m', file=sys.stderr)


def temp_file(file: str, content: str) -> str:
    """ Create and save content to temporary files. """
    file = os.path.join('/tmp/', file)
    with open(file, 'w') as fp:
        fp.write(content)
    return file


def load_args() -> dict[str, Any]:
    """ Loading arguments from the command line. """
    parser = argparse.ArgumentParser(description='Syncplay Docker Bootstrap')
    parser.add_argument('-p', '--port', type=int, help='listen port of syncplay server')
    parser.add_argument('--password', type=str, help='authentication of syncplay server')
    parser.add_argument('--motd', type=str, help='welcome text after the user enters the room')
    parser.add_argument('--salt', type=str, help='string used to secure passwords')
    parser.add_argument('--random-salt', action='store_true', help='use a randomly generated salt value')
    parser.add_argument('--isolate-rooms', action='store_true', help='room isolation enabled')
    parser.add_argument('--disable-chat', action='store_true', help='disables the chat feature')
    parser.add_argument('--disable-ready', action='store_true', help='disables the readiness indicator feature')
    parser.add_argument('--enable-stats', action='store_true', help='enable syncplay server statistics')
    parser.add_argument('--enable-tls', action='store_true', help='enable tls support of syncplay server')
    parser.add_argument('--persistent', action='store_true', help='enables room persistence')
    parser.add_argument('--max-username', type=int, help='maximum length of usernames')
    parser.add_argument('--max-chat-message', type=int, help='maximum length of chat messages')
    parser.add_argument('--permanent-rooms', type=str, nargs='*', help='permanent rooms of syncplay server')
    args = parser.parse_args()
    debug(f'Command line arguments -> {args}')
    return {k.replace('_', '-'): v for k, v in vars(args).items()}


def load_config(args: dict[str, Any], file: str) -> dict[str, Any]:
    """ Complete uninitialized arguments from configure file. """
    if not os.path.exists(file):
        return args
    config = yaml.safe_load(open(file).read())
    options = [
        'port', 'password', 'motd', 'salt', 'random-salt',
        'isolate-rooms', 'disable-chat', 'disable-ready',
        'enable-stats', 'enable-tls', 'persistent',
        'max-username', 'max-chat-message', 'permanent-rooms',
    ]
    override = {x: config[x] for x in options if not args[x] and x in config}
    debug(f'Configure file override -> {override}')
    return args | override


def build_args(opts: dict):
    """ Construct the startup arguments for syncplay server. """
    args = ['--port', str(opts.get('port', 8999))]
    if 'password' in opts:
        args += ['--password', opts['password']]
    if 'motd' in opts:
        args += ['--motd-file', temp_file('motd.data', opts['motd'])]

    salt = opts.get('salt', None if 'random-salt' in opts else '')
    if salt is not None:
        args += ['--salt', salt]  # using random salt without this option
    for opt in ['isolate-rooms', 'disable-chat', 'disable-ready']:
        if opt in opts:
            args.append(f'--{opt}')

    if 'enable-stats' in opts:
        args += ['--stats-db-file', os.path.join(WorkDir, 'stats.db')]
    if 'enable-tls' in opts:
        args += ['--tls', CertDir]
    if 'persistent' in opts:
        args += ['--rooms-db-file', os.path.join(WorkDir, 'rooms.db')]

    if 'max-username' in opts:
        args += ['--max-username-length', str(opts['max-username'])]
    if 'max-chat-message' in opts:
        args += ['--max-chat-message-length', str(opts['max-chat-message'])]
    if 'permanent-rooms' in opts:
        rooms = '\n'.join(opts['permanent-rooms'])
        args += ['--permanent-rooms-file', temp_file('rooms.list', rooms)]
    return args


if __name__ == '__main__':
    origin_args = load_config(load_args(), os.path.join(WorkDir, ConfigFile))
    origin_args = {k: v for k, v in origin_args.items() if v is not None and v is not False}  # remove invalid items
    debug(f'Parsed arguments -> {origin_args}')
    syncplay_args = build_args(origin_args)
    debug(f'Syncplay startup arguments -> {syncplay_args}')
    sys.argv = ['syncplay'] + syncplay_args
    sys.exit(ep_server.main())
