#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Syncplay Bootstrap using to convert redesigned parameter fields into arguments
that are non-intrusive to Syncplay Server. It supports command line arguments,
environment variables, JSON / YAML / TOML configuration input, and processes
them according to priority.

The command line parameters of Syncplay server are not convenient for container
startup, especially for scenarios that require specified file, which can easily
confuse people who use docker. Through this adapter, you will no longer need to
create files and specify paths, but directly configure it through the command
line or other methods.

Docs: https://syncplay.pl/guide/server/
      https://man.archlinux.org/man/extra/syncplay/syncplay-server.1

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Docker Arguments              ┃ Official Arguments                    ┃
┠───────────────────────────────╂───────────────────────────────────────┨
┃ --config [FILE]               ┃ /                                     ┃
┠───────────────────────────────╂───────────────────────────────────────┨
┃ --port [PORT]                 ┃ PASS-THROUGH                          ┃
┃ --password [PASSWD]           ┃                                       ┃
┃ --isolate-rooms               ┃                                       ┃
┃ --disable-chat                ┃                                       ┃
┃ --disable-ready               ┃                                       ┃
┠───────────────────────────────╂───────────────────────────────────────┨
┃ --motd [MESSAGE]              ┃ --motd-file [FILE]                    ┃
┃ --salt [TEXT] & --random-salt ┃ --salt [TEXT]                         ┃
┃ --enable-stats                ┃ --stats-db-file [FILE]                ┃
┃ --enable-tls                  ┃ --tls [PATH]                          ┃
┃ --persistent                  ┃ --rooms-db-file [FILE]                ┃
┃ --max-username [NUM]          ┃ --max-username-length [NUM]           ┃
┃ --max-chat-message [NUM]      ┃ --max-chat-message-length [NUM]       ┃
┃ --permanent-rooms [ROOM ...]  ┃ --permanent-rooms-file [FILE]         ┃
┃ --listen-ipv4 [ADDR]          ┃ --ipv4-only & --interface-ipv4 [ADDR] ┃
┃ --listen-ipv6 [ADDR]          ┃ --ipv6-only & --interface-ipv6 [ADDR] ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

import os
import sys
import json
import yaml
import tomllib
import argparse
import platform
import syncplay

from types import GenericAlias
from typing import Any, TypedDict, NotRequired


class SyncplayOptions(TypedDict):
    config: NotRequired[str]  # special option for loading
    port: NotRequired[int]
    password: NotRequired[str]
    motd: NotRequired[str]
    salt: NotRequired[str]
    random_salt: NotRequired[bool]  # bool options must be True when existed
    isolate_rooms: NotRequired[bool]
    disable_chat: NotRequired[bool]
    disable_ready: NotRequired[bool]
    enable_stats: NotRequired[bool]
    enable_tls: NotRequired[bool]
    persistent: NotRequired[bool]
    max_username: NotRequired[int]
    max_chat_message: NotRequired[int]
    permanent_rooms: NotRequired[list[str]]
    listen_ipv4: NotRequired[str]
    listen_ipv6: NotRequired[str]


DESC = {
    'config': ('FILE', 'configure file path'),
    'port': ('PORT', 'listen port of syncplay server'),
    'password': ('PASSWD', 'authentication of syncplay server'),
    'motd': ('MESSAGE', 'welcome text after the user enters the room'),
    'salt': ('TEXT', 'string used to secure passwords'),
    'random_salt': (None, 'use a randomly generated salt value'),
    'isolate_rooms': (None, 'room isolation enabled'),
    'disable_chat': (None, 'disables the chat feature'),
    'disable_ready': (None, 'disables the readiness indicator feature'),
    'enable_stats': (None, 'enable syncplay server statistics'),
    'enable_tls': (None, 'enable tls support of syncplay server'),
    'persistent': (None, 'enables room persistence'),
    'max_username': ('NUM', 'maximum length of usernames'),
    'max_chat_message': ('NUM', 'maximum length of chat messages'),
    'permanent_rooms': ('ROOM', 'permanent rooms of syncplay server'),
    'listen_ipv4': ('ADDR', 'listening address of ipv4'),
    'listen_ipv6': ('ADDR', 'listening address of ipv6'),
}

ARG_OPTS: dict[str, dict] = {}  # for loading cli arguments

ENV_OPTS: dict[str, type] = {}  # for loading env variables

CFG_OPTS: dict[str, tuple[type, bool]] = {}  # for loading configure file


def debug_msg(prefix: str, message: Any) -> None:
    """ Output debug message. """
    if os.environ.get('DEBUG', '').upper() in ['ON', 'TRUE']:
        print(f'\033[33m{prefix}\033[0m -> \033[90m{message}\033[0m', file=sys.stderr)


def init_opts() -> None:
    """ Build syncplay formatting options. """
    for name, field in SyncplayOptions.__annotations__.items():
        field_t, is_list = field.__args__[0], False
        if type(field_t) is GenericAlias:
            field_t, is_list = field_t.__args__[0], True  # list[T] -> T

        ENV_OPTS[name] = field_t
        CFG_OPTS[name] = (field_t, is_list)
        ARG_OPTS[name] = {'type': field_t, 'metavar': DESC[name][0], 'help': DESC[name][1]}

        if is_list:
            ENV_OPTS.pop(name)  # not supported in env
            ARG_OPTS[name]['nargs'] = '*'  # multiple values

        if field_t is bool:
            ARG_OPTS[name]['action'] = 'store_true'
            [ARG_OPTS[name].pop(x) for x in ('type', 'metavar')]

    debug_msg('ENV_OPTS', ENV_OPTS)
    debug_msg('CFG_OPTS', CFG_OPTS)
    debug_msg('ARG_OPTS', ARG_OPTS)


def load_from_env() -> SyncplayOptions:
    """ Load syncplay options from environment variables. """
    options: SyncplayOptions = {}
    for name, field_t in ENV_OPTS.items():
        if name.upper() in os.environ:
            value = os.environ[name.upper()]
            if field_t is str:
                options[name] = value
            elif field_t is int:
                options[name] = int(value)
            elif field_t is bool:
                options[name] = value.upper() in ['ON', 'TRUE']

    debug_msg('Environment variables', os.environ)
    return options


def load_from_args() -> SyncplayOptions:
    """ Load syncplay options from command line arguments. """

    def __version_msg() -> str:
        python_ver = f'{platform.python_implementation()} {platform.python_version()}'
        return (f'{parser.description} v{syncplay.version} '
                f'({syncplay.milestone} {syncplay.release_number}) '
                f'[{python_ver} {platform.machine()}]')

    def __build_args(opt: str) -> list[str]:
        match opt := opt.replace('_', '-'):
            case 'config': return ['-c', f'--{opt}']
            case 'port': return ['-p', f'--{opt}']
            case 'motd': return ['-m', f'--{opt}']
            case 'password': return ['-k', f'--{opt}']
            case _: return [f'--{opt}']

    parser = argparse.ArgumentParser(description='Syncplay Docker Bootstrap')
    parser.add_argument('-v', '--version', action='version', version=__version_msg())
    for name, opts in ARG_OPTS.items():
        parser.add_argument(*__build_args(name), **opts)

    args = parser.parse_args(sys.argv[1:])
    debug_msg('Command line arguments', args)

    options: SyncplayOptions = {}
    for arg, value in vars(args).items():
        if value is None or value is False:
            continue
        options[arg] = value
    return options


def load_from_config(path: str) -> SyncplayOptions:
    """ Load syncplay options from configure file. """

    def __load_file() -> dict[str, Any]:
        if not os.path.exists(path):
            return {}
        content = open(path).read()
        if path.endswith('.json'):
            return json.loads(content)
        elif path.endswith('.toml'):
            return tomllib.loads(content)
        else:
            return yaml.safe_load(content)  # assume YAML format

    assert type(config := __load_file()) is dict
    debug_msg('Configure content', config)

    options: SyncplayOptions = {}
    for key, (field_t, is_list) in CFG_OPTS.items():
        value = config.get(key.replace('_', '-'), None)
        if value is not None:
            if is_list:
                assert type(value) is list
                assert all(type(x) is field_t for x in value)
            else:
                assert type(value) is field_t
            options[key] = value
    return options


def load_opts() -> SyncplayOptions:
    """ Combine syncplay options from multiple source. """
    env_opts = load_from_env()
    cli_opts = load_from_args()
    cfg_opts = load_from_config((env_opts | cli_opts).get('config', 'config.yml'))

    debug_msg('Environment options', env_opts)
    debug_msg('Command line options', cli_opts)
    debug_msg('Configure file options', cfg_opts)

    final_opts: SyncplayOptions = {}
    for opt, value in (env_opts | cfg_opts | cli_opts).items():
        if type(value) is not bool or value:
            final_opts[opt] = value
    debug_msg('Bootstrap final options', final_opts)
    return final_opts


def sp_convert(opts: SyncplayOptions) -> list[str]:
    """ Construct the startup arguments for syncplay server. """

    def __temp_file(file: str, content: str) -> str:
        """ Create and save content to temporary files. """
        file = os.path.join(temp_dir, file)
        with open(file, 'w', encoding='utf-8') as fp:
            fp.write(content)
        return file

    temp_dir = os.environ.get('TEMP_DIR', '/tmp/')
    work_dir = os.environ.get('WORK_DIR', '/data/')
    cert_dir = os.environ.get('CERT_DIR', '/certs/')

    args = ['--port', f'{opts.get('port', 8999)}']
    if 'password' in opts:
        args += ['--password', opts['password']]
    if 'motd' in opts:
        args += ['--motd-file', __temp_file('motd.data', opts['motd'])]

    salt = opts.get('salt', None if 'random_salt' in opts else '')
    if salt is not None:
        args += ['--salt', salt]  # using random salt without this option
    for opt in ['isolate_rooms', 'disable_chat', 'disable_ready']:
        if opt in opts:
            args.append(f'--{opt}'.replace('_', '-'))

    if 'enable_stats' in opts:
        args += ['--stats-db-file', os.path.join(work_dir, 'stats.db')]
    if 'enable_tls' in opts:
        args += ['--tls', cert_dir]
    if 'persistent' in opts:
        args += ['--rooms-db-file', os.path.join(work_dir, 'rooms.db')]

    if 'max_username' in opts:
        args += ['--max-username-length', str(opts['max_username'])]
    if 'max_chat_message' in opts:
        args += ['--max-chat-message-length', str(opts['max_chat_message'])]
    if 'permanent_rooms' in opts:
        rooms = '\n'.join(opts['permanent_rooms'])
        args += ['--permanent-rooms-file', __temp_file('rooms.list', rooms)]

    if 'listen_ipv4' in opts and 'listen_ipv6' in opts:  # dual stack
        args += ['--interface-ipv4', opts['listen_ipv4']]
        args += ['--interface-ipv6', opts['listen_ipv6']]
    elif 'listen_ipv4' in opts:
        args += ['--ipv4-only', '--interface-ipv4', opts['listen_ipv4']]
    elif 'listen_ipv6' in opts:
        args += ['--ipv6-only', '--interface-ipv6', opts['listen_ipv6']]
    return args


def boot() -> None:
    init_opts()
    sys.argv = ['syncplay'] + sp_convert(load_opts())
    debug_msg('Syncplay startup arguments', sys.argv)

    from syncplay import ep_server
    sys.exit(ep_server.main())


if __name__ == '__main__':
    boot()
