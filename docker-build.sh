#!/usr/bin/env bash

# setup temp dockerbuild folder for single layer copy
# scripts
mkdir -p dockerbuild/home/nodeyez/nodeyez/scripts/LuxorLabs
cp ./scripts/*.py dockerbuild/home/nodeyez/nodeyez/scripts/
cp ./scripts/LuxorLabs/*.py dockerbuild/home/nodeyez/nodeyez/scripts/LuxorLabs/
# images
mkdir -p dockerbuild/home/nodeyez/nodeyez/images
cp ./images/blockhash-dungeon-bitcoin-*.png dockerbuild/home/nodeyez/nodeyez/images/
cp ./images/logo.png dockerbuild/home/nodeyez/nodeyez/images/
cp ./images/nodeyez.svg dockerbuild/home/nodeyez/nodeyez/images/
cp ./images/samourai.png dockerbuild/home/nodeyez/nodeyez/images/
cp ./images/whirlpool-*-32.png dockerbuild/home/nodeyez/nodeyez/images/
# TODO: service scripts
# TODO: web server

# make the image
docker build . --tag ghcr.io/vicariousdrama/nodeyez:latest

# remove temp dockerbuild folder
rm -rf dockerbuild/
