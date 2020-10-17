from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf
from flask import Flask, request

app = Flask(__name__)
rabbit = Rabbit(get_conf(['RabbitMQ', 'host']))
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'post_queue']),durable=True)
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'get_queue']),durable=True)
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'put_queue']),durable=True)
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'delete_queue']),durable=True)


@app.route('/<string:db>/<string:table>', methods=['POST'])
def post(db, table):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration")
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration")
    else:
        try:
            body = request.get_json()
        except: 
            return("ERROR: To post a record, you must send it in a JSON")
        body['db'] = db
        body['table'] = table
        result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'post_queue']), body)
        return(result)


@app.route('/<string:db>/<string:table>', methods=['GET'])
@app.route('/<string:db>/<string:table>/<string:record_id>', methods=['GET'])
def get(db, table, record_id=None):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration")
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration")
    else:
        if record_id == None:
            try:
                body = request.get_json()
            except: 
                return("ERROR: To post a record, you must send it in a JSON")

            body['db'] = db
            body['table'] = table
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'get_queue']), body)
            return(result)

        else:
            body = {"record_id": record_id, "db": db, "table": table}
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'get_queue']), body)
            return(result)


@app.route('/<string:db>/<string:table>/<string:record_id>', methods=['PUT'])
def put(db, table, record_id):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration")
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration")
    else:
        if record_id == None:
            return("ERROR: no record id specified in the url")
        else:
            try:
                body = request.get_json()
            except: 
                return("ERROR: To put a record, you must send it in a JSON")
            
            body['db'] = db
            body['table'] = table
            body["record_id"] = record_id
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'put_queue']), body)
            return(result)


@app.route('/<string:db>/<string:table>/<string:record_id>', methods=['DELETE'])
def delete(db, table, record_id):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration")
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration")
    else:
        if record_id == None:
            return("ERROR: no record id specified in the url")
        else:
            body = {"record_id": record_id, "db": db, "table": table}
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'delete_queue']), body)
            return(result)


app.run(debug=True)