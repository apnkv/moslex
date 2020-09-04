#!/usr/bin/env bash

rm -f "./db.sqlite"
python3 ./moslex/scripts/initializedb.py production.ini
pserve --reload production.ini
