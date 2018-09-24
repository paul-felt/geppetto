from gevent import monkey
monkey.patch_all()

import time
import cgi
import redis
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
db = redis.StrictRedis('redis', 6379, 0)
socketio = SocketIO(app)

__version__ = "0.0.1"

def new_robot_db_entry():
    return {'sensors':[], 'controls':[]}


@app.route('/')
def main():
    return render_template('index.html')
    #for robot_name in db.smembers('robots'):
    #    for control_name in db.smembers('controls:%s'%robot_name):
    #        socketio_name = db['control-socketio:%s:%s'%(robot_name,control_name)]
    #        socketio.emit(socketio_name, 'forward-%s'%time.time())
    #return ''

@socketio.on('connect')
def ws_conn():
    print('connected')
    socketio.emit('msg', {'version': __version__})

@socketio.on('disconnect')
def ws_disconn():
    print('disconnected')
    socketio.emit('msg', {'version': __version__})

@socketio.on('register-sensor')
def ws_register_sensor(message):
    robot_name = message['robot_name']
    sensor_name = message['sensor_name']
    socketio_name = message['socketio_name']
    mediatype = message['mediatype']
    # add to the set of robots
    db.sadd('robots',robot_name)
    # add to this robot's set of sensors
    db.sadd('sensors:%s'%robot_name, sensor_name)
    # remember this sensor's socketio_name
    db['sensor-socketio:%s:%s'%(robot_name, sensor_name)] = socketio_name
    # remember this sensor's type
    db['sensor-mediatype:%s:%s'%(robot_name, sensor_name)] = mediatype
    print('got sensor registration: %s'%message)

@socketio.on('sensor')
def ws_sensor(message):
    print('got sensor message: %s'%message)
    socketio_name, signal = message

@socketio.on('register-control')
def ws_register_control(message):
    robot_name = message['robot_name']
    control_name = message['control_name']
    socketio_name = message['socketio_name']
    limits = message['limits']
    # add to the set of robots
    db.sadd('robots',robot_name)
    # add to this robot's set of controls
    db.sadd('controls:%s'%robot_name, control_name)
    # remember this control's socketio_name
    db['control-socketio:%s:%s'%(robot_name, control_name)] = socketio_name
    # remember this control's type
    db['control-mediatype:%s:%s'%(robot_name, control_name)] = mediatype
    print('got control registration: %s'%message)


if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", port=5555, debug=True)

