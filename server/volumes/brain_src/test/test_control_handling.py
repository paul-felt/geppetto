import unittest

import numpy as np
import base64

from brain import control_handling
from brain import constants

claw_control_info = {
    constants.SIGNAL_NAME: 'claw',
    constants.SIGNAL_LIMITS: [100.0, 400.0],
    constants.SIGNAL_CHANNEL_NAME: 'gp.robots.testrobot.controls.claw',
}
twist_control_info = {
    constants.SIGNAL_NAME: 'twist',
    constants.SIGNAL_LIMITS: [100.0, 500.0],
    constants.SIGNAL_CHANNEL_NAME: 'gp.robots.testrobot.controls.twist',
}

class TestControlHandling(unittest.TestCase):

    # example assertions
    #self.assertEqual('foo'.upper(), 'FOO')
    #self.assertTrue('FOO'.isupper())
    #self.assertFalse('Foo'.isupper())
    #with self.assertRaises(TypeError):
    #    s.split(2)

    def test_format_control_output(self):
        data = [
            {
                constants.SIGNAL_NAME: "bogus",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_CONTROL,
                constants.SIGNAL_VALUE: 100,
                constants.SIGNAL_TS: 1,
            },
            {
                constants.SIGNAL_NAME: "claw",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_CONTROL,
                constants.SIGNAL_VALUE: 100,
                constants.SIGNAL_TS: 2,
            },
            {
                constants.SIGNAL_NAME: "twist",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_CONTROL,
                constants.SIGNAL_VALUE: 500,
                constants.SIGNAL_TS: 3,
            },
            {
                constants.SIGNAL_NAME: "claw",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_CONTROL,
                constants.SIGNAL_VALUE: 250,
                constants.SIGNAL_TS: 4,
            },
        ]

        batch = control_handling.format_data(data, control_infos = [claw_control_info, twist_control_info])

        #print('aaa',batch.keys())
        self.assertEqual(batch.keys(), set(['claw', 'claw_mask', 'twist', 'twist_mask']))
        #print('bbb claw_mask',batch['claw_mask'])
        self.assertTrue( np.all( batch['claw_mask'] == [0,1,0,1] ) )
        #print('ccc claw',batch['claw'])
        self.assertTrue( np.all( batch['claw'] == [0.5, 0.0, 0.0, 0.5] ) )

        #print('ddd twist_mask',batch['twist_mask'])
        self.assertTrue( np.all( batch['twist_mask'] == [0,0,1,0]) )
        #print('eee twist',batch['twist'])
        self.assertTrue( np.all( batch['twist'] == [0.5, 0.5, 1.0, 1.0] ) )

    def test_format_control_output_empty(self):
        ' make sure an empty batch (just sensors) gives us default values for all controls '
        data = [
            {
                constants.SIGNAL_NAME: "bogus",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_SENSOR,
                constants.SIGNAL_VALUE: 100,
                constants.SIGNAL_TS: 1,
            },
        ]

        batch = control_handling.format_data(data, control_infos = [claw_control_info, twist_control_info])
        self.assertEqual(batch.keys(), set(['claw', 'claw_mask', 'twist', 'twist_mask']))
        #print('bbb claw_mask',batch['claw_mask'])
        self.assertTrue( np.all( batch['claw_mask'] == [0] ) )
        #print('ccc claw',batch['claw'])
        self.assertTrue( np.all( batch['claw'] == [0.5] ) )



    def test_scale_between_0_and_1(self):
        self.assertEqual( 0.0, control_handling.scale_between_0_and_1(100, claw_control_info) )
        self.assertEqual( 0.5, control_handling.scale_between_0_and_1(250, claw_control_info) )
        self.assertEqual( 1.0, control_handling.scale_between_0_and_1(400, claw_control_info) )

    def test_to_control_limits(self):
        self.assertEqual( 100, control_handling.scale_to_control_limits(0.0, claw_control_info) )
        self.assertEqual( 250, control_handling.scale_to_control_limits(0.5, claw_control_info) )
        self.assertEqual( 400, control_handling.scale_to_control_limits(1.0, claw_control_info) )

    def test_shift_forward(self):
        batch = {
            'a': np.array([2,4,6,8], dtype='float32'),
            'b': np.array([1,3,5,7], dtype='float32'),
        }
        shifted_batch = control_handling.shift_forward(batch, prefix='prev_', default=0.5)
        #print('shifted batch==%s'%shifted_batch)
        self.assertTrue(np.all( shifted_batch['prev_a'] == [0.5, 2, 4, 6] ) )
        self.assertTrue(np.all( shifted_batch['prev_b'] == [0.5, 1, 3, 5] ) )

        shifted_batch = control_handling.shift_forward(batch, prefix='prev_', prev_batch={'a':[0.4], 'b':[0.3]})
        #print('shifted batch==%s'%shifted_batch)
        self.assertTrue(np.all( shifted_batch['prev_a'] == [0.4, 2, 4, 6] ) )
        self.assertTrue(np.all( shifted_batch['prev_b'] == [0.3, 1, 3, 5] ) )

if __name__ == '__main__':
    unittest.main()

