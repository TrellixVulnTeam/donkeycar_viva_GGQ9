from datetime import datetime
import donkeycar as dk
import re
import time
import logging
from donkeycar.parts.actuator import RobocarsHat
from donkeycar.utilities.logger import init_special_logger

mylogger = init_special_logger ("Rx")
mylogger.setLevel(logging.INFO)


class RobocarsHatIn:
    def __init__(self, cfg):

        self.cfg = cfg
        self.inSteering = 0.0
        self.inThrottle = 0.0
        self.inAux1 = 0.0
        self.inAux2 = 0.0

        self.sensor = RobocarsHat(self.cfg)
        self.on = True

    def map_range(self, x, X_min, X_max, Y_min, Y_max):
        '''
        Linear mapping between two ranges of values
        '''
        X_range = X_max - X_min
        Y_range = Y_max - Y_min
        XY_ratio = X_range/Y_range

        return ((x-X_min) / XY_ratio + Y_min)


    def update(self):

        while self.on:
            start = datetime.now()

            l = self.sensor.readline()
            if l != None:
                params = l.split(',')
                if len(params) == 5 and int(params[0])==1 :
                    if params[0].isnumeric():
                        self.inThrottle = self.map_range(int(params[1]),
                                self.cfg.ROBOCARSHAT_PWM_IN_THROTTLE_MIN, self.cfg.ROBOCARSHAT_PWM_IN_THROTTLE_MAX,
                            -1, 1)
                    if params[2].isnumeric():
                        self.inSteering = self.map_range(int(params[2]),
                            self.cfg.ROBOCARSHAT_PWM_IN_STEERING_MIN, self.cfg.ROBOCARSHAT_PWM_IN_STEERING_MAX,
                            -1, 1)
                    if params[3].isnumeric():
                        self.inAux1 = self.map_range(int(params[3]),
                            self.cfg.ROBOCARSHAT_PWM_IN_AUX_MIN, self.cfg.ROBOCARSHAT_PWM_IN_AUX_MAX,
                            -1, 1)
                    if params[4].isnumeric():
                        self.inAux2 = self.map_range(int(params[4]),
                            self.cfg.ROBOCARSHAT_PWM_IN_AUX_MIN, self.cfg.ROBOCARSHAT_PWM_IN_AUX_MAX,
                            -1, 1)
                    mylogger.debug("CtrlIn {} {} {} {}".format(int(params[1]), int(params[2]), int(params[3]), int(params[4])))
            stop = datetime.now()
            s = 0.01 - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)

    def run_threaded(self):

        recording=False
        mode='user'
        user_throttle = self.inThrottle
        if (self.inAux2>0):
            recording=True
        if (self.inAux1>0.5):
            mode='local_angle'
            user_throttle = self.cfg.ROBOCARSHAT_LOCAL_ANGLE_FIX_THROTTLE
        return self.inSteering, user_throttle, mode, recording

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stopping Robocars Hat Controller')
        time.sleep(.5)
