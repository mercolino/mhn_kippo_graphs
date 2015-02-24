#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y mysql-server libpng12-devel libfreetype6-dev libxft-dev

MHN_HOME=`dirname $0`/..
cd $MHN_HOME
MHN_HOME=`pwd`

. env/bin/activate
pip install pymysql numpy matplotlib PILLOW

cd $MHN_HOME/scripts
sudo wget https://github.com/threatstream/kippo/raw/master/doc/sql/mysql.sql -O kippo_mysql.sql

sed -i "150i\            'Ubuntu - Suricata': path.abspath('../scripts/mhn_kippo_graphs/deploy_kippo_MySQL_support.sh')," /opt/mhn/server/mhn/__init__.py

supervisorctl restart mhn-uwsgi

echo "Remember, each time a kippo sensor with MySQL support is installed you should run the following command:"
echo "sudo python /opt/mhn/scripts/mhn_kippo_graphs/kippo_update_mysql.py"