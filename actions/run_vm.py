#!/usr/bin/env python

from __future__ import print_function
import os

from common import ssh_connect, ssh_get_key

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def do_run(ip, username, keystr, keypass=None):
    key = ssh_get_key(keystr, keypass)
    client = ssh_connect(ip, username, key)

    (stdin, stdout, stderr) = client.exec_command(
        'cd oio-qa/run && ./run.sh', get_pty=True)
    for line in stdout:
        print(line.encode('utf-8'), end="")
