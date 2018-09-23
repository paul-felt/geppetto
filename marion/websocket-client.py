#!/usr/bin/python
from websocket import create_connection
ws = create_connection("ws://localhost:8080/websocket")
print "Sending 'Hello, World'..."
ws.send("Hello, world")
print "Sent"
print "Receiving.."
result = ws.recv()
print "Received '%s'" % result
ws.close()
