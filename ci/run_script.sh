#!/bin/sh
Xvfb :99 -screen 0 640x480x24 &
klayout -e -z -nc -rx -r "$@"