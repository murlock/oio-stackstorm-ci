#!/usr/bin/env python

from __future__ import print_function

import os
import tempfile
import time
import shutil
import traceback
import uuid

try:
    from st2actions.runners.pythonrunner import Action
except:
    class Action(object):
        def __init__(self, config):
            pass

from common import remove_keypair, download_directory
from common import ssh_connect, ssh_get_key, upload_result

import create_vm
from prepare_vm import do_prepare
from run_vm import do_run
from html import create_html_report


class BuildAction(Action):
    def __init__(self, config):
        for key, val in config.items():
            if key in create_vm.CREDS:
                create_vm.CREDS[key] = val
        super(BuildAction, self).__init__(config=config)
        self.github_token = config.get('GITHUB_TOKEN')
        self.properties = {}
        if self.github_token:
            print("GITHUB TOKEN:", self.github_token[0:2] + "...")
        else:
            print("No GITHUB TOKEN")

    def run(self):
        create_vm.os_connect()
        try:
            results = self.build()
            ret = (True, {'res': results})
        except:
            traceback.print_exc()
            ret = (False, {'error': traceback.format_exc()})
        self.cleanup()
        # This environment variable is not available outside of the action
        # script, so get it here and return it to allow notification message to
        # contain the URL to the ST2 logs:
        # https://${ST2_HOST}/#/history/${ST2_ACTION_EXECUTION_ID}/general
        ret[1]['execution_id'] = os.environ['ST2_ACTION_EXECUTION_ID']
        return ret

    def build(self):
        # FIXME: should be PR name or git revision
        create_vm.SERVER_NAME = "{0}-{1}".format("master", str(uuid.uuid1()))
        create_vm.VOLUME_NAME = create_vm.SERVER_NAME + "-vol"
        create_vm.KEYPAIR_NAME = create_vm.SERVER_NAME + "-id"

        print("Create Instance")
        self.properties = create_vm.create_server(create_vm.CONN)

        print("key priv\n", self.properties['keypriv'])
        print("key pub\n", self.properties['keypub'])

        # ssh_connect use retry mecanism to connect to VM
        # but we still use a delay to allow VM to boot
        time.sleep(20)

        print("Prepare and build Docker template")
        do_prepare(self.properties['ip'],
                   'ubuntu',
                   self.properties['keypriv'],
                   token=self.github_token)

        print("Launch test")
        do_run(self.properties['ip'],
               'ubuntu',
               self.properties['keypriv'])

        tmpdir = tempfile.mkdtemp()

        # download artifacts
        key = ssh_get_key(self.properties['keypriv'])
        client = ssh_connect(self.properties['ip'], 'ubuntu', key)
        download_directory(client, "output/", tmpdir)
        # build webpage
        results = create_html_report(tmpdir)

        # and upload somewhere
        # TODO: include properies like branch/tag/commit id/PR/time consumed
        to_delete = True
        if os.getenv('RESULT_UPLOAD_URL'):
            print("Uploading result to", os.getenv('RESULT_UPLOAD_URL'))
            to_delete = upload_result(tmpdir, os.getenv('RESULT_UPLOAD_URL'))

        # remove tmpdir
        if to_delete:
            shutil.rmtree(tmpdir)
        else:
            print("Result of build available in", tmpdir)
        return results

    def cleanup(self):
        if self.properties.get('keycreated', False):
            remove_keypair(create_vm.CONN, self.properties['keyname'])

        if self.properties.get('server_id', None):
            create_vm.delete_server(create_vm.CONN,
                                    self.properties['server_id'])
        self.properties = {}


def cli():
    cfg = {}
    for key in ['OS_AUTH_URL', 'OS_PASSWORD', 'OS_TENANT_ID',
                'OS_TENANT_NAME', 'OS_USERNAME',
                'GITHUB_TOKEN']:
        cfg[key] = os.getenv(key)
    job = BuildAction(cfg)
    job.run()


if __name__ == "__main__":
    cli()
