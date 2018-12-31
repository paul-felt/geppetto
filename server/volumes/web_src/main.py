import time
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
    #channel.emit(get_control_channel(robot_name, control_name), signal)

def get_robots():
    return sorted(s.decode('utf-8') for s in db.smembers('robots'))

def add_robot_name(robot_name):
    db.sadd('robots',robot_name)

def delete_robot(robot_name):
    for control_name in get_controls(robot_name):
        delete_control(robot_name, control_name)
    for sensor_name in get_sensors(robot_name):
        delete_sensor(robot_name, sensor_name)
    db.srem('robots',robot_name)

def get_controls(robot_name):
    return sorted(s.decode('utf-8') for s in db.smembers('controls:%s'%robot_name))

def add_controls(robot_name, control_infos):
    if not (isinstance(control_infos, list) or isinstance(control_infos, tuple)):
        abort(400)
    for control_info in control_infos:
        add_control(robot_name, control_info)

def add_control(robot_name, control_info):
    # validate and get data
    if not isinstance(control_info,dict):
        abort(400, 'control is not a json object: %s'%control_info)
    if 'name' not in control_info:
        abort(400, 'control lacks required field: name')
    control_name = control_info['name']
    if 'channel_name' not in control_info:
        abort(400, 'control lacks required field: channel_name')
    channel_name = control_info['channel_name']
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
    # remember this control's channel_name
    db['control-channel:%s:%s'%(robot_name, control_name)] = channel_name
    # remember this control's limits
    db['control-min:%s:%s'%(robot_name, control_name)] = min_limit
    db['control-max:%s:%s'%(robot_name, control_name)] = max_limit
    app.logger.info('added control to %s: %s', robot_name, control_info)

def delete_control(robot_name, control_name):
    db.srem('controls:%s'%robot_name, control_name)
    db.delete('control-channel:%s:%s'%(robot_name, control_name))
    db.delete('control-min:%s:%s'%(robot_name, control_name))
    db.delete('control-max:%s:%s'%(robot_name, control_name))

def get_control_channel(robot_name, control_name):
    return db.get('control-channel:%s:%s'%(robot_name,control_name)).decode('utf-8')

def get_control_limits(robot_name, control_name):
    return (
            float(db.get('control-min:%s:%s'%(robot_name,control_name))),
            float(db.get('control-max:%s:%s'%(robot_name,control_name)))
            )

def get_control_info(robot_name, control_name):
    return {'name': control_name,
            'limits': get_control_limits(robot_name, control_name),
            'channel_name': get_control_channel(robot_name, control_name)}

def get_sensor_info(robot_name, sensor_name):
    return {'name': sensor_name,
            'mediatype': get_sensor_mediatype(robot_name, sensor_name),
            'shape': get_sensor_shape(robot_name, sensor_name),
            'channel_name': get_sensor_channel(robot_name, sensor_name)}

def get_robot_info(robot_name):
    return {
            'robot_name': robot_name,
            'controls': [get_control_info(robot_name,control) for control in get_controls(robot_name)],
            'sensors': [get_sensor_info(robot_name,sensor) for sensor in get_sensors(robot_name)],
            }

def get_sensors(robot_name):
    return sorted(s.decode('utf-8') for s in db.smembers('sensors:%s'%robot_name))

def add_sensor(robot_name, sensor_info):
    # validate and get data
    if not isinstance(sensor_info,dict):
        abort(400, 'sensor is not a json object: %s'%sensor_info)
    if 'name' not in sensor_info:
        abort(400, 'sensor lacks required field: name')
    sensor_name = sensor_info['name']
    if 'channel_name' not in sensor_info:
        abort(400, 'sensor lacks required field: channel_name')
    channel_name = sensor_info['channel_name']
    if 'mediatype' not in sensor_info:
        abort(400, 'sensor lacks required field: mediatype')
    mediatype = sensor_info['mediatype']
    shape = sensor_info['shape']
    # add to the set of robots
    add_robot_name(robot_name)
    # add to this robot's set of sensors
    db.sadd('sensors:%s'%robot_name, sensor_name)
    # remember this sensor's channel_name
    db['sensor-channel:%s:%s'%(robot_name, sensor_name)] = channel_name
    # remember this sensor's mediatype
    db['sensor-mediatype:%s:%s'%(robot_name, sensor_name)] = mediatype
    # remember this sensor's shape
    db['sensor-shape:%s:%s'%(robot_name, sensor_name)] = ','.join(str(v) for v in shape)
    app.logger.info('added sensor to %s: %s', robot_name, sensor_info)

def add_sensors(robot_name, sensor_infos):
    if not (isinstance(sensor_infos, list) or isinstance(sensor_infos, tuple)):
        abort(400)
    for sensor_info in sensor_infos:
        add_sensor(robot_name, sensor_info)

def delete_sensor(robot_name, sensor_name):
    db.srem('sensors:%s'%robot_name, sensor_name)
    db.delete('sensor-channel:%s:%s'%(robot_name, sensor_name))
    db.delete('sensor-mediatype:%s:%s'%(robot_name, sensor_name))

def get_sensor_channel(robot_name, sensor_name):
    return db.get('sensor-channel:%s:%s'%(robot_name,sensor_name)).decode('utf-8')

def get_sensor_mediatype(robot_name, sensor_name):
    return db.get('sensor-mediatype:%s:%s'%(robot_name, sensor_name)).decode('utf-8')

def get_sensor_shape(robot_name, sensor_name):
    return tuple( int(v) for v in db.get('sensor-shape:%s:%s'%(robot_name, sensor_name)).decode('utf-8').split(',') )

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
    return render_template('index.html')

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
    if not request.is_json:
        abort(400, 'request must be application/json')
    data = request.get_json()
    add_robot_name(robot_name)
    if 'controls' in data:
        add_controls(robot_name, data['controls'])
    if 'sensors' in data:
        add_sensors(robot_name, data['sensors'])
    db.save() # write data to disk
    return jsonify(get_robot_info(robot_name))

@app.route('/robots/<robot_name>', methods=['DELETE'])
def rest_delete_robot(robot_name):
    check_robot(robot_name)
    delete_robot(robot_name)
    db.save() # write data to disk
    return 'ok'

@app.route('/robots/<robot_name>/controls', methods=['GET'])
def rest_get_controls(robot_name):
    check_robot(robot_name)
    return jsonify([get_control_info(robot_name,name) for name in get_controls(robot_name)])

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['GET'])
def rest_get_control(robot_name, control_name):
    check_robot(robot_name)
    check_control(robot_name,control_name)
    return jsonify(get_control_info(robot_name,control_name))

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['POST'])
def rest_post_control(robot_name, control_name):
    if not request.is_json:
        abort(400, 'request must be application/json')
    data = request.get_json()
    if 'name' not in data:
        data['name'] = control_name
    add_robot_name(robot_name)
    add_control(robot_name, data)
    db.save() # write data to disk
    return jsonify(get_control_info(robot_name,control_name))

@app.route('/robots/<robot_name>/controls/<control_name>', methods=['DELETE'])
def rest_delete_control(robot_name, control_name):
    check_robot(robot_name)
    check_control(robot_name,control_name)
    delete_control(robot_name, control_name)
    db.save() # write data to disk
    return 'ok'

@app.route('/robots/<robot_name>/sensors', methods=['GET'])
def rest_get_sensors(robot_name):
    check_robot(robot_name)
    return jsonify([get_sensor_info(robot_name,name) for name in get_sensors(robot_name)])

@app.route('/robots/<robot_name>/sensors/<sensor_name>', methods=['GET'])
def rest_get_sensor(robot_name, sensor_name):
    check_robot(robot_name)
    check_sensor(robot_name,sensor_name)
    return jsonify(get_sensor_info(robot_name,sensor_name))

@app.route('/robots/<robot_name>/sensors/<sensor_name>', methods=['POST'])
def rest_post_sensor(robot_name, sensor_name):
    if not request.is_json:
        abort(400, 'request must be application/json')
    data = request.get_json()
    if 'name' not in data:
        data['name'] = sensor_name
    add_robot_name(robot_name)
    add_sensor(robot_name, data)
    db.save() # write data to disk
    return jsonify(get_sensor_info(robot_name,sensor_name))

@app.route('/robots/<robot_name>/sensors/<sensor_name>', methods=['DELETE'])
def rest_delete_sensor(robot_name, sensor_name):
    check_robot(robot_name)
    check_sensor(robot_name,sensor_name)
    delete_sensor(robot_name, sensor_name)
    db.save() # write data to disk
    return 'ok'


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)

