#!/usr/bin/env python3

import os
import sys
import time

# def runSyncplay(args: list, envs: dict) -> None:
#     os.execvpe('syncplay-server', ['syncplay-server'] + args, envs)

# runSyncplay(['--password', 'test'], {'PYTHONUNBUFFERED': '1'})

print(sys.argv)
print(os.environ)

time.sleep(200)
