import unittest

import numpy as np
import base64

from brain import sensor_handling
from brain import constants

# a single-pixel rgb image: dim = (1,1,3), value = [[[255, 255, 255]]]
# where the dimensions are (height, width, channels)
base64_encoded_one_pixel_jpeg = r'/9j/4AAQSkZJRgABAQEAYABgAAD/4QAWRXhpZgAASUkqAAgAAAAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AAf/Z'

testcam2_sensor_info = {
    constants.SIGNAL_NAME: 'testcam2',
    constants.SIGNAL_SHAPE: [1,1],
    constants.SIGNAL_MEDIATYPE: 'jpeg',
    constants.SIGNAL_CHANNEL_NAME: 'gp.robots.testrobot.sensors.testcam2',
}
jpeg_sensor_info = {
    constants.SIGNAL_NAME: 'testcam',
    constants.SIGNAL_SHAPE: [1,1],
    constants.SIGNAL_MEDIATYPE: 'jpeg',
    constants.SIGNAL_CHANNEL_NAME: 'gp.robots.testrobot.sensors.testcam',
}

class TestSensorHandling(unittest.TestCase):

    # example assertions
    #self.assertEqual('foo'.upper(), 'FOO')
    #self.assertTrue('FOO'.isupper())
    #self.assertFalse('Foo'.isupper())
    #with self.assertRaises(TypeError):
    #    s.split(2)

    def test_format_data_jpeg(self):
        data = [
            {
                constants.SIGNAL_NAME: "bogus",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_SENSOR,
                constants.SIGNAL_MEDIATYPE: "jpeg",
                constants.SIGNAL_VALUE: base64_encoded_one_pixel_jpeg,
                constants.SIGNAL_TS: 1,
            },
            {
                constants.SIGNAL_NAME: "testcam",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_SENSOR,
                constants.SIGNAL_MEDIATYPE: "jpeg",
                constants.SIGNAL_VALUE: base64_encoded_one_pixel_jpeg,
                constants.SIGNAL_TS: 2,
            },
            {
                constants.SIGNAL_NAME: "testcam2",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_SENSOR,
                constants.SIGNAL_MEDIATYPE: "jpeg",
                constants.SIGNAL_VALUE: base64_encoded_one_pixel_jpeg,
                constants.SIGNAL_TS: 3,
            },
            {
                constants.SIGNAL_NAME: "testcam",
                constants.SIGNAL_TYPE: constants.SIGNAL_TYPE_SENSOR,
                constants.SIGNAL_MEDIATYPE: "jpeg",
                constants.SIGNAL_VALUE: base64_encoded_one_pixel_jpeg,
                constants.SIGNAL_TS: 4,
            },
        ]

        batch = sensor_handling.format_data(data, sensor_infos = [jpeg_sensor_info, testcam2_sensor_info])

        #print('aaa',batch.keys())
        self.assertEqual(batch.keys(), set(['testcam', 'testcam_mask', 'testcam2', 'testcam2_mask']))
        #print('bbb testcam_mask',batch['testcam_mask'])
        self.assertTrue( np.all( batch['testcam_mask'] == [0,1,0,1]) )
        #print('ccc testcam',batch['testcam'])
        self.assertTrue( np.all( batch['testcam'] == np.array([
                                                            [[[0.,0.,0.]]],
                                                            [[[255.,255.,255.]]],
                                                            [[[255.,255.,255.]]],
                                                            [[[255.,255.,255.]]],
        ]) ) )

        #print('ddd testcam2_mask',batch['testcam2_mask'])
        self.assertTrue( np.all( batch['testcam2_mask'] == [0,0,1,0]) )
        #print('eee testcam2',batch['testcam2'])
        self.assertTrue( np.all( batch['testcam2'] == np.array([
                                                            [[[0.,0.,0.]]],
                                                            [[[0.,0.,0.]]],
                                                            [[[255.,255.,255.]]],
                                                            [[[255.,255.,255.]]],
        ]) ) )
        
        

if __name__ == '__main__':
    unittest.main()
