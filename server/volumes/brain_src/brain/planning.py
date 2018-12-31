import time
import random
import asyncio
import logging
import numpy as np
import keras

from brain.utils import episode_utils
from brain import sensor_handling
from brain import control_handling
from brain import constants
from brain import models

logger = logging.getLogger(__name__)


class Planner(object):
    def __init__(self, robot_info, session):
        pass
    def init(self):
        raise NotImplementedError()
    def is_time_to_act(self, batch):
        return len(batch) > 0
    async def train(self):
        pass # default implementation is no-op
    async def update(self, world_state, plan, input_batch):
        raise NotImplementedError()


class NoopPlanner(Planner):
    def init(self):
        return None,None
    async def update(self, world_state, plan, input_batch):
        await asyncio.sleep(1)
        return None,None

class PrintingPlanner(Planner):
    def init(self):
        return None,None
    async def update(self, world_state, plan, input_batch):
        print ('InputPrintingPlanner: Input Batch:',input_batch)
        await asyncio.sleep(1)
        return None,None

class TwitchPlanner(Planner):
    def __init__(self, robot_info, session):
        self.robot_info = robot_info
        self.session = session
        self.ts = time.time()
    def init(self):
        return None,None
    async def update(self, world_state, plan, input_batch):
        # sleep for a second to simulate processing time
        await asyncio.sleep(1) # keep it from burning all the cpu
        for control in self.robot_info.get('controls',[]):
            min_lim, max_lim = control.get('limits',[None,None])
            # The full span would be max_lim-min_lim, but that could be dangerous
            # if the robot behaves badly at its control extremes. So we halve the range.
            span = (max_lim-min_lim)/2
            rand_val = random.random()*span + min_lim + (span/2)
            # emit twitch
            msg = {
                constants.SIGNAL_VALUE : rand_val,
                constants.SIGNAL_ROBOT_NAME: self.robot_info[constants.SIGNAL_ROBOT_NAME],
                constants.SIGNAL_NAME: control[constants.SIGNAL_NAME],
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_CONTROL,
                constants.SIGNAL_SOURCE: constants.SIGNAL_SOURCE_BRAIN,
                constants.SIGNAL_TS: time.time()*1000,
            }
            logger.info('Twitch %s=%s (batch=%s)', control[constants.SIGNAL_NAME], rand_val, len(input_batch))
            url = 'gp.robots.{robot_name}.controls.{control_name}'.format(
                robot_name=self.robot_info[constants.SIGNAL_ROBOT_NAME],
                control_name=control[constants.SIGNAL_NAME],
            )
            self.session.publish(url, **msg)
        self.ts = time.time()
        return None,None


class SingleStepDLPlanner(Planner):
    ' A simple planner that makes decisions based on the inputs with no kind of statefulness or memory across timesteps. '
    def __init__(self, robot_info, session, world_state_shape=(50,50), plan_shape=(50)):
        self.world_state_shape = world_state_shape
        self.plan_shape = plan_shape
        self.robot_info = robot_info
        self.session = session
        self.model = models.create_end_to_end_model1(robot_info)
        self.ts = time.time()
    def init(self):
        # TODO: random init
        world_state = np.zeros(self.world_state_shape)
        plan_state = np.zeros(self.plan_shape)
        return world_state, plan_state

    def is_time_to_act(self, batch):
        ' dumb heuristic that encourages lots of training to happen '
        return len(batch) > 0 and random.random() < 0.1

    async def train(self):
        ' train on a random episode '
        episode_batch = episode_utils.load_random_episode(self.robot_info[constants.SIGNAL_ROBOT_NAME])
        if episode_batch is not None:
            batch_inputs  = sensor_handling.format_data(episode_batch, sensor_infos = self.robot_info['sensors'])
            batch_outputs = control_handling.format_data(episode_batch, control_infos = self.robot_info['controls'])
            loss = self.model.train_on_batch(batch_inputs, batch_outputs)
            logger.info('SingleStepDLPlanner model.train_on_batch: %s', str(loss))
        else:
            logger.info('SingleStepDLPlanner found no episodes to train on.')

    async def update(self, world_state, plan, input_batch):
        # Update world state and our plan in a single joint model
        # 1- format sensor data for DL
        batch = sensor_handling.format_data(input_batch, sensor_infos = self.robot_info['sensors'])
        logger.info('SingleStepDLPlanner batch: %s', ' '.join( [ '%s:%s' % (k,v.shape) for k,v in batch.items() ] ))

        # 2- run through the model
        predictions = models.predict_as_dict(self.model, batch)
        logger.info( 'SingleStepDLPlanner model.predict(batch): %s', ' '.join(['%s:%s' % (k,v.shape) for k,v in predictions.items()]) )

        # TODO: think about doing:
        # 3- get world state out of model
        # 4- get plan state out of model
        # 5- get action(s) out of model

        # 6- Do actions
        await asyncio.sleep(0.01) # keep it from burning all the cpu
        robot_name = self.robot_info[constants.SIGNAL_ROBOT_NAME]
        for control in self.robot_info.get('controls',[]):
            control_name = control[constants.SIGNAL_NAME]
            # note: if we had a batch of multiple observations, we're just going to 
            # ignore all but the final predictions. Because this simple model ignores 
            # transitions across time
            control_value = predictions[control_name][-1]
            # rescale the prediction from 0-1 out to the control's limits
            control_value = control_handling.scale_to_limits(control_value, control)
            # emit twitch
            msg = {
                constants.SIGNAL_VALUE : control_value,
                constants.SIGNAL_ROBOT_NAME: robot_name,
                constants.SIGNAL_NAME: control_name,
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_CONTROL,
                constants.SIGNAL_SOURCE: constants.SIGNAL_SOURCE_BRAIN,
                constants.SIGNAL_TS: time.time()*1000,
            }
            logger.info('SingleStepDLPlanner emit action: %s=%s (batch_len=%s)', control_name, control_value, len(input_batch))
            url = 'gp.robots.{robot_name}.controls.{control_name}'.format(
                robot_name=robot_name,
                control_name=control_name,
            )
            #self.session.publish(url, **msg) TODONOW: re-enable this
        self.ts = time.time()
        return None,None

