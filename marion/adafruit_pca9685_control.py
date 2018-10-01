import geppetto_client
# Import the PCA9685 module.
import Adafruit_PCA9685

## Helper function to make setting a servo pulse width simpler.
#from __future__ import division
#def set_servo_pulse(channel, pulse):
#    pulse_length = 1000000    # 1,000,000 us per second
#    pulse_length //= 50       # 60 Hz
#    print('{0}us per period'.format(pulse_length))
#    pulse_length //= 4096     # 12 bits of resolution
#    print('{0}us per bit'.format(pulse_length))
#    pulse *= 1000
#    pulse //= pulse_length
#    pwm.set_pwm(channel, 0, pulse)

class AdaFruitPCA9685Control(geppetto_client.Control):
    def __init__(self, host, port, robot_name, servo_name, channel, pwm_frequency=50, min_limit=200, max_limit=400):
        self.channel = channel
        self.min_limit = min_limit
        self.max_limit = max_limit
        # Initialise the PCA9685 using the default address (0x40).
        self.pwm = Adafruit_PCA9685.PCA9685()
        # Set frequency 
        self.pwm.set_pwm_freq(pwm_frequency)
        super(AdaFruitPCA9685Control, self).__init__(host, port, robot_name, servo_name)
    def get_limits(self):
        return self.min_limit, self.max_limit
    def apply_control(self, signal):
        print('%s-%s: applying control %s' % (self.robot_name,self.signal_name, signal))
        assert self.min_limit <= signal and signal <= self.max_limit
	self.pwm.set_pwm(self.channel, 0, int(signal))

