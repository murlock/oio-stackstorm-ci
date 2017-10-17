#!/bin/bash

if [ -d dockerfiles ]; then
    rm -rf dockerfiles
fi

# FIXME: use real REPO with real branch name
git clone https://github.com/murlock/dockerfiles.git -b build_source
cd dockerfiles/openio-sds-source/
docker build -t sds-source ubuntu

# TODO: push docker image to registry ?



#
# OIOFS
#
if [ -d oiofs ]; then
    rm -rf oiofs
fi
if [ -z "${GITHUB_TOKEN}" ]; then
    echo "No GITHUB Token, cannot interacte with private repository"
else
    git clone https://unused:${GITHUB_TOKEN}@github.com/openio-private/oio-fs.git
    cd oio-fs/docker
    docker build -t oiofs --build-arg GITHUB_TOKEN=${GITHUB_TOKEN} .
fi
