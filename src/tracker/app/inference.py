### local model 

import requests
import time
import asyncio

import cv2
import os

import numpy as np
import time
import threading
import imutils

from collections import deque

# from colour_finder import *

LOCAL_ENDPOINT = os.environ["MODEL_ENDPOINT"]

## old values .. just so that I can remember


headers = {'Content-Type': 'application/octet-stream'}

save_response = None

async def local_predict(img,local=False):
    
    global save_response
    
    is_success, im_buf_arr = cv2.imencode(".jpg", img)
    byte_im = im_buf_arr.tobytes()
    
    # call face api to find all faces
    response = requests.post(LOCAL_ENDPOINT, headers = headers, data = byte_im)
    
    save_response = response
    
    return response.json()


THRESHOLD = float(os.environ["MODEL_THRESHOLD"])

bboxes =  []
thread_counter = 0

colours = {'with-mask-improper':  (0,255,0),
           'with-mask-proper': (0,191,255),
           'without-mask':   (255,165,0)}

TRACKER = 'KCF' # let us try this one

# initialize a dictionary that maps strings to their corresponding
# OpenCV object tracker implementations
OPENCV_OBJECT_TRACKERS = {
    "CSRT": cv2.legacy.TrackerCSRT_create,
    "KCF": cv2.legacy.TrackerKCF_create,
    "MIL": cv2.legacy.TrackerMIL_create,
    "MOSSE": cv2.legacy.TrackerMOSSE_create
}
# initialize OpenCV's special multi-object tracker
trackers = cv2.legacy.MultiTracker_create()

tracker = OPENCV_OBJECT_TRACKERS[TRACKER]()

import time


async def analyse_image(frame,local=False,verbose=0):

    global bboxes, trackers, tracker, thread_counter

    thread_counter += 1
   
    height,width = frame.shape[:2]   
    
    # predict 
    results = await local_predict(imutils.resize(frame, width=300),local=local)
 
    # if len(results['boxes']) > 0:
    if len(results['predictions']) > 0:
        new_trackers = cv2.legacy.MultiTracker_create()
        bboxes = []

        # add AI found boxes
        # for prediction in results['boxes']:
        for prediction in results['predictions']:

            # if prediction['score'] >= THRESHOLD:
            if prediction['probability'] >= THRESHOLD:

                # colour = colours[prediction['label']]
                colour = colours[prediction['tagName']]

                # tag = f"{prediction['label']} {prediction['score']*100:.2f}%"
                tag = f"{prediction['tagName']} {prediction['probability']*100:.2f}%"

                bboxes.append((colour,tag))

                # l_p = round(prediction['box']['topX'] * width)
                # r_p = round(prediction['box']['bottomX'] * width)
                # t_p = round(prediction['box']['topY'] * height)
                # b_p = round(prediction['box']['bottomY'] *  height)
                # box = (l_p,t_p,r_p-l_p,b_p-t_p)

                l_p = round(prediction['boundingBox']['left'] * width)
                w_p = round(prediction['boundingBox']['width'] * width)
                t_p = round(prediction['boundingBox']['top'] * height)
                h_p = round(prediction['boundingBox']['height'] *  height)
                box = (l_p,t_p,w_p,h_p)

                # added to tracker
                tracker = OPENCV_OBJECT_TRACKERS[TRACKER]()
                new_trackers.add(tracker, frame, box)
        

        trackers = new_trackers   

    thread_counter -= 1






class _GoCheckModel(threading.Thread):
    def __init__(self,frame,local):
        self.frame = frame
        self.local = local
        super().__init__()
    def run(self):
        asyncio.run(analyse_image(self.frame,local=self.local))

class FPSTimer():
    
    def __init__(self,cap):
        
        self.cap = cap
        self.last_call = None
        
    def sleep(self):
        per_frame = 1.0 / self.cap.get(cv2.CAP_PROP_FPS)
        slack = 0.0
        if self.last_call:            
            slack = per_frame - (time.time() - self.last_call)
            if slack > 0:
                time.sleep(slack)
        self.last_call = time.time()
        return slack

class ImgQueue():
    def __init__(self,size=0):
        self.size = size
        self.queue = deque([])
    def append(self,img):
        self.queue.append(img)
    def get_next(self):
        if len(self.queue) > self.size:
            return self.queue.popleft()
        else:
            return None

def analyse_video_fast(video,send=None,local=True,extract_freq=1,analyse_freq=50):
    
    global bboxes, trackers

    bboxes = []
    
    # start the file video stream thread and allow the buffer to
    # start to fill
    # print("[INFO] starting video file thread...")
    
    # try:
    cap = cv2.VideoCapture(video)
    
    extract_count = 0
    analyse_count = 0
        
    fps = cap.get(cv2.CAP_PROP_FPS)

    img_queue = ImgQueue(int(analyse_freq)) # will get eahd of time one cycle

    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    if fps == 0:
        return

    # fpsTimer = FPSTimer(cap)


    # loop over frames from the video file stream
    while True:
        
        try:
            # grab the frame from the threaded video file stream
            ret, new_image = cap.read()
            
            if ret:
                # using a queue to estabilise images
                img_queue.append(new_image)

            elif frame is None: 
                #### NB .. this only happens if both ret is False and frame is None!
                break

            # will display the next element in the queue
            frame = img_queue.get_next()
            
            if frame is None:
                # fpsTimer.sleep() # it needs to be here to make the best adjustment
                continue
            
            if extract_freq > 1:

                # counting before, so that zero is NOT ignored
                extract_count += 1

                if extract_count % extract_freq != 0: 
                    # fpsTimer.sleep() # adjust time
                    continue            

            if analyse_count % analyse_freq == 0 and new_image is not None: 
                ### NB ... will check "NEW_IMAGE", not frame!
                _GoCheckModel(new_image,local=local).start() 
            
            # counting aftwards, to ensure zero is counted
            analyse_count += 1
                
            (success, boxes) = trackers.update(frame)
            # loop over the bounding boxes and draw then on the frame
            for indx,box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                
                try:
                    (colour,tag) = bboxes[indx]
                except:
                    (colour,tag) = ((0,0,0),"")
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), colour, 2)                
                cv2.rectangle(frame, (x, y-20), (x+150,y), colour, -1)
                
                cv2.putText(frame,tag, (x+5,y-5), cv2.FONT_HERSHEY_PLAIN , 1.0, (0,0,0), 1)

                # blur
                try:
                    frame[ y:y+h, x:x+w ] = cv2.blur(frame[y:y+h, x:x+w], (23, 23))
                except:
                    pass

            if send:
                 asyncio.run(send(frame))

            # fpsTimer.sleep() # it needs to be here to make the best adjustment

        except:
            break

    cap.release()
