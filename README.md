# TrafficSignDetection

Steps to Rerun experiment:
1) Clone the github repository: git clone https://github.com/mishr100/TrafficSignDetection . Once cloned, there should be a folder called TrafficSignDetection under whichever folder the git clone command was ran from. 
2) Open up the folder in VSCode. Once the folder has been opened in VSCode, using the terminal window run the following command: python3 CollisionPrevention.py 
3) After step 2 the model should be acquiring predictions for test images. You should see various image names (i.e. stopsign.jpg) followed by a large amount of text and the prediction for what the sign is at the end. After one image is ran through yolov5 and the prediction is acquired, you should see a couple of dashed lines before the same thing happens with the next image. Once all the images are ran and predictions are acquired a 'classes.txt' file will be generated in the topmost directory. 
4) Once step 3 is done (it may take a minute), the simulation should pop up with the traffic sign and a car moving downward reacting to the traffic sign. 
5) The simulation will end once a collison occurs or when there have been two iterations of the car moving downward and off of the screen. 
