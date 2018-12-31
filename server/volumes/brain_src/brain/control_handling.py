import numpy as np

from brain import constants

def scale_to_limits(value, control_info):
    min_lim, max_lim = control_info.get('limits',[None,None])
    span = max_lim - min_lim
    return (value * span) + min_lim

############################################################
# Main - Data formatting
############################################################
def format_data(batch, control_infos, prev_batch=None, default_value=0.5):
    '''
    Convert a list of messages into a fmt_batch dictionary that maps each control_name to a numpy array 
    suitable for training models against as outputs. Values are normalized to between 0 and 1 based 
    on the control limits.

    Details:
    - Each layer is aligned by timestamp so that len(fmt_batch["control1"]) == len(fmt_batch["control2"]).
    - Sensor alignment creates gaps where, e.g., we have a timestamp with a new reading for control1 but not control2. 
    In these cases, control1's new reading is provided aligned with control2's most recent reading repeated. 
    To indicate where this padding has been added, the returned fmt_batch is augmented with a mask entry 
    named "{control_name}_mask" for each control name. Mask entries are numpy arrays filled with 1s (original values) and 0s (padded values). 

    control_info is a list of dictionaries of information associated with each control, such as would be returned by GET(localhost:8080/robots/<robot_name>/controls).

    prev_batch is the optional previous batch. If provided, it will be used to get values for padding control values before an initial value is obtained.
    '''

    # initialize batch dictionary (return value)
    fmt_batch = {}

    # Note: the following logic doesn't even attempt to time-align different controls. There's room for improvement here
    for info in control_infos:
        name = info[constants.SIGNAL_NAME]
        # create a column for this control
        col, col_mask = [], []
        # initialize our value (for padding)
        val = default_value if prev_batch is None else prev_batch[name][-1]

        # now work through the batch, formatting each entry or inserting the previous value as padding
        for item in batch:
            is_control = item[constants.SIGNAL_TYPE] == constants.SIGNAL_TYPE_CONTROL
            # is this position a mask position? (boolean)
            # mask all non-control entries (can't just ignore them--they need to line up w the inputs)
            mask_val = is_control and item[ constants.SIGNAL_NAME ] == name
            # mask_val == True means we've got a new reading 
            # for this control. Update the val
            if mask_val == True:
                val = float(item[constants.SIGNAL_VALUE])
            col.append(val)
            col_mask.append(mask_val)

        # Scale each column between 0 and 1 using the limits defined in the control info
        min_val, max_val = info[constants.SIGNAL_LIMITS]
        col_vals = ( np.array(col, dtype=np.float32) - min_val ) / max_val

        # add the new column (and its mask) as a numpy array in the batch
        fmt_batch[ name ] = col_vals
        fmt_batch[ '%s_mask' % name ] = np.array(col_mask, dtype=np.float32)

    return fmt_batch
