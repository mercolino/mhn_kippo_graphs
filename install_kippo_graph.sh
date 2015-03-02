#!/bin/bash

set -e
set -x

# Install MySQL and matplotlib dependencies
sudo apt-get update
sudo apt-get install -y mysql-server libpng12-dev libfreetype6-dev libxft-dev

# Modifying Mysql configuration to allow connection from everywhere
sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf
sudo service mysql restart

# Getting MHN directory
MHN_HOME=`dirname $0`/../..
cd $MHN_HOME
MHN_HOME=`pwd`

# Installing pymysql numpy matplotlib and PILLOW
. env/bin/activate
pip install pymysql numpy matplotlib PILLOW

# Downloading the sql file to create tables on the databases
cd scripts/
sudo wget https://github.com/threatstream/kippo/raw/master/doc/sql/mysql.sql -O kippo_mysql.sql

# Creating the directory inside mhn server app
mkdir $MHN_HOME/server/mhn/static/img/kippo_graphs
chown www-data:www-data $MHN_HOME/server/mhn/static/img/kippo_graphs

# Adding the kippo with mysql support to mhn app
cd mhn_kippo_graphs/
sudo python insert_deploy_kippo.py $MHN_HOME/server/mhn.db

# Creating CronTab to run the generating graph script every 5 minutes
crontab -l | { cat; echo "*/5 * * * * $MHN_HOME/env/bin/python $MHN_HOME/scripts/mhn_kippo_graphs/kippo_generate_graphs.py"; } | crontab -

# Modifying Web Application
# Modifying configuration file to add channel kippo-mysql
sed -i~ '$i\    '\''kippo-mysql'\'' : ['\''kippo.sessions'\'']' $MHN_HOME/server/config.py

# Removing blank lines in base.html
sed -i~ "/^\s*$/d" $MHN_HOME/server/mhn/templates/base.html

# Adding menu item
sed -i~ '
/\s*<\/ul>/ {
N
/\n.*Right Nav Section.*/ i\
\                    <li><a href="{{ url_for('\''kg.kippo_graph'\'') }}">Kippo-Graph</a></li>
}' $MHN_HOME/server/mhn/templates/base.html

# Registering Blueprint with Flask app
sed -i~ '
/mhn.register_blueprint(auth)/ a\
\
from mhn.kg.views import kg\
mhn.register_blueprint(kg)
' $MHN_HOME/server/mhn/__init__.py

#Copying blueprint and templates and changing the ownerships
cd $MHN_HOME/scripts/mhn_kippo_graphs
mkdir $MHN_HOME/server/mhn/kg/
sudo cp mhn/kg/* $MHN_HOME/server/mhn/kg/
mkdir $MHN_HOME/server/mhn/templates/kg/
sudo cp mhn/templates/kg/* $MHN_HOME/server/mhn/templates/kg/
sudo chown -R www-data:www-data $MHN_HOME/server/mhn/kg/
sudo chown -R www-data:www-data $MHN_HOME/server/mhn/templates/kg/

#Restart uwsgi
sudo supervisorctl restart mhn-uwsgi

# Remember to run this script
echo "Remember, each time a kippo sensor with MySQL support is installed you should run the following command:"
echo "sudo /opt/mhn/env/bin/python /opt/mhn/scripts/mhn_kippo_graphs/kippo_update_mysql.py"