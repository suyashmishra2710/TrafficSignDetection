import sys 
sys.path.append('/Users/suyash/miniconda3/lib/python3.9/site-packages')
import time 
import pygame
import random 
import threading
import subprocess
import os
import re 

#necessary constants and offsets
vel = 5
collisionCheckDist = 150 #the number of x,y units that will be checked. Making this smaller should make the simulation run smaller.
upDownOffset = 1
leftRightOffset = 1

#speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike':2.5} #average speed of vehicles 
speeds = {'car': 2.25, 'bus': 1.5, 'truck': 1.8, 'bike':2.5} #average speed of vehicles 
x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}
vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}
# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stoppingGap = 15    # stopping gap
movingGap = 15   # moving gap
driverAssigned = False # represents whether there is one car responsible for looking and responding to traffic signs
simulation_over = 0 # 0 for when simulation is still running, 1 for when simulation is over 
collisionCount = 0 # counts the number of collisions in trials 
totalTrials = 0 # counts the total number of simulation trials (so that we can add percentage of trials that have a collison )
lastDirection = 999999

#initializing pygame
pygame.init()
simulation = []

#-------------- added from merging the simulation code -------------------------------------#
def get_model_predictions():
    os.chdir('./yolov5/img')
    files_output = (subprocess.run('ls', capture_output=True)).stdout.decode().strip()
    filenames = files_output.split('\n')
    os.chdir('..')
    os.chdir('..')
    f = open("classes.txt", "w")
    os.chdir('./yolov5')
    for imageName in filenames:
        print(imageName)
        output = str(subprocess.run(f'python3 detect.py --weights best.pt --source img/{imageName}', shell=True, capture_output=True, text=True))
        print(output)
        indices = re.search(r"\d+x\d+ ", output)
        start = indices.span()[1]
        indices = re.search(r", \d+.\dms", output)
        end = indices.span()[0]
        classes = output[start:end]
        classList = classes.split(', ')
        trafficSign = classList[-1]
        print(classes)
        print(trafficSign)
        print("-----")
        f.write(f'{imageName} {trafficSign}\n')
    os.chdir('..')
    return 

# this function reads through the classes.txt file in order to figure out 
# what test image file name will get rendered and what the neural network 
#predicts it to be 
def displayTestImage():
    with open('./classes.txt', 'r') as tests:
        k = random.randint(1, 4)
        for i in range(0, k):
            line = tests.readline()
            line = line.split()
    filePath = f'./yolov5/img/{line[0]}' # extract the image by using the property the first part until the space will be an image file
    if line[1] == '(no':
        return filePath, 'Not Detected'
    else:
        return filePath, line[2]


def renderTestSign(screen):
    testSign = pygame.image.load(imgPath)
    testSign = pygame.transform.scale(testSign, (100, 100))
    screen.blit(testSign, (800, 225))

# this function checks if the "loading zone" of the particular direction the vehicle is moving in is not occupied 
def checkZones(direction_number):
    # want to know all the vehicles that are present in the simulation so zone checking can be done 
    veh_list = []
    veh_rectlist = []
    for vehicle in simulation:
        veh_list.append(vehicle)
        veh_rectlist.append(vehicle.vehicleRect)
        # check the rightbox zone
    if direction_number == 0:
        rightRect = pygame.Rect(0, 340, 100, 90)
        zoneCheck = rightRect.collidelist(veh_rectlist)
        # check the downbox zone 
    elif direction_number == 1:
        downRect = pygame.Rect(680, 0, 90, 100)
        zoneCheck = downRect.collidelist(veh_rectlist)
        #check the leftbox zone 
    elif direction_number == 2:
        leftRect = pygame.Rect(1310, 340, 100, 90)
        zoneCheck = leftRect.collidelist(veh_rectlist)
        # check the up box zone 
    elif direction_number == 3:  
        upRect = pygame.Rect((590, 700, 90, 100))
        zoneCheck = upRect.collidelist(veh_rectlist)
    if zoneCheck != -1:
        return False 
    return True 
#------------------------------------- end of first set of merging simulation code ----------------------------------

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleType, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane 
        self.vehicleType = vehicleType # this stores whether the vehicle is bus, car, truck, etc 
        self.speed = speeds[vehicleType] # uses the predefined constants to assign speed to appropriate vehicle
        self.direction_number = direction_number #tracks whether vehicle is moving up, down, left, or right 
        self.direction = direction # the direction in text format 
        self.x = x[direction][lane] # x coordinate of moving vehicle 
        self.y = y[direction][lane] # y coordinate of moving vehicle 
        self.crossed = 0 #represents whether vehicle has crossed intersection 
        self.isDriver = 0 #represents whether or not vehicle is responsible for observing + responding to traffic signs
        vehicles[direction][lane].append(self) # keeping track of all vehicles in same lane and direction as current one
        self.index = len(vehicles[direction][lane]) - 1 # keeps track of number of vehicles in same lane (way to index through it)
        # for vehicle loading and rendering to screen
        path = "images/" + direction + "/" + vehicleType + ".png" 
        self.image = pygame.image.load(path)
        self.stop = 0
        self.vehicleRect = self.image.get_rect(topleft = [self.x, self.y])
        self.waiting = 0
        
        
        #checks if there are cars in same lane and direction as current vehicle 
        # if so we need to set the value of stop and consider width and height 
        # of vehicles in front 
        if (len(vehicles[direction][lane])> 1 and vehicles[direction][lane][self.index-1].crossed==0):
            if(direction == 'right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap 
            elif(direction == 'left'):
                self.stop = vehicles[direction][lane][self.index-1].stop  + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif(direction == 'down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif(direction == 'up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap  
            else:
                self.stop = defaultStop[direction]

        
        #updating coordinates so that new vehicles can't be generated on existing ones 
            if(direction=='right'):
                temp = self.image.get_rect().width + stoppingGap    
                x[direction][lane] -= temp
            elif(direction=='left'):
                temp = self.image.get_rect().width + stoppingGap
                x[direction][lane] += temp
            elif(direction=='down'):
                temp = self.image.get_rect().height + stoppingGap
                y[direction][lane] -= temp
            elif(direction=='up'):
                temp = self.image.get_rect().height + stoppingGap
                y[direction][lane] += temp
            simulation.append(self)
            #print(simulation)

    # to make sure to update the position of the vehicle
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y)) 
    
    # below are functions for different responses the car going downwards may carry out 
    # as it is approaching/predicting a traffic sign 
    
    # appropriate response if the car is predicting there to be a stop sign 
    def stopResponse(self):
        if abs(self.y - 350) > 50 or self.waiting > 100:
            self.y += self.speed #update position of vehicles moving down to continue to move down 
            self.vehicleRect.bottom += self.speed 
        else:
            self.waiting += 1
            
    #appropriate response if the car is predicting there to be a yield sign 
    def yieldResponse(self):
        if abs(self.y - 350) > 100 or self.waiting > 100:
            self.y += self.speed
            self.vehicleRect.bottom += self.speed
        else:
            self.y += self.speed / 2
            self.vehicleRect.bottom += self.speed / 2
            self.waiting += 1
    
    # appropriate response to a speed limit sign (if car is going to far below the speed limit)
    def speedUpResponse(self):
        if self.y - 350 < -50:
            self.y += self.speed 
            self.vehicleRect.bottom += self.speed 
        else:
            self.y += self.speed * 3
            self.vehicleRect.bottom += (self.speed * 3)
    
    # appropriate response to a speed limit sign (if car is going to far above the speed limit)  
    def slowDownResponse(self):
        if self.y - 350 < -50:
            self.y += self.speed 
            self.vehicleRect.bottom += self.speed 
        else:
            self.y += (self.speed / 2)
            self.vehicleRect.bottom += (self.speed / 2)
    
    #normal response -- car keeps moving 
    def normalResponse(self):
        self.y += self.speed 
        self.vehicleRect.bottom += self.speed
    
    def laneChangeResponse(self):
        # the striped white squares are at y coordinate 350
        # so all lane changes, speed changes, etc should occur 
        # as the image approaches y coordinate of 350
        if self.y > 340 and self.y < 350 and self.lane == 2:
            self.x += 33 # for moving from the left lane to the right lane 
            self.vehicleRect.right += 33 # for moving from the left lane to the right lane 
            self.vehicleRect.bottom += 10
            self.y += 10
            self.lane = 1 # making sure (for later debugging purposes) that the lane car appears in and what's stored here is consistent
            print(self.lane)
        elif self.y > 340 and self.y < 350 and self.lane == 1:
            self.x -= 33 # for moving from the right lane to the left lane 
            self.vehicleRect.right -= 33 # for moving from the right lane to the left lane 
            self.vehicleRect.bottom += 10
            self.y += 10
            self.lane = 2
            print(self.lane)
        else:
            self.normalResponse()
            
    
        
    #updating the coordinates of each vehicle so that simulation has moving vehicles
    def move(self, imgPath, pred):
        checkPossCollison = False
        for vehicle2 in simulation:
            if (self.vehicleRect == vehicle2.vehicleRect):
                    continue
            if (self.direction == 'up'):
                checkPossCollison = self.checkUp(self.vehicleRect, vehicle2.vehicleRect)
            elif (self.direction == 'down'):
                checkPossCollison = self.checkDown(self.vehicleRect, vehicle2.vehicleRect)
            elif (self.direction == 'right'):
                checkPossCollison = self.checkRight(self.vehicleRect, vehicle2.vehicleRect)
            else:
                checkPossCollison = self.checkLeft(self.vehicleRect, vehicle2.vehicleRect)
            if checkPossCollison == True:
                self.vehicleRect.right += 0
                vehicle2.vehicleRect.right += 0
                time.sleep(0.01)
                return imgPath, pred
        '''
        checkPossCollison = False # to get returned from the checkUp, checkDown, checkRight, and left func
        for vehicle1 in simulation:
            for vehicle2 in simulation:
                if (vehicle1 == vehicle2 or vehicle1.lane == vehicle2.lane):
                    continue
                if (self.direction == 'up'):
                    checkPossCollison = self.checkUp(vehicle1.vehicleRect, vehicle2.vehicleRect)
                elif (self.direction == 'down'):
                    checkPossCollison = self.checkDown(vehicle1.vehicleRect, vehicle2.vehicleRect)
                elif (self.direction == 'right'):
                    checkPossCollison = self.checkRight(vehicle1.vehicleRect, vehicle2.vehicleRect)
                else:
                    checkPossCollison = self.checkLeft(vehicle1.vehicleRect, vehicle2.vehicleRect)
                if checkPossCollison == True:
                    break
        '''
        if(self.direction == 'right'):
            self.x += self.speed #update the position of the vehicles that are moving right to keep moving right
            self.vehicleRect.right += self.speed    
        elif(self.direction == 'left'):
            self.x -= self.speed #update the position of the vehicles that are moving left to keep moving left 
            self.vehicleRect.right -= self.speed 
        elif(self.direction == 'down'):
            if pred == 'stop':
                self.stopResponse()  
            elif pred == 'yield': 
                self.yieldResponse()
            elif pred == 'speed up':
                self.speedUpResponse()
            elif pred == 'speed down':
                self.slowDownResponse()
            elif pred == 'merge':
                self.laneChangeResponse()
            else:
                self.normalResponse()
        elif(self.direction == 'up'):
            self.y -= self.speed #update position of vehicles moving up to continue to move up 
            self.vehicleRect.bottom -= self.speed
        if self.x <0 or self.x > 1400 or self.y < 0 or self.y > 800:
            if self.direction == 'down':
                imgPath, pred = displayTestImage() 
            simulation.remove(self)
        #self.collisionDetection() #This should do nothing if the collision detections work
        '''
        for vehicle1 in simulation:
            for vehicle2 in simulation:
                if (vehicle1 == vehicle2 or vehicle1.lane == vehicle2.lane):
                    continue
                if (self.direction == 'up'):
                    self.checkUp(vehicle1.vehicleRect, vehicle2.vehicleRect)
                elif (self.direction == 'down'):
                    self.checkDown(vehicle1.vehicleRect, vehicle2.vehicleRect)
                elif (self.direction == 'right'):
                    self.checkRight(vehicle1.vehicleRect, vehicle2.vehicleRect)
                else:
                    self.checkLeft(vehicle1.vehicleRect, vehicle2.vehicleRect)
        '''
        self.collisionDetection()
        return imgPath, pred


                

    #def updateVehicleCount(self):
    '''
    idea is the following
    1) pygame's collision detection applies on rectangle objects 
    2) each vehicle's vehicleRect attribute is the rectangle object to use for collision detection among all vehicles
    3) each vehicle image (vehicle.image) is connected to its rectangle object (vehicle.vehicleRect) -- specifically the screen.blit part in the main class 
    '''
    def pause_simulation(self):
        global simulation_over
        global collisionCount
        simulation_over = 1
        collisionCount += 1
    def pause_simulation_PS(self):
        global simulation_over
        #global collisionCount
        simulation_over = 3
        #collisionCount += 1

    # all of these checking functions return True if there is a collision that is going to happen 
    def checkUp(self, rect1, rect2):
        for i in range(1, collisionCheckDist):
            if (rect1.y - i == rect2.y and abs(rect1.x - rect2.x) < upDownOffset):
                print("Possible collision top")
                self.print_collision_info(rect1, rect2)
                return True
        return False
    def checkDown(self, rect1, rect2):
        for i in range(1, collisionCheckDist):
            if (rect1.y + i == rect2.y and abs(rect1.x - rect2.x) < upDownOffset):
                print("Possible collision back")
                self.print_collision_info(rect1, rect2)
                return True
        return False

    #I'm not sure how changing the heading of the car affects things so I added a left and right check.
    def checkRight(self, rect1, rect2):
        for i in range(1, collisionCheckDist):
            if (rect1.x + i == rect2.x and abs(rect1.y - rect2.y) < leftRightOffset):
                print("Possible collision right")
                self.print_collision_info(rect1, rect2)
                return True 
        return False

    def checkLeft(self, rect1, rect2):
        for i in range(1, collisionCheckDist):
            if (rect1.x - i == rect2.x and abs(rect1.y - rect2.y) < leftRightOffset):
                print("Possible collision left")
                self.print_collision_info(rect1, rect2)
                return True 
        return False
    
    def print_collision_info(self, rect1, rect2):
        #print("line 241")
        #return
        #print out some information regrading which cars may be getting hit
        print("Vehcile 1 type: " + self.vehicleType + " lane number: " 
                + str(self.lane) + " direction num: " 
                + str(self.direction_number))
        
        print("rect1 coord:")
        print("(" + str(rect1.x) + ", " + str(rect1.y) + ")")
        print("rect2 coord:")
        print("(" + str(rect2.x) + ", " + str(rect2.y) + ")")
        #self.pause_simulation()

    def collisionDetection(self):
        #Here we have two working versions commented below 
        # the first one uses pygame's collidelist function 
        # the second one uses the pygame's colliderect function
        # idea is to figure out which one is faster and keep that one 
        # first one should appear to be faster because O(2n) time complexity vs O(n^2)
        
        global collisionCount
        # following two arrays are supposed to be indexed the same 
        # meaning that index 1 in veh_list (the vehicle) will correspond to index 1 in veh_rectlist (the vehicle's rectangle)
        veh_list = []
        veh_rectlist = []
        for vehicle in simulation:
            veh_list.append(vehicle)
            veh_rectlist.append(vehicle.vehicleRect)
        for vehicle in simulation:
            collisions = vehicle.vehicleRect.collidelist(veh_rectlist)
            if collisions != -1 and vehicle != veh_list[collisions]:
                print('collision')
                self.pause_simulation()
        '''
        global collisionCount
        for vehicle in simulation:
            for compare in simulation:
                if vehicle != compare:
                    collide = pygame.Rect.colliderect(vehicle.vehicleRect, compare.vehicleRect)
                    if collide:
                        print('Collided')
                        sys.exit()
        '''
    
                                              
class Main:
    def generateVehicles():
        while(True):
            global lastDirection
            carDown = False
            vehicle_type = random.randint(0,3) # the random vehicle created
            lane_number = random.randint(1,2) # the lane in particular direction 
            temp = random.randint(0,99)
            direction_number = 0
            dist= [25,50,75,100]
            if(temp<dist[0]):
                direction_number = 0
            # commented out because don't want vehicles other than cars moving downward
            #elif(temp<dist[1]):
                #direction_number = 1
            elif(temp<dist[2]):
                direction_number = 2
            elif(temp<dist[3]):
                direction_number = 3
            # all cars should be moving downward (only cars will be detecting and predicting traffic signs)
            if vehicle_type == 0:
                direction_number = 1
            # checking if there is a car moving downwards in the simulation - if so, don't want to create another car 
            for vehicle in simulation: 
                if vehicle.vehicleType == 'car':
                    carDown = True
                    break
            #print(f'Found a vehicle in simulation going downwards {carDown}')
            # render all vehicles if they aren't a car and only render cars if there isn't one currently going downwards 
            '''
            if vehicle_type != 0:
                Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
            elif not carDown:
                Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
            time.sleep(0.05)
            break
            '''
            zoneFree = checkZones(direction_number)
            if vehicle_type != 0 and direction_number != lastDirection and zoneFree: 
                Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
                lastDirection = direction_number
            elif not carDown and direction_number != lastDirection and zoneFree:
                Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
                lastDirection = direction_number
            time.sleep(0.01)
    
    #get_model_predictions()
    imgPath, pred = displayTestImage() #opens up the classes.txt file and returns the file path of the test image to display and prediction from neural network model
    
    # the driving force behind coordinating the display of our simulation 
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()
    
    black = (0, 0, 0)
    white = (255, 255, 255) 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)
    background = pygame.image.load('images/intersection.png')
    testSign = pygame.image.load(imgPath)
    testSign = pygame.transform.scale(testSign, (100, 100))
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("TRAFFIC SIMULATION")
    global simulation_over
    
    '''
    # the driving force behind coordinating the display of our simulation 
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()
    '''
    
    firstRun = 0 #to easily be able to add object collision detection 
    list_veh = [] # adding all vehicles
    #v1 = Vehicle(1, vehicleTypes[0], 1, directionNumbers[2])
    #v2 = Vehicle(2, vehicleTypes[1], 2, directionNumbers[1])
    #simulation.append(v1)
    #simulation.append(v2)
    while True:
        #generateVehicles()
        # for the coordinates of the zones to check if there's a vehicle in before rendering it in and needing to prevent a collision 
        # the third argument is in (x, y, width, height) format 
        pygame.draw.rect(screen, (255, 0, 0), (680, 0, 90, 100), 5) # downbox
        pygame.draw.rect(screen, (255, 0, 0), (0, 340, 100, 90), 5) # rightbox 
        pygame.draw.rect(screen, (255,0,0), (1310, 340, 100, 90), 5) # leftbox
        pygame.draw.rect(screen, (255,0,0), (590, 700, 90, 100), 5) #upbox
        #pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 2)
        #pygame.draw.line(screen, (255,0,0), (1400, 340), (1400, 430), 5)
        pygame.display.update()
        testSign = pygame.image.load(imgPath)
        testSign = pygame.transform.scale(testSign, (100, 100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    sys.exit()
        if simulation_over == 0:
            screen.blit(background, (0, 0)) # renders the entire intersection onto the screen
            screen.blit(testSign, (800, 225)) # renders the specific test image onto the screen for the car to read 
            for vehicle in simulation: 
                screen.blit(vehicle.image, vehicle.vehicleRect)
                #pygame.draw.line(screen, pygame.Color('black'), (700, 350), (900, 350)) # as you approach 350 want to stop 
                if vehicle.direction_number == 1:
                    pygame.draw.rect(screen, (255,0,0), vehicle.vehicleRect, 4)
                imgPath, pred = vehicle.move(imgPath, pred)
        elif simulation_over == 3:
            green = (255, 255, 255)
            blue = (0, 0, 0)
            X = 2200
            Y = 200
            endingMsg = pygame.font.Font('freesansbold.ttf', 32)
            txt = endingMsg.render('Simulation over: PS', True, green, blue)
            txtRect = txt.get_rect()
            txtRect.center = (X // 2, Y // 2)
            screen.blit(txt, txtRect)
            simulation_over = 3
        else: 
            green = (255, 255, 255)
            blue = (0, 0, 0)
            X = 2200
            Y = 200
            endingMsg = pygame.font.Font('freesansbold.ttf', 32)
            txt = endingMsg.render('Simulation over', True, green, blue)
            txtRect = txt.get_rect()
            txtRect.center = (X // 2, Y // 2)
            screen.blit(txt, txtRect)
            simulation_over = 1
                
            
            
            
            '''
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        simulation_over = 0  
                        simulation.clear()   
                        screen.blit(background, (0, 0))
                        count += 1
                        print(f'len of simulation is {len(simulation)}')
            '''
                        
            #print(f'Simulation over value is {simulation_over}')
            
            
        pygame.display.update()
    startGame(5)
        
