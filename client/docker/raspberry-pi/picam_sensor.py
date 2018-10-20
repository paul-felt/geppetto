from io import BytesIO
from time import sleep
from picamera import PiCamera
from geppetto_client import Sensor

class PicamSensor(Sensor):
    def __init__(self, robot_name, sensor_name, width=2592/24, height=1944/24, **camargs):
        self.dims = int(width), int(height)
        self.camargs = camargs
        self.image_gen = None
        super(PicamSensor, self).__init__(robot_name, sensor_name)
    def get_mediatype(self):
        return 'video'
    def get_reading(self):
        if self.image_gen is None:
            print('initializing camera with resolution: %s'%str(self.dims))
            self.cam = PiCamera()
            # apply user-supplied settings
            for key,val in self.camargs.items():
                setattr(self.cam, key, val)
            self.image_gen = self.cam.capture_continuous(BytesIO(), 'jpeg', resize=self.dims, use_video_port=True)
        #print('getting video')
        #return b'1234567890'
        stream = next(self.image_gen)
        # read out bytes
        stream.seek(0)
        pic_bytes = stream.read()
        # reset stream for next capture
        stream.seek(0) 
        stream.truncate()
        #print('emitting video frame from: %s (%s)'%(self.get_socketio_name(),len(pic_bytes)))
        return pic_bytes
    def cleanup(self):
        print('initializing camera with resolution: %s'%str(self.dims))
        self.cam.close()
        self.cam = None
        self.image_gen = None
