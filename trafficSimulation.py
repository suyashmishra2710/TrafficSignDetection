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
collisionCount = 0


#initializing pygame
pygame.init()
simulation = []

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
    # to make sure to update the position of the vehicle
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y)) 
    

    
    #updating the coordinates of each vehicle so that simulation has moving vehicles
    def move(self):
        if(self.direction == 'right'):
            self.x += self.speed #update the position of the vehicles that are moving right to keep moving right
            self.vehicleRect.right += self.speed
            #self.image.get_rect().right += self.speed
        elif(self.direction == 'left'):
            self.x -= self.speed #update the position of the vehicles that are moving left to keep moving left 
            self.vehicleRect.right -= self.speed 
            #self.image.get_rect().right -= self.speed
        elif(self.direction == 'down'):
            self.y += self.speed #update position of vehicles moving down to continue to move down 
            self.vehicleRect.bottom += self.speed
            #self.image.get_rect().top -= self.speed
        elif(self.direction == 'up'):
            self.y -= self.speed #update position of vehicles moving up to continue to move up 
            self.vehicleRect.bottom -= self.speed
            #self.image.get_rect().top += self.speed
        #if self.x <0 or self.x > 1400 or self.y < 0 or self.y > 800:
            #simulation.remove(self)
        self.collisionDetection()
    
    #def updateVehicleCount(self):
    '''
    idea is the following
    1) pygame's collision detection applies on rectangle objects 
    2) each vehicle's vehicleRect attribute is the rectangle object to use for collision detection among all vehicles
    3) each vehicle image (vehicle.image) is connected to its rectangle object (vehicle.vehicleRect) -- specifically the screen.blit part in the main class 
    '''
        
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
                sys.exit()
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
            time.sleep(0.2)
    
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
            screen.blit(vehicle.image, vehicle.vehicleRect)
            vehicle.move()
            
        pygame.display.update()
        