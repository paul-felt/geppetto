import client

class PWMServo(client.Control):
    def __init__(self, robot_name, servo_name, gpio_pin):
        self.gpio_pin = gpio_pin
        super(PWMServo, self).__init__(robot_name, servo_name)
    def get_limits(self):
        return 1000, 2000
    def apply_control(self, signal):
        assert 1000 < signal and signal < 2000
        self.pi.set_servo_pulsewidth(self.gpio_pin, signal)

client.register_control(PWMServo('arm-swiv', 1))
#client.register_control(PWMServo('arm-horz', 2))
#client.register_control(PWMServo('arm-vert', 3))
#client.register_control(PWMServo('arm-claw', 4))
