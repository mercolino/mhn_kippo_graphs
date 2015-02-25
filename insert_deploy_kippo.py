import sqlite3
import sys
from datetime import datetime

try:
    conn = sqlite3.connect(sys.argv[1])
except sqlite3.OperationalError as e:
    print e
    sys.exit(1)
cur = conn.cursor()
f = open('deploy_kippo_MySQL_support.sh', 'r')
date = datetime.now()
notes = 'Initial deploy script for Ubuntu - Kippo with MySQL support'
name = 'Ubuntu - Kippo with MySQL support'
sql = "INSERT INTO deploy_scripts (script,date,notes,name,user_id) " \
      "VALUES (?, ?, ?, ?, ?)"
print sql
cur.execute(sql, (f.read(), date.strftime('%Y-%m-%d %H:%m:%d'), notes, name, 1))
conn.commit()
conn.close()
f.close()

__author__ = 'mercolino'