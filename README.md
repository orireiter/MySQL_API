Made by Ori Reiter

This is a simple web api to query a db through http request to avoid having it open to public, and also automating the querying process.
The best use case is cd-ing into the docker-compose directory and configuring it as wished,
and then using -> docker-compose up.
When doing so, all the containers will use the same config, minimizing the chance of problems.

Architecture:
-------------
1) Nginx UNIT server, serving a Flask app that handles GET,POST,PUT,DELETE requests meant to query a database.
   These requests are processed and sent to a messaging queue.
2) RabbitMQ server - a messaging queue that receives messages and sends them to relevant cosnumers.
3) Consumers that consume from their configured queue and query the DB according to the info they received from the rabbit server (which is the info sent to the flask server, usually through a json).
They then return either the record ID or the result of a query as a sign of success.
4) MySQL server - a database.

