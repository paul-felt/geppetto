from gevent import monkey
monkey.patch_all()

import time
import cgi
import redis
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
#db = redis.StrictRedis('localhost', 6379, 0)
socketio = SocketIO(app)

__version__ = "0.0.1"

#@app.route('/')
#def main():
#    return "hi world"

#@socketio.on('connect', namespace='/geppetto')
#def ws_conn():
#    c = db.incr('connected')
#    socketio.emit('msg', {'count': c}, namespace='/geppetto')

@socketio.on('connect')
def ws_conn():
    print 'connected'
    socketio.emit('msg', {'version': __version__})

@socketio.on('disconnect')
def ws_disconn():
    print 'disconnected'
    socketio.emit('msg', {'version': __version__})

@socketio.on('register-sensor')
def ws_register_sensor(message):
    print 'got sensor registration: %s'%message

@socketio.on('sensor')
def ws_sensor(message):
    print 'got sensor message: %s'%message
    socketio.emit('control duh-vice 1', 'forward-%s'%time.time())

@socketio.on('register-control')
def ws_register_control(message):
    print 'got control registration: %s'%message


if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", port=5555, debug=True)

