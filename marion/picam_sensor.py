from io import BytesIO
from time import sleep
from picamera import PiCamera

from geppetto_client import Sensor

class PicamSensor(Sensor):
    def __init__(self, host, port, robot_name, sensor_name, width=2592/16, height=1944/16):
        self.dims = width, height
        self.camera = PiCamera()
        super(PicamSensor, self).__init__(host, port, robot_name, sensor_name)
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        print('getting video')
        return {'video': b'1234567890'}
        #pic_stream = BytesIO()
        #self.camera.capture(pic_stream, 'jpeg', resize=self.dims)
        #frame = pic_stream.getvalue()
        #print('emitting video frame from: %s (%s)'%(self.get_socketio_name(),len(frame)))
        #return {'video': frame}
    #def close(self):
    #    self.camera.close()

#try:
#    # Create an in-memory stream
#    #my_stream = BytesIO()
#    camera = PiCamera()
#    #camera.start_preview()
#    # Camera warm-up time
#    sleep(2)
#    while True:
#        my_stream = open('/tmp/image.jpg', 'w')
#        camera.capture(my_stream, 'jpeg', resize=(600,480))
#        my_stream.close()
#        sleep(1)
#finally:
#    my_stream.close()
#    #camera.stop_preview()
#    camera.close()
