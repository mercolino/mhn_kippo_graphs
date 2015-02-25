#!/bin/bash

set -e

# Getting MHN directory
MHN_HOME=`dirname $0`/../..
cd $MHN_HOME
MHN_HOME=`pwd`

# Activate Virtual Environment
. env/bin/activate

# Run kippo_update_config.py
cd scripts/mhn_kippo_graphs/
python kippo_update_config.py