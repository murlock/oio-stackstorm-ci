#!/usr/bin/env python

from __future__ import print_function
import os

from common import ssh_connect, ssh_get_key


def do_prepare(ip, username, keystr, keypass=None,
               token=""):
    key = ssh_get_key(keystr, keypass)

    client = ssh_connect(ip, username, key)

    # Fill token
    print("XXXXXXX TOKEN")
    (stdin, stdout, stderr) = client.exec_command(
        'echo "export GITHUB_TOKEN=%s" > ~/.env' % token)
    print("STDOUT:")
    for line in stdout:
        print(line.encode('utf-8'), end="")
    print("STDERR:")
    for line in stderr:
        print(line.encode('utf-8'), end="")


    # Checkout oio-qa
    print("XXXXXXX CHECKOUT")
    (stdin, stdout, stderr) = client.exec_command(
        'git clone https://github.com/murlock/oio-qa.git -b stackstorm')
    print("STDOUT:")
    for line in stdout:
        print(line.encode('utf-8'), end="")
    print("STDERR:")
    for line in stderr:
        print(line.encode('utf-8'), end="")

    # Launch install step
    print("XXXXXXX INSTALL")
    (stdin, stdout, stderr) = client.exec_command(
        'cd ~/oio-qa/prepare && ./install.sh')
    print("STDOUT:")
    for line in stdout:
        print(line.encode('utf-8'), end="")
    print("STDERR:")
    for line in stderr:
        print(line.encode('utf-8'), end="")

    # reconnect to proper use of group
    client = ssh_connect(ip, username, key)


    # Launch build step
    print("XXXXXXX BUILD")
    (stdin, stdout, stderr) = client.exec_command(
        'cd ~/oio-qa/prepare && ./build.sh')
    print("STDOUT:")
    for line in stdout:
        print(line.encode('utf-8'), end="")
    print("STDERR:")
    for line in stderr:
        print(line.encode('utf-8'), end="")
