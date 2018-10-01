from io import BytesIO
from time import sleep
from picamera import PiCamera

from geppetto_client import Sensor

class PicamSensor(Sensor):
    def __init__(self, host, port, robot_name, sensor_name, width=2592/16, height=1944/16):
        self.dims = width, height
        self.image_gen = PiCamera().capture_continuous(BytesIO(), 'jpeg')
        super(PicamSensor, self).__init__(host, port, robot_name, sensor_name)
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        print('getting video')
        #return bytearray(b'1234567890')
        pic_stream = BytesIO()
        stream = self.image_gen.next()
        print('got video stream')
        stream.seek(0)
        pic_bytes = bytearray(stream.read())
        print('got video bytes')
        stream.truncate()
        print('emitting video frame from: %s (%s)'%(self.get_socketio_name(),len(pic_bytes)))
        #return bytearray(b'1234567890')
        return pic_bytes
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
