#!/usr/bin/env python3

import os
import sys
from syncplay import ep_server


def checkOpt(args: list, option: str) -> bool:
    if option not in args:  # option not found
        return False
    args.remove(option)  # remove target option
    return True


def fetchOpt(args: list, option: str, default):
    if option not in args:  # option not found
        return default
    index = args.index(option)
    if index + 1 == len(args):
        print('Error: `%s` missing value' % option, file = sys.stderr)
        sys.exit(1)
    targetVal = args[index + 1]
    del sys.argv[index : index + 2]  # remove target option and value
    return targetVal


isDebug = checkOpt(sys.argv, '--debug')


portValue = None  # no specify in default
if 'PORT' in os.environ:  # `PORT` env variable
    portValue = os.environ['PORT']
portValue = fetchOpt(sys.argv, '--port', portValue)


passwdStr = None  # no password in default
if 'PASSWD' in os.environ:  # `PASSWD` env variable
    passwdStr = os.environ['PASSWD']
passwdStr = fetchOpt(sys.argv, '--password', passwdStr)


saltValue = ''  # using empty string in default
if 'SALT' in os.environ:  # `SALT` env variable
    saltValue = os.environ['SALT']
if checkOpt(sys.argv, '--random-salt'):
    saltValue = None
saltValue = fetchOpt(sys.argv, '--salt', saltValue)


isolateRoom = False  # disable isolate room in default
if 'ISOLATE' in os.environ and os.environ['ISOLATE'] in ['ON', 'TRUE']:
    isolateRoom = True
if checkOpt(sys.argv, '--isolate-room'):
    isolateRoom = True


tlsPath = '/certs'
if 'TLS_PATH' in os.environ:  # `TLS_PATH` env variable
    tlsPath = os.environ['TLS_PATH']
tlsPath = fetchOpt(sys.argv, '--tls', tlsPath)

enableTls = False
if checkOpt(sys.argv, '--enable-tls'):
    enableTls = True
if 'TLS' in os.environ and os.environ['TLS'] in ['ON', 'TRUE']:
    enableTls = True


motdMessage = None  # without motd message in default
if 'MOTD' in os.environ:  # `MOTD` env variable
    motdMessage = os.environ['MOTD']
motdMessage = fetchOpt(sys.argv, '--motd', motdMessage)

motdFile = fetchOpt(sys.argv, '--motd-file', None)
if motdFile is not None:
    motdMessage = None  # cover motd message
elif motdMessage is not None:
    motdFile = '/app/syncplay/motd'
    os.system('mkdir -p /app/syncplay/')
    with open(motdFile, mode = 'w', encoding = 'utf-8') as fileObj:
        fileObj.write(motdMessage)


if isDebug:  # print debug log
    if portValue is not None:
        print('Port -> %s' % portValue, file = sys.stderr)

    if saltValue is None:
        print('Using random salt', file = sys.stderr)
    else:
        print('Salt -> `%s`' % saltValue, file = sys.stderr)

    if isolateRoom:
        print('Isolate room enabled', file = sys.stderr)

    if passwdStr is None:
        print('Running without password', file = sys.stderr)
    else:
        print('Password -> `%s`' % passwdStr, file = sys.stderr)

    if enableTls:
        print('TLS enabled -> `%s`' % tlsPath, file = sys.stderr)

    if motdFile is not None:
        print('MOTD File -> `%s`' % motdFile, file = sys.stderr)
    if motdMessage is not None:
        print('MOTD message -> `%s`' % motdMessage, file = sys.stderr)


if portValue is not None:
    sys.argv += ['--port', portValue]
if passwdStr is not None:
    sys.argv += ['--password', passwdStr]
if saltValue is not None:
    sys.argv += ['--salt', saltValue]
if enableTls:
    sys.argv += ['--tls', tlsPath]
if isolateRoom:
    sys.argv += ['--isolate-room']
if motdFile is not None:
    sys.argv += ['--motd-file', motdFile]


if isDebug:  # print debug log
    print('Boot args -> %s' % sys.argv, file = sys.stderr)


sys.exit(ep_server.main())
