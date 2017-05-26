#!/usr/bin/env python

from __future__ import print_function
import sys

from paramiko import SSHClient, RSAKey, AutoAddPolicy

from common import ssh_connect, upload_file, ssh_get_key

def do_prepare(ip, username, keystr, keypass=None):
    key = ssh_get_key(keystr, keypass)

    client = ssh_connect(ip, username, key)

    # upload minimal requirements stuff
    upload_file(client, 'install.sh',  0o0555)

    # install Docker
    print("install docker")
    (stdin, stdout, stderr) = client.exec_command('./install.sh')
    for line in stdout:
        print(line, end="")

    print("done")
    client.close()

    # close and reopen connection to refresh ID and Groups
    client = ssh_connect(ip, username='ubuntu', key=key)

    upload_file(client, 'build.sh', 0o0555)
    print("build docker image")
    (stdin, stdout, stderr) = client.exec_command('./build.sh')
    for line in stdout:
        print(line, end="")
