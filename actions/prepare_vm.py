#!/usr/bin/env python

from __future__ import print_function
import os

from common import ssh_connect, upload_file, ssh_get_key

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def do_prepare(ip, username, keystr, keypass=None,
               token=""):
    key = ssh_get_key(keystr, keypass)

    client = ssh_connect(ip, username, key)

    # upload minimal requirements stuff
    print("BASE_DIR", BASE_DIR)
    upload_file(client, BASE_DIR + '/install.sh', perm=0o0555)

    # install Docker
    print("install docker")
    (stdin, stdout, stderr) = client.exec_command('./install.sh')
    for line in stdout:
        print(line.encode('utf-8'), end="")

    print("done")
    client.close()

    # close and reopen connection to refresh ID and Groups
    client = ssh_connect(ip, username='ubuntu', key=key)

    upload_file(client, BASE_DIR + '/build.sh', perm=0o0555)
    print("build docker image")
    (stdin, stdout, stderr) = client.exec_command(
        './build.sh', environment={'GITHUB_TOKEN': token})
    for line in stdout:
        print(line.encode('utf-8'), end="")
