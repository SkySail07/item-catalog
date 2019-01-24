#!/bin/bash
set -ex

export LANG=en_US.utf-8
export LC_ALL=en_US.utf-8
export FLASK_APP=run.py


flask db init
flask db migrate
flask db upgrade