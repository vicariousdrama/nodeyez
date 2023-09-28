FROM python:3.10.0-alpine

# Copy in our filesystem
COPY ./dockerbuild /

# Set work directory
WORKDIR /home/nodeyez/nodeyez/scripts
