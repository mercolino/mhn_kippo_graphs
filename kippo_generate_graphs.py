import kippo_update_config as conf
import matplotlib.pyplot as plt
import pymysql
import sys
import pwd
import grp
import os


def noGraphGenerated(name):
    try:
        from PIL import Image, ImageDraw, ImageFont

        drawWidth = 8 * conf.KIPPO_GRAPH_RES
        drawHeight = 6 * conf.KIPPO_GRAPH_RES
        img = Image.new('RGB', (drawWidth, drawHeight), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(conf.KIPPO_FONT, conf.KIPPO_FONT_SIZE)
        textWidth, textHeight = draw.textsize('No Data Available', font)
        draw.text(((drawWidth/2) - (textWidth/2), (drawHeight/2) - (textHeight/2)), "No Data Available", (0, 0, 0), font=font)
        img.save(conf.KIPPO_GRAPH_PATH + name + '_th' + '.' + conf.KIPPO_GRAPH_FORMAT)
        img.save(conf.KIPPO_GRAPH_PATH + name + '.' + conf.KIPPO_GRAPH_FORMAT)
        os.chown(conf.KIPPO_GRAPH_PATH + name + '.' + conf.KIPPO_GRAPH_FORMAT, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)
        os.chown(conf.KIPPO_GRAPH_PATH + name + '_th' + '.' + conf.KIPPO_GRAPH_FORMAT, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)
    except:
        print 'No enough data to generate the graph %s but no file generated because PIL Library was not found' % name


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


def autolabel(rects):
    """Function to generate the data labels in the Bar Charts"""
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2., height*1.05, '%d' % int(height), ha='center', va='bottom', rotation=50)


def generateBarGraph(x, y, title, graphName):
    """Function to generate the Bar Graphs with matplotlib"""
    plt.style.use(conf.KIPPO_STYLE)
    plt.title(title)
    rects = plt.bar(range(len(x)), y, align='center')
    plt.xticks(range(len(x)), x, rotation=50, size='small', ha='right')
    plt.axes().set_ylim([0, max(y)*1.2])
    plt.axes().yaxis.grid(True, lw=1, ls='--', c='.75')
    autolabel(rects)
    #plt.show()
    plt.savefig(conf.KIPPO_GRAPH_PATH + graphName + '.' + conf.KIPPO_GRAPH_FORMAT,
                dpi=conf.KIPPO_GRAPH_RES,
                format=conf.KIPPO_GRAPH_FORMAT,
                bbox_inches='tight')
    plt.savefig(conf.KIPPO_GRAPH_PATH + graphName + '_th' + '.' + conf.KIPPO_GRAPH_FORMAT,
                dpi=conf.KIPPO_GRAPH_RES/conf.KIPPO_THUMB_FACTOR,
                format=conf.KIPPO_GRAPH_FORMAT,
                bbox_inches='tight')
    os.chown(conf.KIPPO_GRAPH_PATH + graphName + '_th' + '.' + conf.KIPPO_GRAPH_FORMAT, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)
    os.chown(conf.KIPPO_GRAPH_PATH + graphName + '.' + conf.KIPPO_GRAPH_FORMAT, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)
    plt.clf()


def generateLineGraph(x, y, title, graphName):
    """Function to generate the Line Graphs with matplotlib"""
    plt.style.use(conf.KIPPO_STYLE)
    plt.title(title)
    plt.plot(range(len(x)), y, marker='o', markersize=5)
    plt.xticks(range(len(x)), x, rotation=50, size='small', ha='right')
    plt.axes().set_ylim([0, max(y)*1.2])
    plt.axes().yaxis.grid(True, lw=1, ls='--', c='.75')
    plt.axes().xaxis.grid(True, lw=1, ls='--', c='.75')
    #plt.show()
    plt.savefig(conf.KIPPO_GRAPH_PATH + graphName + '.' + conf.KIPPO_GRAPH_FORMAT,
                dpi=conf.KIPPO_GRAPH_RES,
                format=conf.KIPPO_GRAPH_FORMAT,
                bbox_inches='tight')
    plt.savefig(conf.KIPPO_GRAPH_PATH + graphName + '_th' + '.' + conf.KIPPO_GRAPH_FORMAT,
                dpi=conf.KIPPO_GRAPH_RES/conf.KIPPO_THUMB_FACTOR,
                format=conf.KIPPO_GRAPH_FORMAT,
                bbox_inches='tight')
    os.chown(conf.KIPPO_GRAPH_PATH + graphName + '_th' + '.' + conf.KIPPO_GRAPH_FORMAT, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)
    os.chown(conf.KIPPO_GRAPH_PATH + graphName + '.' + conf.KIPPO_GRAPH_FORMAT, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)
    plt.clf()


def generateTop10Passwords(database):
    """Generate the Top 10 Password from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT password, COUNT(password) " \
          "FROM auth " \
          "WHERE password <> '' " \
          "GROUP BY password " \
          "ORDER BY COUNT(password) " \
          "DESC LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        password = []
        countPassword = []
        for (pwd, countPwd) in cur.fetchall():
            password.append(pwd)
            countPassword.append(countPwd)
        cur.close()
        conn.close()
        title = 'Top 10 Passwords Attempted'
        generateBarGraph(password, countPassword, title, 'top_10_passwords_' + database)
    else:
        noGraphGenerated('top_10_passwords_' + database)


def generateTop10Usernames(database):
    """Generate the Top 10 Usernames from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT username, COUNT(username) " \
          "FROM auth " \
          "WHERE username <> '' " \
          "GROUP BY username " \
          "ORDER BY COUNT(username) " \
          "DESC LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        username = []
        countUsername = []
        for (user, countUser) in cur.fetchall():
            username.append(user)
            countUsername.append(countUser)
        cur.close()
        conn.close()
        title = 'Top 10 Usernames Attempted'
        generateBarGraph(username, countUsername, title, 'top_10_usernames_' + database)
    else:
        noGraphGenerated('top_10_usernames_' + database)


def generateTop10Combinations(database):
    """Generate the Top 10 Usernames-Password Combinations from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT username, password, COUNT(username) " \
          "FROM auth " \
          "WHERE username <> '' AND password <> '' " \
          "GROUP BY username, password " \
          "ORDER BY COUNT(username) " \
          "DESC LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        combination = []
        countCombination = []
        for (user, pwd, countComb) in cur.fetchall():
            combination.append(user + '/' + pwd)
            countCombination.append(countComb)
        cur.close()
        conn.close()
        title = 'Top 10 Username-Password Combinations'
        generateBarGraph(combination, countCombination, title, 'top_10_combinations_' + database)
    else:
        noGraphGenerated('top_10_combinations_' + database)


def generateSuccessRatio(database):
    """Generate the Authentication Success Ratio from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT success, COUNT(success) " \
          "FROM auth " \
          "GROUP BY success " \
          "ORDER BY success"
    cur.execute(sql)
    if cur.rowcount != 0:
        countSuccess = []
        Success=[]
        for (success, countSuc) in cur.fetchall():
            if success == 0:
                Success.append('Failure')
            elif success == 1:
                Success.append('Success')
            countSuccess.append(countSuc)
        cur.close()
        conn.close()
        title = 'Overall Success Ratio'
        generateBarGraph(Success, countSuccess, title, 'success_ratio_' + database)
    else:
        noGraphGenerated('success_ratio_' + database)


def generateNumberOfConnectionsPerIP(database):
    """Generate the Number of Connections per IP from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT ip, COUNT(ip) " \
          "FROM sessions " \
          "GROUP BY ip " \
          "ORDER BY COUNT(ip) DESC " \
          "LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        ip = []
        countIp = []
        for (ipAddr, countIpAddr) in cur.fetchall():
            ip.append(ipAddr)
            countIp.append(countIpAddr)
        cur.close()
        conn.close()
        title = 'Number of Connections per Unique IP (Top 10)'
        generateBarGraph(ip, countIp, title, 'number_connections_per_ip_' + database)
    else:
        noGraphGenerated('number_connections_per_ip_' + database)


def generateSuccessfulLoginsFromSameIP(database):
    """Generate the Successful Logins from same IP from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT sessions.ip, COUNT(sessions.ip) " \
          "FROM sessions INNER JOIN auth ON sessions.id = auth.session " \
          "WHERE auth.success = 1 " \
          "GROUP BY sessions.ip " \
          "ORDER BY COUNT(sessions.ip) DESC " \
          "LIMIT 20"
    cur.execute(sql)
    if cur.rowcount != 0:
        ip = []
        countSessionsIp = []
        for (ipAddr, countSessIpAddr) in cur.fetchall():
            ip.append(ipAddr)
            countSessionsIp.append(countSessIpAddr)
        cur.close()
        conn.close()
        title = 'Successful Logins from Same IP (Top 20)'
        generateBarGraph(ip, countSessionsIp, title, 'successful_logins_from_same_ip_' + database)
    else:
        noGraphGenerated('successful_logins_from_same_ip_' + database)


def generateTop10SSHClients(database):
    """Generate the Top 10 SSH Clients used to connect from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT clients.version, COUNT(client) " \
          "FROM sessions INNER JOIN clients ON sessions.client = clients.id " \
          "GROUP BY sessions.client " \
          "ORDER BY COUNT(client) DESC " \
          "LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        version = []
        countVersion = []
        for (ver, countVer) in cur.fetchall():
            version.append(ver)
            countVersion.append(countVer)
        cur.close()
        conn.close()
        title = 'Top 10 SSH Clients'
        generateBarGraph(version, countVersion, title, 'top_10_ssh_clients_' + database)
    else:
        noGraphGenerated('top_10_ssh_clients_' + database)


def generateTop10OverallInput(database):
    """Generate the Top 10 Overall Input commands issued in the sensor from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT input, COUNT(input) " \
          "FROM input " \
          "GROUP BY input " \
          "ORDER BY COUNT(input) DESC " \
          "LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        input = []
        countInput = []
        for (inp, countInp) in cur.fetchall():
            input.append(inp)
            countInput.append(countInp)
        cur.close()
        conn.close()
        title = 'Top 10 Input (Overall)'
        generateBarGraph(input, countInput, title, 'top_10_overall_input_' + database)
    else:
        noGraphGenerated('top_10_overall_input_' + database)


def generateTop10SuccessfulInput(database):
    """Generate the Top 10 Successful Input commands issued in the sensor from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT input, COUNT(input) " \
          "FROM input " \
          "WHERE success = 1 " \
          "GROUP BY input " \
          "ORDER BY COUNT(input) DESC " \
          "LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        input = []
        countInput = []
        for (inp, countInp) in cur.fetchall():
            input.append(inp)
            countInput.append(countInp)
        cur.close()
        conn.close()
        title = 'Top 10 Successful Input'
        generateBarGraph(input, countInput, title, 'top_10_successful_input_' + database)
    else:
        noGraphGenerated('top_10_successful_input_' + database)


def generateTop10FailedInput(database):
    """Generate the Top 10 Failed Input commands issued in the sensor from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT input, COUNT(input) " \
          "FROM input " \
          "WHERE success = 0 " \
          "GROUP BY input " \
          "ORDER BY COUNT(input) DESC " \
          "LIMIT 10"
    cur.execute(sql)
    if cur.rowcount != 0:
        input = []
        countInput = []
        for (inp, countInp) in cur.fetchall():
            input.append(inp)
            countInput.append(countInp)
        cur.close()
        conn.close()
        title = 'Top 10 Successful Input'
        generateBarGraph(input, countInput, title, 'top_10_failed_input_' + database)
    else:
        noGraphGenerated('top_10_failed_input_' + database)


def generateMostSuccessfulLoginsPerDay(database):
    """Generate the Top 20 most successful logins per day from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT timestamp, COUNT(session) " \
          "FROM auth " \
          "WHERE success = 1 " \
          "GROUP BY DAYOFYEAR(timestamp) " \
          "ORDER BY COUNT(session) DESC " \
          "LIMIT 20"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (dt, countSess) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Most Successful Logins per day (Top 20)'
        generateBarGraph(timestamp, countSession, title, 'most_successful_logins_per_day_' + database)
    else:
        noGraphGenerated('most_successful_logins_per_day_' + database)


def generateSuccessesPerDay(database):
    """Generate the Successes per day from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT timestamp, COUNT(session) " \
          "FROM auth " \
          "WHERE success = 1 " \
          "GROUP BY DAYOFYEAR(timestamp) " \
          "ORDER BY timestamp ASC"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (dt, countSess) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Successes per day'
        generateLineGraph(timestamp, countSession, title, 'successes_per_day_' + database)
    else:
        noGraphGenerated('successes_per_day_' + database)


def generateSuccessesPerWeek(database):
    """Generate the Successes per Week from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(session), " \
          "MAKEDATE(CASE WHEN WEEKOFYEAR(timestamp) = 52 " \
          "THEN YEAR(timestamp)-1 " \
          "ELSE YEAR(timestamp) " \
          "END, (WEEKOFYEAR(timestamp) * 7)-4) AS DateOfWeek_Value " \
          "FROM auth " \
          "WHERE success = 1 " \
          "GROUP BY WEEKOFYEAR(timestamp) " \
          "ORDER BY timestamp ASC"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Successes per Week'
        generateLineGraph(timestamp, countSession, title, 'successes_per_week_' + database)
    else:
        noGraphGenerated('successes_per_week_' + database)


def generateMostProbesPerDay(database):
    """Generate the Top 20 most probes per day from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(session), timestamp " \
          "FROM auth " \
          "GROUP BY DAYOFYEAR(timestamp) " \
          "ORDER BY COUNT(session) DESC " \
          "LIMIT 20"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Most Probes per day (Top 20)'
        generateBarGraph(timestamp, countSession, title, 'most_probes_per_day_' + database)
    else:
        noGraphGenerated('most_probes_per_day_' + database)


def generateProbesPerDay(database):
    """Generate the Probes per day from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(session), timestamp " \
          "FROM auth " \
          "GROUP BY DAYOFYEAR(timestamp) " \
          "ORDER BY timestamp ASC"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Probes per day'
        generateLineGraph(timestamp, countSession, title, 'probes_per_day_' + database)
    else:
        noGraphGenerated('probes_per_day_' + database)


def generateProbesPerWeek(database):
    """Generate the Probes per Week from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(session), " \
          "MAKEDATE(CASE WHEN WEEKOFYEAR(timestamp) = 52 " \
          "THEN YEAR(timestamp)-1 " \
          "ELSE YEAR(timestamp) " \
          "END, (WEEKOFYEAR(timestamp) * 7)-4) AS DateOfWeek_Value " \
          "FROM auth " \
          "GROUP BY WEEKOFYEAR(timestamp) " \
          "ORDER BY timestamp ASC"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Probes per Week'
        generateLineGraph(timestamp, countSession, title, 'probes_per_week_' + database)
    else:
        noGraphGenerated('probes_per_week_' + database)


def generateHumanActivityBusiestDays(database):
    """Generate the Top 20 days with most human activity from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(input), timestamp " \
          "FROM input " \
          "GROUP BY DAYOFYEAR(timestamp) " \
          "ORDER BY COUNT(input) DESC " \
          "LIMIT 20"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Human Activity busiest days (Top 20)'
        generateBarGraph(timestamp, countSession, title, 'human_activity_busiest_days_' + database)
    else:
        noGraphGenerated('human_activity_busiest_days_' + database)


def generateHumanActivityPerDay(database):
    """Generate the Human Activity per day from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(input), timestamp " \
          "FROM input " \
          "GROUP BY DAYOFYEAR(timestamp) " \
          "ORDER BY timestamp ASC"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Human Activity per day'
        generateLineGraph(timestamp, countSession, title, 'human_activity_per_day_' + database)
    else:
        noGraphGenerated('human_activity_per_day_' + database)


def generateHumanActivityPerWeek(database):
    """Generate the Human activity per Week from the MySQL Database"""
    try:
        conn = pymysql.connect(host=conf.MYSQL_HOST, port=conf.MYSQL_PORT, user=conf.MYSQL_USER, passwd=conf.MYSQL_PWD, db=database)
    except pymysql.MySQLError as e:
        print e.args[1]
        sys.exit(1)
    cur = conn.cursor()
    sql = "SELECT COUNT(input), " \
          "MAKEDATE( CASE WHEN WEEKOFYEAR(timestamp) = 52 " \
          "THEN YEAR(timestamp)-1 " \
          "ELSE YEAR(timestamp) END, (WEEKOFYEAR(timestamp) * 7)-4) AS DateOfWeek_Value " \
          "FROM input " \
          "GROUP BY WEEKOFYEAR(timestamp) " \
          "ORDER BY timestamp ASC"
    cur.execute(sql)
    if cur.rowcount != 0:
        timestamp = []
        countSession = []
        for (countSess, dt) in cur.fetchall():
            timestamp.append(dt.strftime('%m-%d-%Y'))
            countSession.append(countSess)
        cur.close()
        conn.close()
        title = 'Human Activity per Week'
        generateLineGraph(timestamp, countSession, title, 'human_activity_per_week_' + database)
    else:
        noGraphGenerated('human_activity_per_week_' + database)


def main():
    """Main Function"""
    kippoDbs = getMySQLKippoData()
    for db in kippoDbs:
        generateTop10Passwords(db)
        generateTop10Usernames(db)
        generateTop10Combinations(db)
        generateSuccessRatio(db)
        generateNumberOfConnectionsPerIP(db)
        generateSuccessfulLoginsFromSameIP(db)
        generateTop10SSHClients(db)
        generateTop10OverallInput(db)
        generateTop10SuccessfulInput(db)
        generateTop10FailedInput(db)
        generateMostSuccessfulLoginsPerDay(db)
        generateSuccessesPerDay(db)
        generateSuccessesPerWeek(db)
        generateMostProbesPerDay(db)
        generateProbesPerDay(db)
        generateProbesPerWeek(db)
        generateHumanActivityBusiestDays(db)
        generateHumanActivityPerDay(db)
        generateHumanActivityPerWeek(db)


if __name__ == "__main__":
    main()

__author__ = 'mercolino'
