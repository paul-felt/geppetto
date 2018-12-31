import numpy as np
import base64
from io import BytesIO
from PIL import Image
import logging

from brain import constants
from brain import models

logger = logging.getLogger(__file__)

############################################################
# Formatters
############################################################
def parse_image_from_data(jpgdata):
    # if text, assume base64-encoding
    if isinstance(jpgdata, str):
        jpgdata = base64.b64decode(jpgdata)
    file_jpgdata = BytesIO(jpgdata)
    img = Image.open(file_jpgdata)
    return img

def jpeg_formatter(sensor_info, default_value=0):
    def jpeg_formatter_impl(signal_info):
        if signal_info is not None:
            # PIL image
            pic = parse_image_from_data( signal_info[constants.SIGNAL_VALUE] )
        # we don't have an image. Just return an array of default_value with the right dimensions
        else:
            # create a fake picture and stuff it full of default values
            pic = Image.new(mode='RGB', size=sensor_info[constants.SIGNAL_SHAPE])
            pic.putdata([(default_value,default_value,default_value)] * np.prod(sensor_info[constants.SIGNAL_SHAPE]))
        # np array that is (width, height, channel)
        return np.array(pic)
    return jpeg_formatter_impl

############################################################
# Mappings (which model/formatter goes with which data?)
############################################################
def data_formatter_for(sensor_info):
    ' get the data formatter in charge of handling the given sensor_info '
    mediatype_to_data_formatter = {
        'jpeg' : jpeg_formatter(sensor_info),
    }
    mediatype = sensor_info[constants.SIGNAL_MEDIATYPE]
    return mediatype_to_data_formatter.get( mediatype, None )

############################################################
# Main - Data formatting
############################################################
def format_data(batch, sensor_infos, prev_batch=None):
    '''
    Convert a list of messages into a fmt_batch dictionary that maps each sensor_name to a numpy array 
    suitable for training models against. 

    Details:
    - Each layer is aligned by timestamp so that len(fmt_batch["sensor1"]) == len(fmt_batch["sensor2"]).
    - Sensor alignment creates gaps where, e.g., we have a timestamp with a new reading for sensor1 but not sensor2. 
    In these cases, sensor1's new reading is provided aligned with sensor2's most recent reading repeated. 
    To indicate where this padding has been added, the returned fmt_batch is augmented with a mask entry 
    named "{sensor_name}_mask" for each sensor name. Mask entries are numpy arrays filled with 1s (original values) and 0s (padded values). 

    sensor_info is a list of dictionaries of information associated with each sensor, such as would be returned by GET(localhost:8080/robots/<robot_name>/sensors).

    prev_batch is the optional previous batch. If provided, it will be used to get values for padding sensor values before an initial value is obtained.
    '''
    assert batch is not None, 'unable to format a None batch'

    # initialize batch dictionary (return value)
    fmt_batch = {}

    # Note: the following logic doesn't even attempt to time-align different sensors. There's room for improvement here
    for info in sensor_infos:
        name = info[constants.SIGNAL_NAME]
        # create a column for this sensor
        col, col_mask = [], []
        formatter = data_formatter_for( info )
        if formatter is None:
            raise ValueError('no formatter for sensor mediatype: %s' % info.get(constants.SIGNAL_MEDIATYPE))
        # initialize our value (for padding)
        val = formatter(None) if prev_batch is None else prev_batch[name][-1]

        # now work through the batch, formatting each sensor entry or inserting the previous value as padding
        for item in batch:
            is_sensor = item[constants.SIGNAL_TYPE] == constants.SIGNAL_TYPE_SENSOR
            # is this position a mask position? (boolean)
            # mask all non-sensor entries (can't just ignore them--they need to line up w the outputs)
            mask_val = is_sensor and item[ constants.SIGNAL_NAME ] == name
            # mask==True means this is a legit new value and
            # we've got a new reading for this sensor. Update the val
            if mask_val == True:
                val = formatter(item)
            col.append(val)
            col_mask.append(mask_val)

        # add the new column (and its mask) as a numpy array in the batch
        fmt_batch[ name ] = np.array(col, dtype=np.float32)
        fmt_batch[ '%s_mask' % name ] = np.array(col_mask, dtype=np.float32)

    return fmt_batch
