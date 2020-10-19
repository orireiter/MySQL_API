from pyTools.MySQL_Class.MySQL_Class import MSQL
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, fix_json_quotings
import json

is_rabbit_up, is_mysql_up, is_conf_up = False, False, False
print("POST consumer awaiting config")
while is_conf_up is False:
    try:
        confer = get_conf(['DBs'])
        is_conf_up = True
    except:
        pass
print("POST consumer awaiting connection to RabbitMQ")
while is_rabbit_up is False:
    try:
        rab = Rabbit(host=get_conf(['RabbitMQ', 'host']))
        is_rabbit_up = True
        rab.close_connection()
    except:
        pass
print("POST consumer awaiting connection to MySQL")
while is_mysql_up is False:
    try:
        mas = conn = MSQL(get_conf(['mysql_cred','host']),
                get_conf(['mysql_cred','user']),
                str(get_conf(['mysql_cred','password'])))
        is_mysql_up = True
        dbs =  get_conf(['DBs'])
        for db in dbs:
            conn.create_db(db)
            print(db + " db initialized")
            tables = get_conf(['DBs', db, 'tables'])
            for table in tables:
                conn.create_table(table, get_conf(['DBs', db, 'tables', table]))
                print(table + " table initialized")
    except:
        pass

consumer = Rabbit(host=get_conf(['RabbitMQ', 'host']))
consumer.declare_queue(get_conf(['RabbitMQ', 'queues', 'post_queue']),durable=True)

def poster(msg):
    msg_as_str = msg.decode('utf-8')    
    msg_as_dict = fix_json_quotings(msg_as_str)
    
    try:
        conn = MSQL(get_conf(['DBs',msg_as_dict['db'],'db_cred','host']),
                get_conf(['DBs',msg_as_dict['db'],'db_cred','user']),
                str(get_conf(['DBs',msg_as_dict['db'],'db_cred','password'])),
                msg_as_dict['db'])
    except:
        return("ERROR: couldn't connect with given credentials")
    msg_as_dict.pop('db')
    table = msg_as_dict.pop('table')
    
    record = conn.insert_record(table, tuple(msg_as_dict.keys()), tuple(msg_as_dict.values()))
    return(record)

consumer.receive_n_send_many(get_conf(['RabbitMQ', 'queues', 'post_queue']), poster)