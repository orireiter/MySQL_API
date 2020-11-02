from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, fix_json_quotings
from flask import Flask, request, jsonify
import json

# Upon execution, first wait until it can find the config, 
# and can connect to the rabbit server.
is_rabbit_up, is_conf_up = False, False
print("Web API awaiting config")
while is_conf_up is False:
    try:
        confer = get_conf(['DBs'])
        is_conf_up = True
    except:
        pass
print("Web API awaiting connection to RabbitMQ")
while is_rabbit_up is False:
    try:
        rab = Rabbit(host=get_conf(['RabbitMQ', 'host']))
        is_rabbit_up = True
        rab.close_connection()
    except:
        pass

# Initialize the flask server and rabbit object
app = Flask(__name__)
rabbit = Rabbit(get_conf(['RabbitMQ', 'host']))
# Declare the queues the the server is going to send messages to.
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'post_queue']),durable=True)
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'get_queue']),durable=True)
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'put_queue']),durable=True)
rabbit.declare_queue(get_conf(['RabbitMQ', 'queues', 'delete_queue']),durable=True)

'''
    All the routes and requests require a database name and a table name.
    Otherwise you'll get a "page not found" error.
    Upon receiving a request, the server will first compare the db and table to the config file,
    so make sure to put all of the relevant info there!
    Then, depending if the method requires a db record id, the server will look for a JSON containing
    the info to post/get/update (and will look for an id in the url if needed).
    The server will then stringify the the info supplied and send it to the relevant rabbit queue,
    while waiting for an answer.
    A GET request willbe answered with the result of the query.
    The other requests (POST,DELETE,PUT) will be answered with the relevant record ID as a sign of success.
'''
@app.route('/<string:db>/<string:table>', methods=['POST'])
def post(db, table):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration"), 400
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration"), 400
    else:
        try:
            body = request.get_json()
            if len(body) == 0:
                return("ERROR: To post a record, you must send it in a JSON"), 400    
        except: 
            return("ERROR: To post a record, you must send it in a JSON"), 400
        body['db'] = db
        body['table'] = table
        result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'post_queue']), body)
        if result.startswith('b"ERROR') == True:
            return result, 400
        else:
            result = result.replace('b"','')
            result = result.replace('"','')
            result = fix_json_quotings(result)
            return jsonify(result)


@app.route('/<string:db>/<string:table>', methods=['GET'])
@app.route('/<string:db>/<string:table>/<string:record_id>', methods=['GET'])
def get(db, table, record_id=None):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration"), 400
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration"), 400
    else:
        if record_id == None:
            try:
                body = request.get_json()
                if body == None:
                   return("ERROR: To get a record not by id, you must send it in a JSON"), 400 
            except: 
                return("ERROR: To get a record not by id, you must send it in a JSON"), 400

            body['db'] = db
            body['table'] = table
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'get_queue']), body)
            
            if result.startswith('b"ERROR') == True:
                return result, 400
            # ie if the query found zero results
            elif result == "b'[]'":
                return jsonify([])
            else:
                result = result.replace('b"','').replace('"','').replace('None', '"None"')
                result = fix_json_quotings(result)
                return jsonify(result)

        else:
            body = {"record_id": record_id, "db": db, "table": table}
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'get_queue']), body)
            
            if result.startswith('b"ERROR') == True:
                return result, 400
            else:
                result = result.replace('b"','').replace('"','').replace('None', '"None"')
                result = fix_json_quotings(result)
                return jsonify(result)


@app.route('/<string:db>/<string:table>/<string:record_id>', methods=['PUT'])
def put(db, table, record_id):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration"), 400
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration"), 400
    else:
        if record_id == None:
            return("ERROR: no record id specified in the url"), 400
        else:
            try:
                body = request.get_json()
                if body == None:
                    return("ERROR: To put a record, you must send it in a JSON"), 400    
            except: 
                return("ERROR: To put a record, you must send it in a JSON"), 400
            
            body['db'] = db
            body['table'] = table
            body["record_id"] = record_id
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'put_queue']), body)
            if result.startswith('b"ERROR') == True:
                return result, 400
            else:
                result = result.replace('b"','')
                result = result.replace('"','')
                result = fix_json_quotings(result)
                return jsonify(result)


@app.route('/<string:db>/<string:table>/<string:record_id>', methods=['DELETE'])
def delete(db, table, record_id):
    if db not in get_conf(['DBs']):
        return("ERROR: db given not specified in the configuration"), 400
    elif table not in get_conf(['DBs', db, 'tables']):
        return("ERROR: table given not specified in the configuration"), 400
    else:
        if record_id == None:
            return("ERROR: no record id specified in the url"), 400
        else:
            body = {"record_id": record_id, "db": db, "table": table}
            result = rabbit.send_n_receive(get_conf(['RabbitMQ', 'queues', 'delete_queue']), body)
            
            if result.startswith('b"ERROR') == True:
                return result, 400
            else:
                result = result.replace('b"','')
                result = result.replace('"','')
                result = fix_json_quotings(result)
                return jsonify(result)
