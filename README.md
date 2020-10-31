Made by Ori Reiter

This is a simple web api to query a db through http request to avoid having it open to public, and also automating the querying process.
The best use case is cd-ing into the docker-compose directory and configuring it as wished,
and then using -> docker-compose up.
When doing so, all the containers will use the same config, minimizing the chance of problems.

Fast use explanation:
---------------------
1. cd into docker-compose directory
2. configure config.json:
This file is responsible for the nginx/flask app, and the only thing you might want to change there is the processes amount.
3. configure config.yml:
This file is used practically by all the containers. Take to the time to look at this example file to understand how the containers expect to recieve this config file. Put the DBs and tables you will use, as well as the columns these table will have and relevant credentials.
Also put the queues' names.
4. Put the password you want the mysql server to initialized with in the .env file.
5. From the docker-compose directory execute the command -> docker-compose up
6. Try using POSTMAN to send HTTP requests.
NOTES:
1. Make sure the pass in the .env matches thise in the config.yml, otherwise make sure you configured everything correctly.
2. I still haven't secured or encrypted any part of this project.

Architecture:
-------------
1. Nginx UNIT server, serving a Flask app that handles GET,POST,PUT,DELETE requests meant to query a database.
   These requests are processed and sent to a messaging queue.
2. RabbitMQ server - a messaging queue that receives messages and sends them to relevant cosnumers.
3. Consumers that consume from their configured queue and query the DB according to the info they received from the rabbit server (which is the info sent to the flask server, usually through a json).
They then return either the record ID or the result of a query as a sign of success.
4. MySQL server - a database.

