from pyTools.MySQL_Class.MySQL_Class import MSQL
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, fix_json_quotings

consumer = Rabbit(host=get_conf(['RabbitMQ', 'host']))
consumer.declare_queue(get_conf(['RabbitMQ', 'queues', 'delete_queue']),durable=True)

def deleter(msg):
    msg_as_str = msg.decode('utf-8')    
    msg_as_dict = fix_json_quotings(msg_as_str)
    
    try:
        conn = MSQL(get_conf(['DBs',msg_as_dict['db'],'db_cred','host']),
                get_conf(['DBs',msg_as_dict['db'],'db_cred','user']),
                str(get_conf(['DBs',msg_as_dict['db'],'db_cred','password'])),
                msg_as_dict['db'])
    except:
        return("ERROR: couldn't connect with given credentials")

    result = conn.delete_record(msg_as_dict['table'],msg_as_dict['record_id'])
    return(result)

consumer.receive_n_send_many(get_conf(['RabbitMQ', 'queues', 'delete_queue']), deleter)