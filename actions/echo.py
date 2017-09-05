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
        return (True, "Success")


def cli():
    cfg = {}
    for key in ['OS_AUTH_URL', 'OS_PASSWORD', 'OS_TENANT_ID',
                'OS_TENANT_NAME', 'OS_USERNAME']:
        cfg[key] = os.getenv(key)
    job = EchoAction(cfg)
    job.run()


if __name__ == "__main__":
    cli()
