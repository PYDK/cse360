

from comm.Serial import SerialController, DataType_Int, DataType_Float
from joystick.JoystickManager import JoystickManager
import time

##### Insert your robot's MAC ADDRESS here ####
## (you can get it by running your arduino and looking at the serial monitor for your flying drone) ##
ROBOT_MAC = "34:85:18:91:24:F0" # "DC:54:75:D7:B3:E8"
### Insert your SERIAL PORT here ###
## may look like "COM5" in windows or "/dev/tty.usbmodem14301" in mac  #
## look in arduino for the port that your specific transeiver is connected to  ##
## Note: make sure that your serial monitor is OFF in arduino or else you will get "access is denied" error. ##
PORT = "COM6"


# For debug purposes
PRINT_JOYSTICK = False


BaseStationAddress = "" # you do not need this, just make sure your DroneMacAddress is not your base station mac address



if __name__ == "__main__":
    # Communication
    serial = SerialController(PORT, timeout=.1)  # 5-second timeout
    serial.manage_peer("A", ROBOT_MAC)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kpz", .6)
    serial.send_preference(ROBOT_MAC, DataType_Float, "kdz", .8)
    serial.send_control_params(ROBOT_MAC, (0,0,90,90, 0, 0, 0, 0, 0, 0, 0, 1, 0)) #refresh parameters
    time.sleep(.2)

    # Joystick
    joystick = JoystickManager()
    BASES1 = 90
    BASES2 = 90

    try:
        m1=0
        m2=0
        s1=BASES1
        s2=BASES2
        b = False
        c=0
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()


            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)

            #### CONTROL INPUTS to the robot here #########
            if m1 < 0.05 and ((abs(axis[0])-0.2)) > 0 and axis[0]*-1*0.005 > 0:
                m1 = 0.05
            else:
                m1 += (axis[0]*-1)*0.005  # Motor 1: a value between 0-1  
            if m1 > 1:
                m1 = 1
            if m1 < 0:
                m1 = 0
            m2 += (axis[0]*-1)*0.005  # Motor 2: a value between 0-1
            if m2 > 1:
                m2 = 1
            if m2 < 0:
                m2 = 0 
            rightDiff = (abs(axis[4]) - 0.2)
            if rightDiff <= 0:
                rightDiff = 0
            if rightDiff == 0:  
                if (abs(axis[5]) - 0.3) <= 0 and (abs(axis[2]) - 0.3) <= 0:
                    axis[2] = 0
                    axis[5] = 0
                if axis[5] > 0:
                    s1 = 50  # Servo 1: a value between 0-180
                    s2 = 130  # Servo 2: a value between 0-180
                elif axis[2] > 0:
                    s1 = 130  # Servo 1: a value between 0-180
                    s2 = 50  # Servo 2: a value between 0-180
                else:
                    s1 = BASES1
                    s2 = BASES2
            else:
                if rightDiff != 0:
                    s1 = 90+axis[4]*20
                    s2 = 90+axis[4]*20
                else:
                    s1= BASES1
                    s2 = BASES2
            if s1 > 180:
                s1 = 180
            if s1 < 0:
                s1 = 0
            if s2 > 180:
                s2 = 180
            if s2 < 0:
                s2 = 0
            led = axis[0]
            ############# End CONTROL INPUTS ###############

            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (m1, m2, s1, s2, led, 0, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(.1)
            
    except KeyboardInterrupt:
        print("Stopping!")
    # Send zero input
    serial.send_control_params(ROBOT_MAC, (0, 0, 90, 90, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    serial.close()
