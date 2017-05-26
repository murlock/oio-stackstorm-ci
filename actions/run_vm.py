#!/usr/bin/env python

from __future__ import print_function
import os
import sys

from common import ssh_connect, upload_file, ssh_get_key

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def do_run(ip, username, keystr, keypass=None):
    key = ssh_get_key(keystr, keypass)
    client = ssh_connect(ip, username, key)

    # upload minimal requirements stuff
    upload_file(client, BASE_DIR + '/run.sh', perm=0o0555)

    (stdin, stdout, stderr) = client.exec_command('./run.sh', get_pty=True)
    for line in stdout:
        print(line, end="")
