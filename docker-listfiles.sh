#!/usr/bin/env bash

docker create --name="tmp_$$" ghcr.io/vicariousdrama/nodeyez:latest
docker export tmp_$$ > docker-listfiles-tar.tar
docker rm tmp_$$
tar -tvf docker-listfiles-tar.tar
rm docker-listfiles-tar.tar