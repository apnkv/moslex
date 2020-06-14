#!/usr/bin/env bash

rm -f "./db.sqlite"
clld initdb development.ini
