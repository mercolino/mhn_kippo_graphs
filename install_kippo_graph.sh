#!/bin/bash

set -e

# Install MySQL and matplotlib dependencies
sudo apt-get update
sudo apt-get install -y mysql-server libpng12-dev libfreetype6-dev libxft-dev

# Getting MHN directory
MHN_HOME=`dirname $0`/../..
cd $MHN_HOME
MHN_HOME=`pwd`

# Installing pymysql numpy matplotlib and PILLOW
. env/bin/activate
pip install pymysql numpy matplotlib PILLOW

# Downloading the sql file to create tables on the databases
cd $MHN_HOME/scripts
sudo wget https://github.com/threatstream/kippo/raw/master/doc/sql/mysql.sql -O kippo_mysql.sql

# Creating the directory inside mhn server app
mkdir $MHN_HOME/server/mhn/static/img/kippo_graphs
chown www-data:www-data $MHN_HOME/server/mhn/static/img/kippo_graphs

# Adding the kippo with mysql support to mhn app
python insert_deploy_kippo.py %MHN_HOME/server/mhn.db

# Creating CronTab to run the generating graph script every 5 minutes
crontab -l | { cat; echo "*/5 * * * * python $MHN_HOME/scripts/mhn_kippo_graphs/kippo_generate_graphs.py"; } | crontab -

# Remember to run this script
echo "Remember, each time a kippo sensor with MySQL support is installed you should run the following command:"
echo "sudo python /opt/mhn/scripts/mhn_kippo_graphs/kippo_update_mysql.py"