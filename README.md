# TrafficSignDetection

## About 
This project is aimed at answering the following question: How effective can object detection algorithms be at understanding different traffic signs? This project consists of a machine learning part and an object-oriented programming part. The machine learning part of the product comes first and utilizes the yolov5 object detection algorithm (after training with hundreds of traffic signs) to analyze traffic signs and come up with a prediction on what type of traffic sign was presented (for example, a stop sign). Once this process has been completed the image name and the prediction are written to a text file that gets used by the second part of our product: a simulation. The simulation is a multi-thread program that uses the pygame library to model a real-life traffic scenario. The simulation consists of bikes, trucks, cars, and buses moving across a four-way intersection. The car is the only vehicle moving downwards and is responsible for responding to a traffic sign that is rendered at the intersection. As the car approaches the test image, a different function (other than the one that is responsible for its normal movement) gets called, based on the prediction written in the text file, and the car responds appropriately. This sort of a mechanism of having a simulation after a machine learning part allows for better communication to audiences that may not have any technical expertise. 



## Steps to Rerun experiment:
0) Make sure that the following python libraries are installed: pytorch, pygame, time, random, threading, subprocess, os, and re 
1) Clone the github repository: git clone https://github.com/mishr100/TrafficSignDetection . Once cloned, there should be a folder called TrafficSignDetection under whichever folder the git clone command was ran from. 
2) Open up the folder in VSCode. Once the folder has been opened in VSCode, using the terminal window run the following command: python3 CollisionPrevention.py 
3) After step 2 the model should be acquiring predictions for test images. You should see various image names (i.e. stopsign.jpg) followed by a large amount of text and the prediction for what the sign is at the end. After one image is ran through yolov5 and the prediction is acquired, you should see a couple of dashed lines before the same thing happens with the next image. Once all the images are ran and predictions are acquired a 'classes.txt' file will be generated in the topmost directory. 
4) Once step 3 is done (it may take a minute), the simulation should pop up with the traffic sign and a car moving downward reacting to the traffic sign. 
5) The simulation will end once a collison occurs or when there have been two iterations of the car moving downward and off of the screen. 
