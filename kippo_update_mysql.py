import kippo_update_config as conf
import pymongo
import sqlite3
import sys
import pymysql


def usage():
    """Function to print how to use the script"""
    print "Python Script to create the kippo databases, username and paswords to keep the log data centralized, " \
          "run it every time you deploy a new kippo sensor."
    print "Usage:\n" \
          "\tpython kippo_update_mysql.py [-h|clean]\n" \
          "\t\tUse -h to print this help\n" \
          "\t\tUse \"clean\" without quotes to clean the kippo databases of sensors that are not deployed anymore\n" \
          "\t\tIf no option is selected the script will create the new MySQL databases, " \
          "username and passwords for each deployed kippo sensor"


def sanitizeString(string):
    return string.replace('-', '_')


def getMongoKippoData():
    """Function to connect to the mongodb and retrieve the kippo sensor identifiers and secrets"""
    try:
        client = pymongo.MongoClient('mongodb://' + conf.MONGO_HOST + ':' + str(conf.MONGO_PORT))
    except pymongo.errors.ConnectionFailure:
        print ('Error Connecting to the database...')
        print ('Check the kippo_update_config file to change the configuration...')
        sys.exit(1)
    db = client.hpfeeds
    auth_keys = db.auth_key
    return auth_keys.find({"publish": ["kippo.sessions"]}, {"identifier": 1, "secret": 1, "_id": 0})


def getSensorIP(ident):
    """Function to get the ip address of the sensor from sqlite3 db"""
    try:
        conn = sqlite3.connect(conf.SQLITE_DB)
    except sqlite3.OperationalError as e:
        print e
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(*) FROM sensors WHERE uuid = '%s'" % ident
    cur.execute(sql)
    if cur.fetchone()[0] != 0:
        sql = "SELECT ip FROM sensors WHERE uuid = '%s'" % ident
        cur.execute(sql)
        conn.commit()
        ip = cur.fetchone()[0]
        conn.close()
        return ip
    else:
        conn.close()
        print 'The sensor was not found on mhn.db and the ip address could not be determined...'
        sys.exit(1)


def getMySQLKippoData():
    """Function to connect to the MySQL db and retrieve the kippo databases already created"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SHOW DATABASES"
    cur.execute(sql)
    kippoDbs = []
    for (db,) in cur:
        if db.startswith('kippo'):
            kippoDbs.append(db)
    cur.close()
    conn.close()
    return kippoDbs


def createKippoDb(db, pwd, ipAddr):
    """Function to create the Kippo Database, the username and password"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "CREATE DATABASE IF NOT EXISTS %s" % db
    cur.execute(sql)
    sql = "CREATE USER 'kippo'@'%s' IDENTIFIED BY '%s'" % (ipAddr, pwd)
    cur.execute(sql)
    sql = "GRANT ALL ON %s.* TO 'kippo'@'%s' IDENTIFIED BY '%s'" % (db, ipAddr, pwd)
    cur.execute(sql)
    sql = "FLUSH PRIVILEGES"
    cur.execute(sql)
    cur.close()
    conn.close()
    createKippoTables(db)


def createKippoTables(database):
    """Function to create the tables on the Kippo Databases"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    f = open(conf.KIPPO_SQL, 'r')
    sql = ''
    for line in f:
        if not line.endswith(';\n'):
            sql = sql + line[:-1]
        else:
            sql = sql + line[:-2]
            cur.execute(sql)
            sql = ''
    cur.close()
    conn.close()


def dropMySQLDb(database):
    """Function to drop Kippo Databases that are no longer used"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = 'DROP DATABASE %s' % database
    cur.execute(sql)
    cur.close()
    conn.close()


def dropMySQLUser(ip):
    """Function to drop Kippo Users that are no longer used"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "DROP USER 'kippo'@'%s'" % ip
    cur.execute(sql)
    cur.close()
    conn.close()


def getMySQLKippoUsers():
    """Get the kippo users configured on MySQL"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(*) FROM mysql.user WHERE User = 'kippo'"
    cur.execute(sql)
    if cur.fetchone()[0] != 0:
        sql = "SELECT Host FROM mysql.user WHERE User = 'kippo'"
        cur.execute(sql)
        userCreated = []
        for (host,) in cur.fetchall():
            userCreated.append(host)
        cur.close()
        conn.close()
        return userCreated
    else:
        cur.close()
        conn.close()
        print "There are no kippo Users configured on MySQL"
        sys.exit(1)


def getHostsSQLite():
    """Function to get all the ip address of the sensor from sqlite3 db"""
    try:
        conn = sqlite3.connect(conf.SQLITE_DB)
    except sqlite3.OperationalError as e:
        print e
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(*) FROM sensors WHERE honeypot = 'kippo'"
    cur.execute(sql)
    sensorsRegistered = []
    if cur.fetchone()[0] != 0:
        sql = "SELECT ip FROM sensors WHERE honeypot = 'kippo'"
        cur.execute(sql)
        conn.commit()
        for (ip,) in cur.fetchall():
            sensorsRegistered.append(ip)
        conn.close()
        return sensorsRegistered
    else:
        conn.close()
        print 'There are not kippo sensors on mhn.db.'
        return sensorsRegistered


def cleanMySQLDb():
    """Function to clean the Kippo Database, the username and password"""
    kippoSensorReg = getMongoKippoData()
    kippoDbReg = []
    for sensor in kippoSensorReg:
        kippoDbReg.append(sanitizeString('kippo-' + sensor['identifier']))
    kippoDbCreated = getMySQLKippoData()
    for database in kippoDbCreated:
        if database not in kippoDbReg:
            dropMySQLDb(database)
            print "MySQL Database %s was dropped." % database
    usersOnMySQL = getMySQLKippoUsers()
    activeSensors = getHostsSQLite()
    usersToDel = list(set(usersOnMySQL) - set(activeSensors))
    for host in usersToDel:
        dropMySQLUser(host)
        print "MySQL User kippo@%s dropped" % host


def main():
    """Main Function"""
    if len(sys.argv) == 1:
        kippoSensorReg = getMongoKippoData()
        kippoDbCreated = getMySQLKippoData()
        for sensor in kippoSensorReg:
            if sanitizeString('kippo-' + sensor['identifier']) not in kippoDbCreated:
                ipAddr = getSensorIP(sensor['identifier'])
                database = sanitizeString('kippo-' + sensor['identifier'])
                password = sensor['secret']
                createKippoDb(database, password, ipAddr)
                print 'Created MySQL DB named %s' % database
                print 'Created a username kippo with a password %s and granted permissions from host %s' % (password, ipAddr)
            else:
                print 'MySQL DB named %s already exists!!!' % sanitizeString('kippo-' + sensor['identifier'])
    elif len(sys.argv) == 2:
        if sys.argv[1] == '-h':
            usage()
        elif sys.argv[1].lower() == 'clean':
            cleanMySQLDb()
    else:
        usage()


if __name__ == "__main__":
    main()


__author__ = 'mercolino'
