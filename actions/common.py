#!/usr/bin/env python

from __future__ import print_function
import os
import stat
from zipfile import ZipFile
try:
    from cStringIO import StringIO
except:
    from io import StringIO
from io import BytesIO
import socket
import time

from paramiko import SSHClient, RSAKey, AutoAddPolicy
from paramiko.ssh_exception import BadHostKeyException, SSHException, \
                                   AuthenticationException, \
                                   NoValidConnectionsError
import requests


def retrieve_or_create_keypair(conn, name, create_if_missing=False):
    keypair = conn.compute.find_keypair(name, ignore_missing=True)
    if keypair:
        return (keypair, False)

    if not create_if_missing:
        raise ValueError("Missing Keypair %s" % name)
    keypair = conn.compute.create_keypair(name=name)
    return (keypair, True)


def remove_keypair(conn, name):
    conn.compute.delete_keypair(name, ignore_missing=True)


def ssh_connect(ip, username, key, quiet=False):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    delay = 2
    while delay < 60:
        try:
            client.connect(ip, username=username, pkey=key)
            return client
        except (BadHostKeyException, AuthenticationException,
                SSHException, NoValidConnectionsError, socket.error) as e:
            if not quiet:
                print("SSH connecting to {0}: {1}".format(ip, str(e)))
            time.sleep(delay)
            delay *= 2
    return None


def upload_file(client, filename, target=None, perm=0o0400):
    print("uploading", filename)
    if target is None:
        target = os.path.basename(filename)
    sftp = client.open_sftp()
    fp = sftp.file(target, mode='w')
    fp.write(open(filename).read())
    fp.close()

    sftp.chmod(target, perm)
    sftp.close()
    print("success")


def download_directory(client, path, dest):
    sftp = client.open_sftp()

    def is_directory(path):
        try:
            return stat.S_ISDIR(sftp.stat(path).st_mode)
        except IOError:
            # Path does not exist, so by definition not a directory
            print("Testing invalid directory")
            return False

    def parse_directory(path, dest):
        item_list = sftp.listdir(path)
        dest = str(dest)

        if not os.path.isdir(dest):
            os.mkdir(dest)

        for item in item_list:
            item = str(item)

            if is_directory(path + "/" + item):
                parse_directory(path + "/" + item, dest + "/" + item)
            else:
                print("retrieve {0}/{1}".format(path, item))
                sftp.get(path + "/" + item, dest + "/" + item)

    parse_directory(path, dest)


def ssh_get_key(keystr, keypass=None):
    buf = StringIO(keystr)
    key = RSAKey.from_private_key(buf, password=keypass)
    return key


def zip_in_memory(result):
    tmpzip = BytesIO()
    myzip = ZipFile(tmpzip, mode="w")
    result = os.path.abspath(result)

    for base, _, fnames in os.walk(result):
        for fname in fnames:
            path = os.path.abspath(os.path.join(base, fname))
            myzip.write(path, path[len(result):])
    myzip.close()
    tmpzip.seek(0)
    return tmpzip


def upload_result(result, url):
    # retrieve CSRF token
    content = zip_in_memory(result)
    get = requests.get(url)
    post = requests.post(
        url,
        files={"result": content},
        data={'csrfmiddlewaretoken': get.cookies['csrftoken']},
        cookies=get.cookies)
    if post.status_code != requests.codes.ok:
        print("An error has occured while submitting result")
        try:
            print(post.content)
        except:
            print(post.content.encode('utf-8'))
        return False
    return True
