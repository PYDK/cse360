# Untitled - By: thong - Fri Mar 29 2024

import pyb # Import module for board related functions
import sensor # Import the module for sensor related functions
import image # Import module containing machine vision algorithms
import time # Import module for tracking elapsed time

sensor.reset() # Resets the sensor
sensor.set_pixformat(sensor.RGB565) # Sets the sensor to RGB
sensor.set_framesize(sensor.QVGA) # Sets the resolution to 320x240 px
sensor.set_vflip(True) # Flips the image vertically
sensor.set_hmirror(True) # Mirrors the image horizontally
sensor.skip_frames(time = 2000) # Skip some frames to let the image stabilize

ledRed = pyb.LED(1) # Initiates the red led
ledGreen = pyb.LED(2) # Initiates the green led

while(True):
    # Define the min/max LAB values we're looking for
    thresholdsApple = (18, 39, 101, 19, 3, 38)
    thresholdsBanana = (85, 42, -16, 21, 26, 49)
    img = sensor.snapshot() # Takes a snapshot and saves it in memory

    # Find blobs with a minimal area of 50x50 = 2500 px
    # Overlapping blobs will be merged
    blobs = img.find_blobs([thresholdsApple, thresholdsBanana], area_threshold=2500, merge=True)

    clock = time.clock()

    # Draw blobs
    for blob in blobs:
        # Draw a rectangle where the blob was found
        img.draw_rectangle(blob.rect(), color=(0,255,0))
        # Draw a cross in the middle of the blob
        u = blob.cx()
        v = blob.cy()
        area = blob.area()
        angle = blob.cx()*0.0029-0.4374
        d = (1/blob.area())*81090+16.57
        img.draw_cross(u, v, color=(0,255,0))

        print(u, " ", v, " ", area, "\n")
        print(angle, " ", d)

    # Turn on green LED if a blob was found
    if len(blobs) > 0:
        ledGreen.on()
        ledRed.off()
    else:
    # Turn the red LED on if no blob was found
        ledGreen.off()
        ledRed.on()
