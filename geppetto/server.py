import time
import cgi
import redis
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
db = redis.StrictRedis('redis', 6379, 0)

import logging
#logging.getLogger('werkzeug').setLevel(logging.ERROR)
#logging.getLogger('werkzeug').disabled = True
#app.logger.disabled = True
#logging.basicConfig(level=logging.WARN)

#from flask.logging import default_handler
#app.logger.removeHandler(default_handler)

__version__ = "0.0.1"


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
    #socketio.emit(get_control_socketio(robot_name, control_name), signal)

def get_robots():
    return sorted(db.smembers('robots'))

def add_robot_name(robot_name):
    db.sadd('robots',robot_name)

def delete_robot(robot_name):
    for control_name in get_controls(robot_name):
        delete_control(robot_name, control_name)
    db.srem('robots',robot_name)

def get_controls(robot_name):
    return sorted(db.smembers('controls:%s'%robot_name))

def add_controls(robot_name, control_info):
    if not (isinstance(sensors, list) or isinstance(sensors, tuple)):
        abort(400)
    for sensor in sensors:
        add_sensor(robot_name, sensor)

def delete_control(robot_name, control_name):
    db.srem('controls:%s'%robot_name, control_name)
    db.delete('control-socketio:%s:%s'%(robot_name, control_name))
    db.delete('control-min:%s:%s'%(robot_name, control_name))
    db.delete('control-max:%s:%s'%(robot_name, control_name))

def add_control(robot_name, control_info):
    # validate and get data
    if not isinstance(control_info,dict):
        abort(400, 'control is not a json object: %s'%control_info)
    if 'control_name' not in control_info:
        abort(400, 'control lacks required field: control_name')
    control_name = control_info['control_name']
    if 'socketio_name' not in control_info:
        abort(400, 'control lacks required field: socketio_name')
    socketio_name = control_info['socketio_name']
    if 'limits' not in control_info:
        abort(400, 'control lacks required field: limits')
    raw_limits = control_info['limits']
    if not (isinstance(raw_limits, list) or isinstance(raw_limits, tuple)) or len(raw_limits)!=2:
        abort(400, 'control required field: limits, is malformed. Must be a tuple of size 2.')
    min_limit, max_limit = control_info['limits']
    # add to the set of robots
    db.sadd('robots',robot_name)
    # add to this robot's set of controls
    db.sadd('controls:%s'%robot_name, control_name)
    # remember this control's socketio_name
    db['control-socketio:%s:%s'%(robot_name, control_name)] = socketio_name
    # remember this control's limits
    db['control-min:%s:%s'%(robot_name, control_name)] = min_limit
    db['control-max:%s:%s'%(robot_name, control_name)] = max_limit
    app.logger.info('added control to %s: %s', robot_name, control_info)

def get_control_socketio(robot_name, control_name):
    return db.get('control-socketio:%s:%s'%(robot_name,control_name))

def get_control_limits(robot_name, control_name):
    return (
            float(db.get('control-min:%s:%s'%(robot_name,control_name))),
            float(db.get('control-max:%s:%s'%(robot_name,control_name)))
            )

def get_control_info(robot_name, control_name):
    return {'control_name': control_name,
            'limits': get_control_limits(robot_name, control_name),
            'socketio': get_control_socketio(robot_name, control_name)}

def get_sensor_info(robot_name, sensor_name):
    return {'sensor_name': sensor_name,
            'mediatype': get_sensor_mediatype(robot_name, sensor_name),
            'socketio': get_sensor_socketio(robot_name, sensor_name)}

def get_robot_info(robot_name):
    return {
            'robot_name': robot_name,
            'controls': [get_control_info(robot_name,control) for control in get_controls(robot_name)],
            'sensors': [get_sensor_info(robot_name,sensor) for sensor in get_sensors(robot_name)],
            }

def get_sensors(robot_name):
    return sorted(db.smembers('sensors:%s'%robot_name))

def add_sensor(robot_name, sensor_info):
    # validate and get data
    if not isinstance(sensor_info,dict):
        abort(400, 'sensor is not a json object: %s'%sensor_info)
    if 'sensor_name' not in sensor_info:
        abort(400, 'sensor lacks required field: sensor_name')
    sensor_name = sensor_info['sensor_name']
    if 'socketio_name' not in sensor_info:
        abort(400, 'sensor lacks required field: socketio_name')
    socketio_name = sensor_info['socketio_name']
    if 'mediatype' not in sensor_info:
        abort(400, 'sensor lacks required field: mediatype')
    mediatype = sensor_info['mediatype']
    # add to the set of robots
    add_robot_name(robot_name)
    # add to this robot's set of sensors
    db.sadd('sensors:%s'%robot_name, sensor_name)
    # remember this sensor's socketio_name
    db['sensor-socketio:%s:%s'%(robot_name, sensor_name)] = socketio_name
    # remember this sensor's mediatype
    db['sensor-mediatype:%s:%s'%(robot_name, sensor_name)] = mediatype
    app.logger.info('added sensor to %s: %s', robot_name, sensor_info)

def add_sensors(robot_name, sensors):
    if not (isinstance(sensors, list) or isinstance(sensors, tuple)):
        abort(400)
    for sensor in sensors:
        add_sensor(robot_name, sensor)

def delete_sensor(robot_name, sensor_name):
    db.srem('sensors:%s'%robot_name, sensor_name)
    db.delete('sensor-socketio:%s:%s'%(robot_name, sensor_name))
    db.delete('sensor-mediatype:%s:%s'%(robot_name, sensor_name))

def get_sensor_socketio(robot_name, sensor_name):
    return db.get('sensor-socketio:%s:%s'%(robot_name,sensor_name))

def get_sensor_mediatype(robot_name, sensor_name):
    return db.get('sensor-mediatype:%s:%s'%(robot_name, sensor_name))

########################################################################
# HTTP communication (browser <--> server)
########################################################################

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
    #return "hi"
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

@app.route('/robots/<robot_name>', methods=['GET'])
def rest_get_robot_info(robot_name):
    check_robot(robot_name)
    return jsonify(get_robot_info(robot_name))

@app.route('/robots/<robot_name>', methods=['POST'])
def rest_post_robot_info(robot_name):
    data = request.json
    add_robot_name(robot_name)
    if 'controls' in data:
        add_controls(robot_name, data['controls'])
    if 'sensors' in data:
        add_sensors(robot_name, data['sensors'])
    return jsonify(get_robot_info(robot_name))

@app.route('/robots/<robot_name>', methods=['DELETE'])
def rest_delete_robot(robot_name):
    delete_robot(robot_name)

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['GET'])
def rest_get_control(robot_name, control_name):
    return jsonify(items=get_control_info(robot_name,control_name))

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['POST'])
def rest_post_control(robot_name, control_name):
    data = request.json
    if 'control_name' not in data:
        data['control_name'] = control_name
    add_robot_name(robot_name)
    add_control(robot_name, data)
    return jsonify(items=get_control_info(robot_name,control_name))

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['DELETE'])
def rest_delete_control(robot_name, control_name):
    delete_control(robot_name, control_name)

@app.route('/robots/<robot_name>/sensors/<sensor_name>', methods=['GET'])
def rest_get_sensors(robot_name, sensor_name):
    return jsonify(items=get_sensor_info(robot_name,sensor_name))

@app.route('/robots/<robot_name>/sensors/<sensor_name>', methods=['POST'])
def rest_post_sensors(robot_name, sensor_name):
    data = request.json
    if 'sensor_name' not in data:
        data['sensor_name'] = sensor_name
    add_robot_name(robot_name)
    add_sensor(robot_name, data)
    return jsonify(items=get_sensor_info(robot_name,sensor_name))

@app.route('/robots/<robot_name>/sensors/<sensor_name>', methods=['DELETE'])
def rest_delete_sensor(robot_name, sensor_name):
    delete_sensor(robot_name, sensor_name)

############ Content REST methods (supporing ajax) ############

#@app.route('/robots/<robot_name>/controls/<control_name>', methods=['POST'])

########################################################################
# SocketIO communication (server <--> robots)
########################################################################

# TODO: make websocket controled (actually, maybe we don't need this anymore)
#def rest_post_control(robot_name, control_name):
#    check_robot(robot_name)
#    check_control(robot_name, control_name)
#    # TODO: check if this control has an active socket
#    signal = request.get_data()
#    app.logger.debug('posting control %s-%s=%s', robot_name, control_name, signal)
#    control_robot(robot_name, control_name, signal)
#    return "Success"

#@socketio.on('connect')
def ws_conn():
    app.logger.info('connected')
    #socketio.emit('msg', {'version': __version__})

#@socketio.on('disconnect')
def ws_disconn():
    app.logger.info('disconnected')
    #socketio.emit('msg', {'version': __version__})

#@socketio.on('sensor')
#def ws_sensor(message):
#    app.logger.info('got sensor message: %s, len=%s'%(message[0], len(message[1])))
#    #app.logger.info('%s'%message)
#    socketio_name, signal = message
#    socketio.emit(socketio_name, signal)


if __name__ == '__main__':
    app.run("0.0.0.0", port=5555, debug=True)

