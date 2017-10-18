#!/usr/bin/env python

from __future__ import print_function
import os

from common import ssh_connect, upload_file, ssh_get_key

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def do_prepare_deprecated(ip, username, keystr, keypass=None,
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
        'export GITHUB_TOKEN="%s"; ./build.sh' % token)
    for line in stdout:
        print(line.encode('utf-8'), end="")


def do_prepare(ip, username, keystr, keypass=None,
               token=""):
    key = ssh_get_key(keystr, keypass)

    client = ssh_connect(ip, username, key)

    # Checkout oio-qa
    print("XXXXXXX CHECKOUT")
    (stdin, stdout, stderr) = client.exec_command(
        'git clone https://github.com/murlock/oio-qa.git -b stackstorm')
    for line in stdout:
        print(line.encode('utf-8'), end="")

    # Fill token
    print("XXXXXXX TOKEN")
    (stdin, stdout, stderr) = client.exec_command(
        'echo export GITHUB_TOKEN=%s >> .profile' % token)
    for line in stdout:
        print(line.encode('utf-8'), end="")

    # Launch install step
    print("XXXXXXX INSTALL")
    (stdin, stdout, stderr) = client.exec_command(
        'cd oio-qa/prepare && ./install.sh')
    for line in stdout:
        print(line.encode('utf-8'), end="")
    # Launch build step
    print("XXXXXXX BUILD")
    (stdin, stdout, stderr) = client.exec_command(
        'cd oio-qa/prepare && ./build.sh')
    for line in stdout:
        print(line.encode('utf-8'), end="")
