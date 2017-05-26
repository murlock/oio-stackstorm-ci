#!/bin/bash

if [ -d dockerfiles ]; then
    rm -rf dockerfiles
fi

# FIXME: use real REPO with real branch name
git clone https://github.com/murlock/dockerfiles.git -b build_source
cd dockerfiles/openio-sds-source/
docker build -t sds-source ubuntu

# TODO: push docker image to registry ?
