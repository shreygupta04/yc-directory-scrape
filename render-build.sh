#!/usr/bin/env bash

# Install system packages needed for headless browsers
apt-get update
apt-get install -y \
    libgtk-3-0 \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libgstgl-1.0-0 \
    libgstcodecparsers-1.0-0 \
    libavif15 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2 \
    libasound2 \
    libxshmfence1 \
    fonts-liberation \
    libnspr4 \
    libnss3 \
    xdg-utils
