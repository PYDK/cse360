

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
    BASES1 = 40

    try:
        dheight=0
        s1=BASES1
        while True:
            # Axis input: [left_vert, left_horz, right_vert, right_horz, left_trigger, right_trigger]
            # Button inputs: [A, B, X, Y]
            axis, buttons = joystick.getJoystickInputs()


            if PRINT_JOYSTICK:
                print(" ".join(["{:.1f}".format(num) for num in axis]), buttons)
                
        
            dheight += (axis[0]*-1)*0.05
            print(dheight, " ", axis[5])


            # Send through serial port
            serial.send_control_params(ROBOT_MAC, (dheight, 0, axis[5], s1, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            time.sleep(.1)
            
    except KeyboardInterrupt:
        print("Stopping!")
    # Send zero input
    serial.send_control_params(ROBOT_MAC, (0, 0, 90, 90, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    serial.close()
