from pyTools.MySQL_Class.MySQL_Class import MSQL
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, fix_json_quotings, list_of_tuples_to_list_of_lists

# Upon execution, first wait until it can find the config, 
# and can connect to the rabbit server and mysql server.
# When first connecting to mysql, it will try to initialize the databases and
# tables in the config.
is_rabbit_up, is_mysql_up, is_conf_up = False, False, False
print("GET consumer awaiting config")
while is_conf_up is False:
    try:
        confer = get_conf(['DBs'])
        is_conf_up = True
    except:
        pass
print("GET consumer awaiting connection to RabbitMQ")
while is_rabbit_up is False:
    try:
        rab = Rabbit(host=get_conf(['RabbitMQ', 'host']))
        is_rabbit_up = True
        rab.close_connection()
    except:
        pass
print("GET consumer awaiting connection to MySQL")
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

# After initializing a rabbit object and declare the queue it will consume from.
consumer = Rabbit(host=get_conf(['RabbitMQ', 'host']))
consumer.declare_queue(get_conf(['RabbitMQ', 'queues', 'get_queue']),durable=True)

# The function that will be executed when a message is consumed.
# It will transform the stringed message from rabbit into a dictionary
# for ease of use and then use the info in it to try and create/delete/update/query from the db.
def getter(msg):
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

    if 'record_id' in msg_as_dict:
        result = conn.find_record(table,msg_as_dict['record_id'])
    elif len(msg_as_dict)==0:
        result = conn.find_all_records(table)
        result = list_of_tuples_to_list_of_lists(result)
    else:
        column =  str(list(msg_as_dict.keys())[0])
        value = str(list(msg_as_dict.values())[0])
        result = conn.find_records(table, column, value)
        print(result)
        if type(result) == type(['list','list']):
            result = list_of_tuples_to_list_of_lists(result)
        else:
            pass
    return(result)

# This function starts listening to the given rabbit queue, 
# and executes the function above upon message consumption, with 
# the message as a parameter.
consumer.receive_n_send_many(get_conf(['RabbitMQ', 'queues', 'get_queue']), getter)