from threading import Thread, Lock
import keyboard
import pyautogui
import cv2 as cv
import numpy as np
from time import time, sleep
import math
import win32api, win32con

key_a = 0x41
key_d = 0x44
key_w = 0x57
key_s = 0x53

class MovementHandler:

    stopped = True
    found = False

    bigscreen = (1920, 1080)
    screen_w = None
    screen_h = None
    screen_pos = None

    destinations = []
    character_x = None
    character_y = None


    def __init__(self, screen_w, screen_h):
        self.lock = Lock()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.character_x = self.screen_w // 2
        self.character_y = self.screen_h // 2

    def calculate_center(self, obj):
        obj_center_x = obj[0] + (obj[2] / 2 if len(obj) > 2 else 0)  # Calculate object center x if obj[2] exists
        obj_center_y = obj[1] + (obj[3] / 2 if len(obj) > 3 else 0)  # Calculate 

        return (obj_center_x, obj_center_y)

    def calculate_distance(self, obj1, obj2):
        x1, y1 = self.calculate_center(obj1)
        x2, y2 = self.calculate_center(obj2)

        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance
    
    def update_screen_relative_pos(self, screen_pos):
        self.screen_pos = screen_pos
        
    def move_towards_destination(self, object_center_x, object_center_y):   
        #print(f'Moving to object {object_center_x},{object_center_y}')
        distance_x = object_center_x - self.character_x
        distance_y = object_center_y - self.character_y
        key = None

        distance_to_target = self.calculate_distance((self.character_x, self.character_y), self.find_closest())

        if distance_to_target < 50:
            self.found = True
            click_x, click_y = self.screen_pos
            click_x, click_y = (self.character_x + click_x, self.character_y + click_y + 20)
            win32api.SetCursorPos((click_x,click_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
            sleep(5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
            return
        
        self.found = False

        if not self.found:
            if distance_x >= 10:
                # Move Right
                key = key_d
                win32api.keybd_event(key, 0, 0, 0)

            elif distance_x < 10:
                # Move Left
                key = key_a
                win32api.keybd_event(key, 0, 0, 0)

            if distance_y >= 10:
                # Move Down
                key = key_s
                win32api.keybd_event(key, 0, 0, 0)

            elif distance_y < 10:
                # Move Up
                key = key_w
                win32api.keybd_event(key, 0, 0, 0)
        
            sleep(0.1)
            win32api.keybd_event(key_a, 0, win32con.KEYEVENTF_KEYUP, 0) 
            win32api.keybd_event(key_d, 0, win32con.KEYEVENTF_KEYUP, 0) 
            win32api.keybd_event(key_w, 0, win32con.KEYEVENTF_KEYUP, 0) 
            win32api.keybd_event(key_s, 0, win32con.KEYEVENTF_KEYUP, 0) 

    def move_right(self):
        keyboard.press('d')
        sleep(0.1)
        keyboard.release('d')
    

    def update_destination(self, destinations):
        self.lock.acquire()
        self.destinations = destinations
        self.lock.release()

    def clear_destinations(self):
        self.lock.acquire()
        self.destinations = []
        self.lock.release()

    def find_closest(self):
        closest_distance = float('inf')
        closest_coordinate = None

        for coord in self.destinations:
            obj_center_x, obj_center_y = self.calculate_center(coord)
            distance = math.sqrt((obj_center_x - self.character_x)**2 + (obj_center_y - self.character_y)**2)

            if distance < closest_distance:
                closest_distance = distance
                closest_coordinate = coord
        
        return closest_coordinate

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            if len(self.destinations) > 0:
                
                object_center_x, object_center_y, w, h= self.find_closest()

                self.lock.acquire()
                self.move_towards_destination(object_center_x, object_center_y)
                self.lock.release()

        sleep(1)
