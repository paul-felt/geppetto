from io import BytesIO
from time import sleep
from picamera import PiCamera

try:
    # Create an in-memory stream
    #my_stream = BytesIO()
    camera = PiCamera()
    #camera.start_preview()
    # Camera warm-up time
    sleep(2)
    while True:
        my_stream = open('/tmp/image.jpg', 'w')
        camera.capture(my_stream, 'jpeg', resize=(600,480))
        my_stream.close()
        sleep(1)
finally:
    my_stream.close()
    #camera.stop_preview()
    camera.close()
