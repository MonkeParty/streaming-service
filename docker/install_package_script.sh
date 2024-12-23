#!/bin/sh
add-apt-repository ppa:savoury1/ffmpeg4
apt-get update
apt-get install -y --no-install-recommends ffmpeg
apt-get clean && \
rm -rf /var/lib/apt/lists/*