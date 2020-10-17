from pyTools.extra_tools import get_conf
from pyTools.MySQL_Class.MySQL_Class import MSQL


conn = MSQL(get_conf(['mysql_cred','host']),get_conf(['mysql_cred','user']),str(get_conf(['mysql_cred','password'])))

dbs =  get_conf(['DBs'])
for db in dbs:
    conn.create_db(db)
    print(db + " db initialized")
    tables = get_conf(['DBs', db, 'tables'])
    for table in tables:
        conn.create_table(table, get_conf(['DBs', db, 'tables', table]))
        print(table + " table initialized")