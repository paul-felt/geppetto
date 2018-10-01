from gevent import monkey
monkey.patch_all()

import time
import cgi
import redis
from flask import Flask, render_template, request, jsonify, abort
from flask_socketio import SocketIO

app = Flask(__name__)
db = redis.StrictRedis('redis', 6379, 0)
socketio = SocketIO(app)

import logging
#logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('werkzeug').disabled = True
app.logger.disabled = True
#logging.basicConfig(level=logging.WARN)

#from flask.logging import default_handler
#app.logger.removeHandler(default_handler)

__version__ = "0.0.1"

def new_robot_db_entry():
    return {'sensors':[], 'controls':[]}


########################################################################
# Utilities
########################################################################

def control_robot(robot_name, control_name, signal):
    # enforce limits on control
    min_limit, max_limit = get_control_limits(robot_name, control_name)
    app.logger.debug("Robot control: %s",signal)
    signal = float(signal)
    signal = min(signal, max_limit)
    signal = max(signal, min_limit)
    app.logger.debug("Limited Robot control: %s",signal)
    socketio.emit(get_control_socketio(robot_name, control_name), signal)

def get_robots():
    return sorted(db.smembers('robots'))

def get_robot_infos():
    return [get_robot_info(robot_name) for robot_name in get_robots()]

def get_controls(robot_name):
    return sorted(db.smembers('controls:%s'%robot_name))

def get_control_socketio(robot_name, control_name):
    return db.get('control-socketio:%s:%s'%(robot_name,control_name))

def get_control_limits(robot_name, control_name):
    return (
            float(db.get('control-min:%s:%s'%(robot_name,control_name))),
            float(db.get('control-max:%s:%s'%(robot_name,control_name)))
            )

def get_control_info(robot_name, control_name):
    return {'control_name': control_name,
            'limits': get_control_limits(robot_name, control_name)}

def get_sensor_info(robot_name, sensor_name):
    return {'sensor_name': sensor_name,
            'mediatype': get_sensor_mediatype(robot_name, sensor_name)}

def get_robot_info(robot_name):
    return {
            'robot_name': robot_name,
            'controls': [get_control_info(robot_name,control) for control in get_controls(robot_name)],
            'sensors': [get_sensor_info(robot_name,sensor) for sensor in get_sensors(robot_name)],
            }

def get_sensors(robot_name):
    return sorted(db.smembers('sensors:%s'%robot_name))

def get_sensor_socketio(robot_name, sensor_name):
    return db.get('sensor-socketio:%s:%s'%(robot_name,sensor_name))

def get_sensor_mediatype(robot_name, sensor_name):
    return db.get('sensor-mediatype:%s:%s'%(robot_name, sensor_name))

########################################################################
# HTTP communication (browser <--> server)
########################################################################
#def jsonify_set(obj):
#    return jsonify({'results': list(obj)})

def check_robot(robot_name):
    if robot_name not in get_robots():
        abort(404)

def check_control(robot_name, control_name):
    if control_name not in get_controls(robot_name):
        abort(404)

def check_sensor(robot_name, sensor_name):
    if sensor_name not in get_sensors(robot_name):
        abort(404)

# Main web page
@app.route('/')
def main():
    return render_template('index.html')
    #for robot_name in db.smembers('robots'):
    #    for control_name in db.smembers('controls:%s'%robot_name):
    #        socketio_name = db['control-socketio:%s:%s'%(robot_name,control_name)]
    #        socketio.emit(socketio_name, 'forward-%s'%time.time())
    #return ''

######### Basic Object REST #########

@app.route('/robots', methods=['GET'])
def rest_get_robots():
    return jsonify({'robots': [{'robot_name':r} for r in get_robots()]})

@app.route('/robots/<robot_name>')
def rest_get_robot_info(robot_name):
    check_robot(robot_name)
    return jsonify(get_robot_info(robot_name))

#@app.route('/robots/<robot_name>/controls')
#def rest_get_controls(robot_name):
#    check_robot(robot_name)
#    return jsonify_set(get_controls(robot_name))
#
#@app.route('/robots/<robot_name>/controls/<control_name>/limits')
#def rest_get_control_limits(robot_name, control_name):
#    check_robot(robot_name)
#    check_control(robot_name, control_name)
#    return jsonify_set(get_control_limits(robot_name, control_name)) 
#
#@app.route('/robots/<robot_name>/sensors')
#def rest_get_sensors(robot_name):
#    check_robot(robot_name)
#    return jsonify_set(get_sensors(robot_name))

############ Content REST methods (supporing ajax) ############

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['POST'])
def rest_post_control(robot_name, control_name):
    check_robot(robot_name)
    check_control(robot_name, control_name)
    # TODO: check if this control has an active socket
    signal = request.get_data()
    app.logger.debug('posting control %s-%s=%s', robot_name, control_name, signal)
    control_robot(robot_name, control_name, signal)
    return "Success"

########################################################################
# SocketIO communication (server <--> robots)
########################################################################

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
    min_limit, max_limit = message['limits']
    # add to the set of robots
    db.sadd('robots',robot_name)
    # add to this robot's set of controls
    db.sadd('controls:%s'%robot_name, control_name)
    # remember this control's socketio_name
    db['control-socketio:%s:%s'%(robot_name, control_name)] = socketio_name
    # remember this control's limits
    db['control-min:%s:%s'%(robot_name, control_name)] = min_limit
    db['control-max:%s:%s'%(robot_name, control_name)] = max_limit
    print('got control registration: %s'%message)


if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", port=5555, debug=True)

