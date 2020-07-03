# Base our image on the latest Envoy image.
FROM envoyproxy/envoy:v1.14.3
# FROM dwflynn/envoy-debug:20170501

# This Dockerfile is set up to install all the application-specific stuff into
# /application.
#
# NOTE: If you don't know what you're doing, it's probably a mistake to 
# blindly hack up this file.

# We need curl, pip, and dnsutils (for nslookup).
RUN apt-get update && apt-get -q install -y \
    curl \
    python3 \
    python3-pip \
    dnsutils

RUN pip3 install pipenv

# Set WORKDIR to /application which is the root of all our apps then COPY 
# only requirements.txt to avoid screwing up Docker caching and causing a
# full reinstall of all dependencies when dependencies are not changed.

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

WORKDIR /application
COPY Pipfile .
COPY Pipfile.lock .

# Install application dependencies
RUN pipenv install

# COPY the app code and configuration into place, then perform any final
# configuration steps.
COPY service.py .

# COPY the entrypoint script and make it runnable.
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
