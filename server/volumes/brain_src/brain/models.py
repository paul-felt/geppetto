import time
import random
import asyncio
import logging
import numpy as np
import keras
from keras import Model
from keras.layers import Input, Conv2D, MaxPool2D, Dropout, Flatten, concatenate
from keras.layers import Dense, RepeatVector, TimeDistributed

from brain import constants

logger = logging.getLogger(__name__)


############################################################
# Utils
############################################################
def predict_as_dict(model, batch):
    ' keras model.outputs have names like "claw/Sigmoid:0", but we just want the first part '
    predictions = model.predict(batch)
    return {out.name.split('/')[0]: predictions[i] for i,out in enumerate(model.outputs)}

############################################################
# Input Sub-models
############################################################
def create_jpeg_input_model(sensor_info, name, xforms=2):
    ' very basic convolutional image model '
    rgb_jpeg_shape = list(reversed(sensor_info[constants.SIGNAL_SHAPE])) + [3,] # the shape is the shape of the image with 3 color channels (RGB)
    image_input = Input(shape=rgb_jpeg_shape)
    layer = image_input

    # CNN transforms
    for i in range(xforms):
    
        layer = Conv2D(10, (3,3), activation='relu') (layer)
        layer = MaxPool2D((2,2)) (layer)
        layer = Dropout(0.2) (layer)

    # Smash down into a single vector
    flat_vector = Flatten()(layer)

    model = Model(inputs=image_input, outputs=flat_vector, name=name)
    print("##################### %s ########################" % name)
    model.summary()
    return model

def create_input_model_for(sensor_info):
    ' get the model in charge of handling the given sensor_info '
    mediatype_to_model_creator = {
        'jpeg' : create_jpeg_input_model,
    }
    sensor_mediatype = sensor_info[constants.SIGNAL_MEDIATYPE]
    assert sensor_mediatype in mediatype_to_model_creator, 'unable to create input model for unknown mediatype: %s' % sensor_mediatype
    return mediatype_to_model_creator[ sensor_mediatype ] (sensor_info, name='%s_submodel'%sensor_info[constants.SIGNAL_NAME])

def input_from_submodel(model):
    " create an Input() layer with the same shape as the given submodel's input, and with the same name as the given submodel minus '_submodel'. For example, if the submodel is named picam_submodel and has an input with shape (32,32), then this method  will return Input(shape=(32,32),name='picam') "
    # Get submodel's input dimensions
    # [1:] selects all dimensions except for the batch dimension at the beginning
    model_input = model.get_input_at(0)
    input_shape = model_input.get_shape().as_list()[1:]
    # use the submodel's name minus '_submodel'
    sensor_name = model.name.replace('_submodel','')
    return Input(shape=input_shape, name=sensor_name)


############################################################
# End-to-End Models
############################################################
def create_end_to_end_model1(robot_info, world_state_size=50, plan_size=20):
    " construct a model based on this robot's inputs/outputs "
    sensor_infos = robot_info['sensors']
    control_infos = robot_info['controls']
    assert len(sensor_infos) >=1, "can't create a model for a robot (%s) with no sensors"%robot_info.get(constants.SIGNAL_ROBOT_NAME)
    assert len(control_infos) >=1, "can't create a model for a robot (%s) with no controls"%robot_info.get(constants.SIGNAL_ROBOT_NAME)

    # Sensor submodels
    sensor_input_submodels = [create_input_model_for(sensor_info) for sensor_info in sensor_infos]

    # create inputs based on the sensor submodel inputs, and then the models over them
    sensor_inputs = [input_from_submodel(input_model) for input_model in sensor_input_submodels]
    sensor_vecs = [sensor_model(sensor_input) for sensor_model,sensor_input in zip(sensor_input_submodels,sensor_inputs)]

    # combine sensor vector representations
    sensor_summary_vec = concatenate(sensor_vecs) if len(sensor_vecs) > 1 else sensor_vecs[0]

    # Sensor vector -> World state vector
    world_state_vec = Dense(world_state_size, activation='relu') (sensor_summary_vec)
    #print("????????????? DEBUG ???????????????")
    #Model(inputs=sensor_inputs, outputs=world_state_vec).summary()

    # World state vector -> Plan 
    plan = Dense(plan_size) (world_state_vec)

    # World state + Plan -> output voltages
    num_controls = len(control_infos)
    actions_input = concatenate([world_state_vec, plan])
    actions_output = []
    for control_info in control_infos:
        actions_output.append( Dense(1,activation='sigmoid', name=control_info[constants.SIGNAL_NAME])(actions_input) )

    model = Model(inputs=sensor_inputs, outputs=actions_output)
    model.compile(optimizer='adam', loss='binary_crossentropy')
    print("########################################## MAIN MODEL #############################################")
    model.summary()
    return model



