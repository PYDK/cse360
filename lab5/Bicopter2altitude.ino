/**
 * BICOPTER with altitude control
 * This code runs a bicopter with altitude control using the feedback from a barometer.
 * For this example, your robot needs a barometer sensor.
 */

#include "BlimpSwarm.h"
#include "robot/RobotFactory.h"
#include "comm/BaseCommunicator.h"
#include "comm/LLC_ESPNow.h"
#include "util/Print.h"
#include "sense/Barometer.h"
#include <Arduino.h>
#include <ESP32Servo.h>


// MAC of the base station
uint8_t base_mac[6] = {0xC0, 0x49, 0xEF, 0xE3, 0x34, 0x78};  // fixme load this from memory


Barometer baro;

const float TIME_STEP = .01;
// Robot
Robot* myRobot = nullptr;
// Communication
BaseCommunicator* baseComm = nullptr;
// Control input from base station
ControlInput cmd;

float estimatedZ = 0;
float startHeight = 0;
float estimatedVZ = 0;
float kpz = 0;
float kdz = 0;
float FLOAT_SPEED = 0.2;

Preferences preferences; //initialize the preferences 
bool updateParams = true;

void setup() {
    Serial.begin(115200);
    Serial.println("Start!");

    // init communication
    baseComm = new BaseCommunicator(new LLC_ESPNow());
    baseComm->setMainBaseStation(base_mac);

    // init robot with new parameters
    myRobot = RobotFactory::createRobot("RawBicopter");

    // Start sensor
    baro.init();
    baro.updateBarometer();
    estimatedZ = baro.getEstimatedZ();
    startHeight = baro.getEstimatedZ();
    estimatedVZ = baro.getVelocityZ();
    paramUpdate();
}


void loop() {

    if (baseComm->isNewMsgCmd()){
      // New command received
      cmd = baseComm->receiveMsgCmd();
      if (int(cmd.params[11]) == 1 && updateParams){
        paramUpdate();
        updateParams = false;
      } else {
        updateParams = true;
      }
      // Print command
      Serial.print("Cmd arrived: ");
      printControlInput(cmd);
    }

    // Update measurements
    if (baro.updateBarometer()){
      // sense 
      float height = baro.getEstimatedZ() - startHeight;
      float height_velocity = baro.getVelocityZ();
      // estimate
      estimatedZ = estimatedZ * .6 + height * .4;
      estimatedVZ = estimatedVZ * .9 + height_velocity * .1;
      
    }


    /**
     * Begin of Controller for Height:
     * Create your height PID to control m1 and m2 here.
     * kpz and kdz are changed from the ground station and are floats declared at the top
     */
    
    float desired_height = cmd.params[0];
    float range = 0.1;
    
    float height_diff = desired_height - estimatedZ;
    float kp = 0.5;
    float zPosition = kp * height_diff;

    float velocity_diff = 0 - estimatedVZ;
    float kd = 0.12;
    float zVelocity = kd * velocity_diff;


    float motorSpeed = zPosition + zVelocity + FLOAT_SPEED;
    if(motorSpeed - 1 > 0) {
      motorSpeed = 1;
    }
    if(motorSpeed < 0.06) {
      motorSpeed = 0.06;
    }

    Serial.print(estimatedZ);
    Serial.print(", ");
    Serial.print(estimatedVZ);
    Serial.print(", ");
    Serial.println(motorSpeed);
    float m1 = motorSpeed;  // YOUR INPUT FOR THE MOTOR 1 HERE
    float m2 = motorSpeed;
    
      // YOUR INPUT FOR THE MOTOR 1 HERE
    /**
     * End of controller
     */
    // Control input
    ControlInput actuate;
    // servo control
    if(cmd.params[2] > 0) {
      actuate.params[2] = 40-40*(cmd.params[2]); //cmd.params[2]; // Servo 1
      actuate.params[3] = 40-40*(cmd.params[2]); //cmd.params[3]; // Servo 2
      m1 *= 1.5;
      m2 *= 1.5;
      
    } else {
      actuate.params[2] = 40; //cmd.params[2]; // Servo 1
      actuate.params[3] = 40; //cmd.params[3]; // Servo 2
    }

    actuate.params[0] = m1; // Motor 1
    actuate.params[1] = m2; // Motor 2
    actuate.params[4] = cmd.params[4]; //led
    // Send command to the actuators
    myRobot->actuate(actuate.params, 5);

    sleep(TIME_STEP);
}


void paramUpdate(){
    preferences.begin("params", true); //true means read-only

    kpz = preferences.getFloat("kpz", .2); //(value is an int) (default_value is manually set)
    kdz = preferences.getFloat("kdz", 0); //(value is an int) (default_value is manually set)
    

    Serial.print("Update Paramters!");
    Serial.print(kpz);
    Serial.print(", ");
    Serial.println(kdz);
    preferences.end();
}