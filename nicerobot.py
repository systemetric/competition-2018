import time

import sr.robot
from sr.robot import (
    INPUT, OUTPUT, INPUT_ANALOG, INPUT_PULLUP,
    MARKER_ARENA, MARKER_TOKEN, MARKER_BUCKET_SIDE, MARKER_BUCKET_END
)

__all__ = [
    "MARKER_ARENA", "MARKER_TOKEN", "MARKER_BUCKET_SIDE", "MARKER_BUCKET_END",
    "INPUT", "OUTPUT", "INPUT_ANALOG", "INPUT_PULLUP",
]

TOKEN = object()
BUCKET = object()

SERVO_ARM = 0
SERVO_LEFT = 2
SERVO_RIGHT = 1

GPIO_GATE = 1
GPIO_PUMP = 2

MULTIPLIER_LEFT = -1
MULTIPLIER_RIGHT = 0.95  # 0.91

SPEED_50 = 1.25 / 3
SPEED_100 = 1.7 * SPEED_50 * 1.25
SPEED_ANGULAR_30 = 360 / 4.25


markers = []


class Robot(sr.robot.Robot):
    def __init__(self):
        super(Robot, self).__init__()

        self.gpio.pin_mode(GPIO_GATE, OUTPUT)
        self.gpio.pin_mode(GPIO_PUMP, OUTPUT)
        self.gpio.digital_write(GPIO_GATE, True)
        self.servos[SERVO_RIGHT] = 0
        self.servos[SERVO_LEFT] = 0

    def move(self, distance):
        self.servos[SERVO_LEFT] = MULTIPLIER_LEFT * 50
        self.servos[SERVO_RIGHT] = MULTIPLIER_RIGHT * 50

        time.sleep(distance / SPEED_50)

        self.servos[SERVO_RIGHT] = 0
        self.servos[SERVO_LEFT] = 0

    def turn(self, angle):
        multiplier = 1
        if angle < 0:
            multiplier = -1
        self.servos[SERVO_LEFT] = MULTIPLIER_LEFT * 30 * multiplier
        self.servos[SERVO_RIGHT] = MULTIPLIER_RIGHT * -30 * multiplier

        time.sleep(abs(angle) / SPEED_ANGULAR_30)

        self.servos[SERVO_RIGHT] = 0
        self.servos[SERVO_LEFT] = 0

    def pickup_cube(self):
        self.servos[SERVO_ARM] = -100
        time.sleep(1)
        self.gpio.digital_write(GPIO_PUMP, True)
        time.sleep(1)
        self.servos[SERVO_ARM] = 100
        time.sleep(0.5)

    def succ(self):
        self.pickup_cube()

    def pump_on(self):
        self.gpio.digital_write(GPIO_PUMP, True)

    def drop(self):
        self.gpio.digital_write(GPIO_PUMP, False)

    def go_to(self, marker_type):
        if marker_type is TOKEN:
            acceptable_types = [MARKER_TOKEN]
            print("Looking for a token...")
        elif marker_type is BUCKET:
            acceptable_types = [MARKER_BUCKET_SIDE, MARKER_BUCKET_END]
            print("Looking for a bucket...")
        else:
            raise ValueError("Invalid marker_type")

        while True:
            markers = self.see()
            acceptable_markers = [m for m in markers if m.info.marker_type in acceptable_types]
            if acceptable_markers:
                dest = acceptable_markers[0]
                print("Found marker {} (dist {}, rot_y {})".format(
                    dest.info.code, dest.dist, dest.rot_y
                ))
                self.turn(dest.rot_y)
                time.sleep(0.3)
                self.move(dest.dist)
                return
            # no good markers visible
            print("Didn't find any acceptable markers, turning to try again")
            self.turn(45)
            time.sleep(0.3)
