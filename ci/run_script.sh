#!/bin/sh
Xvfb :99 -screen 0 800x600x16 &
klayout -e -z -nc -rx -r "$@"