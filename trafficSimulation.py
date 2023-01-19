import sys 
sys.path.append('/Users/suyash/miniconda3/lib/python3.9/site-packages')
import time 
import pygame
import random 
import threading 

#necessary constants
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike':2.5} #average speed of vehicles 
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



#initializing pygame
pygame.init()
simulation = pygame.sprite.Group()

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
            simulation.add(self)
    # to make sure to update the position of the vehicle
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y)) 
    
    def collisionDetection(self, veh_xCord, veh_yCord):
        if self.x in veh_xCord:
            #terminate the simulation by pausing it for a year 
            # NOTE: if possible find the way to permenantly pause the simulation 
            # rather than for set amount of time 
            print("X coordinate matches another x coordinate")
            pygame.time.delay(31536000000) # keep the simulation paused for a year if vehicles collide 
        elif self.y in veh_yCord:
            #terminate the simulation by pausing it 
            # NOTE: if possible find the way to permenantly pause the simulation 
            # rather than for set amount of time
            print("Y coordinate matches another y coordinate")
            pygame.time.delay(31536000000) # keep the simulation paused for a year if vehicles collide
        veh_xCord.append(self.x)
        veh_yCord.append(self.y)
    
    #updating the coordinates of each vehicle so that simulation has moving vehicles
    def move(self):
        if(self.direction == 'right'):
            self.x += self.speed #update the position of the vehicles that are moving right to keep moving right
        elif(self.direction == 'left'):
            self.x -= self.speed #update the position of the vehicles that are moving left to keep moving left 
        elif(self.direction == 'down'):
            self.y += self.speed #update position of vehicles moving down to continue to move down 
        elif(self.direction == 'up'):
            self.y -= self.speed #update position of vehicles moving up to continue to move up 
        #self.collisionDetection()
    
    #def updateVehicleCount(self):
    '''
    idea is the following
    1) if vehicle is moving upwards/downwards but exceeds the y coordinate that is displayable remove it from the simulation array 
    2) if vehicle is moving left/right but exceeds the x coordinate that is displayable remove it from the simulation array
    '''
        
            
    
    def collisionDetection(self):
        #PROBLEM: simulation keeps vehicles that have also left the screen 
        # once a vehicle has left the screen need to remove it from the 
        # simulation array before checking for colliding rectangles
        
        
        for v1 in simulation:
            for v2 in simulation:
                if v1 != v2:
                    if v1.x == v2.x or v1.y == v2.y:
                        print("waiting")
                        pygame.time.wait(31536000000)  
class Main:
    def generateVehicles():
        while(True):
            vehicle_type = random.randint(0,3) # the random vehicle created
            lane_number = random.randint(1,2) # the lane in particular direction 
            temp = random.randint(0,99)
            direction_number = 0
            dist= [10,20,60,100]
            if(temp<dist[0]):
                direction_number = 0
            elif(temp<dist[1]):
                direction_number = 1
            elif(temp<dist[2]):
                direction_number = 2
            elif(temp<dist[3]):
                direction_number = 3
            Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
            time.sleep(1)
    
    black = (0, 0, 0)
    white = (255, 255, 255) 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)
    background = pygame.image.load('images/intersection.png')
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("TRAFFIC SIMULATION")
    
    # the driving force behind coordinating the display of our simulation 
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()
    firstRun = 0 #to easily be able to add object collision detection 
    list_veh = [] # adding all vehicles
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        screen.blit(background, (0, 0))
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()
        