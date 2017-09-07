#!/usr/bin/env python

from __future__ import print_function

import os

try:
    from st2actions.runners.pythonrunner import Action
except:
    class Action(object):
        def __init__(self, config):
            pass


class EchoAction(Action):
    def __init__(self, config):
        super(EchoAction, self).__init__(config=config)

    def run(self):
        print("Success")
        ret = {
            'res': {
                "s3ceph": {
                    "FAIL": 0,
                    "SKIP": 0,
                    "OK": 34,
                    "ERROR": 1
                },
                "s3cmd": {
                    "FAIL": 28,
                    "SKIP": 2,
                    "OK": 11,
                    "ERROR": 0
                }
            },
            'info': 'not set at this time'

        }
        return (True, ret)


def cli():
    cfg = {}
    for key in ['OS_AUTH_URL', 'OS_PASSWORD', 'OS_TENANT_ID',
                'OS_TENANT_NAME', 'OS_USERNAME']:
        cfg[key] = os.getenv(key)
    job = EchoAction(cfg)
    job.run()


if __name__ == "__main__":
    cli()
