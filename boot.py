#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from __future__ import annotations

import os
import sys
import yaml
import argparse
from typing import Any
from typing import Generator
from syncplay import ep_server


class SyncplayBoot:
    """ Handle Syncplay bootstrap arguments. """
    def __debug(self, msg: str) -> None:
        """ Print out debug information. """
        if self.__debug_mode:
            print(f'\033[90m{msg}\033[0m', file=sys.stderr)

    def __build_parser(self) -> Generator:
        """ Build arguments parser for Syncplay bootstrap. """
        parser = argparse.ArgumentParser(description='Syncplay Docker Bootstrap')
        yield parser.add_argument('-p', '--port', type=int, help='listen port of syncplay server')
        yield parser.add_argument('--password', type=str, help='authentication of syncplay server')
        yield parser.add_argument('--motd', type=str, help='welcome text after the user enters the room')
        yield parser.add_argument('--salt', type=str, help='string used to secure passwords')
        yield parser.add_argument('--random-salt', action='store_true', help='use a randomly generated salt value')
        yield parser.add_argument('--isolate-rooms', action='store_true', help='room isolation enabled')
        yield parser.add_argument('--disable-chat', action='store_true', help='disables the chat feature')
        yield parser.add_argument('--disable-ready', action='store_true', help='disables the readiness indicator feature')
        yield parser.add_argument('--enable-stats', action='store_true', help='enable syncplay server statistics')
        yield parser.add_argument('--enable-tls', action='store_true', help='enable tls support of syncplay server')
        yield parser.add_argument('--persistent', action='store_true', help='enables room persistence')
        yield parser.add_argument('--max-username', type=int, help='maximum length of usernames')
        yield parser.add_argument('--max-chat-message', type=int, help='maximum length of chat messages')
        yield parser.add_argument('--permanent-rooms', type=str, nargs='*', help='permanent rooms of syncplay server')
        self.__parser = parser

    def __build_options(self) -> Generator:
        """ Build options list for Syncplay bootstrap. """
        for action in [x for x in self.__build_parser()]:
            is_list = type(action.nargs) is str
            opt_type = bool if action.type is None else action.type
            yield action.dest, opt_type, is_list

    def __init__(self, args: list[str], config: dict[str, Any],
                 work_dir: str, cert_dir: str, debug_mode: bool = False):
        self.__work_dir = work_dir
        self.__cert_dir = cert_dir
        self.__debug_mode = debug_mode
        self.__options = [x for x in self.__build_options()]  # list[(NAME, TYPE, IS_LIST)]
        self.__debug(f'Bootstrap options -> {self.__options}\n')

        env_opts = self.__load_from_env()
        self.__debug(f'Environment options -> {env_opts}\n')
        cfg_opts = self.__load_from_config(config)
        self.__debug(f'Configure file options -> {cfg_opts}\n')
        cli_opts = self.__load_from_args(args)
        self.__debug(f'Command line options -> {cli_opts}\n')

        self.__opts = env_opts | cfg_opts | cli_opts
        self.__debug(f'Bootstrap final options -> {self.__opts}')

    def __load_from_args(self, raw_args: list[str]) -> dict[str, Any]:
        """ Loading options from command line arguments. """
        args = self.__parser.parse_args(raw_args)
        self.__debug(f'Command line arguments -> {args}')
        arg_filter = lambda x: x is not None and x is not False
        return {x: y for x, y in vars(args).items() if arg_filter(y)}

    def __load_from_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """ Loading options from configure file. """
        self.__debug(f'Configure file -> {config}')
        options = {x[0].replace('_', '-'): x[0] for x in self.__options}
        return {options[x]: config[x] for x in options if x in config}

    def __load_from_env(self) -> dict[str, Any]:
        """ Loading options from environment variables. """
        def __convert(opt_raw: str, opt_field: str, opt_type: type) -> tuple[str, Any]:
            if opt_type is str:
                return opt_field, opt_raw
            elif opt_type is int:
                return opt_field, int(opt_raw)
            elif opt_type is bool:
                return opt_field, opt_raw.upper() in ['ON', 'TRUE']

        self.__debug(f'Environment variables -> {os.environ}')
        options = {x.upper(): (x, t) for x, t, is_list in self.__options if not is_list}  # filter non-list options
        return dict([__convert(os.environ[x], *y) for x, y in options.items() if x in os.environ])

    @staticmethod
    def __temp_file(file: str, content: str) -> str:
        """ Create and save content to temporary files. """
        file = os.path.join('/tmp/', file)
        with open(file, 'w') as fp:
            fp.write(content)
        return file

    def release(self) -> list[str]:
        """ Construct the startup arguments for syncplay server. """
        args = ['--port', str(self.__opts.get('port', 8999))]
        if 'password' in self.__opts:
            args += ['--password', self.__opts['password']]
        if 'motd' in self.__opts:
            args += ['--motd-file', SyncplayBoot.__temp_file('motd.data', self.__opts['motd'])]

        salt = self.__opts.get('salt', None if 'random_salt' in self.__opts else '')
        if salt is not None:
            args += ['--salt', salt]  # using random salt without this option
        for opt in ['isolate_rooms', 'disable_chat', 'disable_ready']:
            if opt in self.__opts:
                args.append(f'--{opt.replace("_", "-")}')

        if 'enable_stats' in self.__opts:
            args += ['--stats-db-file', os.path.join(self.__work_dir, 'stats.db')]
        if 'enable_tls' in self.__opts:
            args += ['--tls', self.__cert_dir]
        if 'persistent' in self.__opts:
            args += ['--rooms-db-file', os.path.join(self.__work_dir, 'rooms.db')]

        if 'max_username' in self.__opts:
            args += ['--max-username-length', str(self.__opts['max_username'])]
        if 'max_chat_message' in self.__opts:
            args += ['--max-chat-message-length', str(self.__opts['max_chat_message'])]
        if 'permanent_rooms' in self.__opts:
            rooms = '\n'.join(self.__opts['permanent_rooms'])
            args += ['--permanent-rooms-file', SyncplayBoot.__temp_file('rooms.list', rooms)]

        self.__debug(f'Syncplay startup arguments -> {args}')
        return args


def syncplay_boot() -> None:
    """ Bootstrap the syncplay server. """
    work_dir = os.environ.get('WORK_DIR', '/data')
    cert_dir = os.environ.get('CERT_DIR', '/certs')
    config_file = os.environ.get('CONFIG', 'config.yml')
    debug_mode = os.environ.get('DEBUG', '').upper() in ['ON', 'TRUE']

    config = yaml.safe_load(open(config_file).read()) if os.path.exists(config_file) else {}
    bootstrap = SyncplayBoot(sys.argv[1:], config, work_dir, cert_dir, debug_mode)
    sys.argv = ['syncplay'] + bootstrap.release()


if __name__ == '__main__':
    syncplay_boot()
    sys.exit(ep_server.main())
