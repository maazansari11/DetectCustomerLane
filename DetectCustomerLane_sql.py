
# from ProjectDetectCustomerLane import algo_obj_collision_detection
import DatabaseDetectCustomerLane
import algo_obj_collision_detection
import time
import numpy as np
import pickle
POWER_AI_VISION_API_URL = "https://10.150.20.61/powerai-vision/api/dlapis/e9b61ba4-bf7e-47b5-88a2-282ba1323871"


CLEAN = False  # USE WITH CARE! Wipe out saved files when this is true (else reuse for speed)
input_video_url = "TASJEEL JAFZA C11 (2-5).mp4"  # The input video
START_LINE = 0  # If start line is > 0, cars won't be added until below the line (try 200)
FRAMES_DIR = "frames"  # Output dir to hold/cache the original frames
OUTPUT_DIR = "output"  # Output dir to hold the annotated frames
SAMPLING = 1  # Classify every n frames (use tracking in between)
CONFIDENCE = 0.80  # Confidence threshold to filter iffy objects

# OpenCV colors are (B, G, R) tuples -- RGB in reverse
WHITE = (255, 255, 255)
YELLOW = (66, 244, 238)
GREEN = (80, 220, 60)
LIGHT_CYAN = (255, 255, 224)
RED = (0, 0, 255)
DARK_BLUE = (139, 0, 0)
TRANSPARENT = (255, 255, 255)
BLUE_LIGHT = {135, 206, 235}
GRAY = (128, 128, 128)


line_left_x1 = 464
line_left_y1 = 243
line_left_x2 = 902
line_left_y2 = 1529
line_right_x1 = 771
line_right_y1 = 246
line_right_x2 = 1824
line_right_y2 = 1529
INDEX_LIST = []


import json
import glob
import math
import os
import shutil

import cv2
# from IPython.display import clear_output, Image, display
import requests
import urllib3
import subprocess
urllib3.disable_warnings()
print("Warning: Certificates not verified!")

#get_ipython().magic(u'matplotlib notebook')

# ## Download the video
# This will download a small example video.
#

# In[ ]:


#get_ipython().system(u'wget {input_video_url}')
input_video = input_video_url.split('/')[-1]

# ## Create or clean the directories
# Caching the frames and output directories allows the processing to continue where it left off. This is particularly useful when using a shared system with deployment time limits. This also allows you to quickly `Run all` when tweaking Python code that does not affect the inference.
#
# If you change the input video or just want a fresh start, you should `CLEAN` or change the directory names.


if CLEAN:
    if os.path.isdir(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

if not os.path.isdir(FRAMES_DIR):
    os.mkdir(FRAMES_DIR)
if not os.path.isdir(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

# ## Parse and explode the video file into JPEGs
# Each frame is saved as an individual JPEG file for later use.


if os.path.isfile(input_video):
    video_capture = cv2.VideoCapture(input_video)
else:
    raise Exception("File %s doesn't exist!" % input_video)

total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
print("Frame count estimate is %d" % total_frames)

num = 0
total_frames = 100
already_created = False
IS_ENABLE_DEBUG = True
start_time_value = time.time() /1000
# while video_capture.get(cv2.CAP_PROP_POS_FRAMES) < video_capture.get(cv2.CAP_PROP_FRAME_COUNT):
if already_created == False:
    while video_capture.get(cv2.CAP_PROP_POS_FRAMES) < total_frames:
        success, image = video_capture.read()
        if success:
            num = int(video_capture.get(cv2.CAP_PROP_POS_FRAMES))
            print("Writing frame {num} of {total_frames}".format(
                num=num, total_frames=total_frames))
            cv2.imwrite('{frames_dir}/frame_{num:05d}.jpg'.format(
                frames_dir=FRAMES_DIR, num=num), image)
        else:
            # TODO: If this happens, we need to add retry code
            raise Exception('Error writing frame_{num:05d}.jpg'.format(
                num=int(video_capture.get(cv2.CAP_PROP_POS_FRAMES))))
            # continue

print("\nWrote {num} frames".format(num=num))
if IS_ENABLE_DEBUG:
    time_val = (time.time()/1000) - start_time_value
    print('time taken to make frame::'+str(time_val))
FRAME_FPS = int(video_capture.get(cv2.CAP_PROP_FPS))
FRAME_WIDTH = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
ROI_YMAX = int(round(FRAME_WIDTH * 0.55))  # Bottom quarter = finish line
ROI_YMAX1 = int(round(FRAME_WIDTH * 0.25))  # Bottom quarter = finish line
print("Frame Dimensions: %sx%s" % (FRAME_WIDTH, FRAME_HEIGHT))



s = requests.Session()


def detect_objects(filename):
    # with open(filename, 'rb') as f:
    #     # WARNING! verify=False is here to allow an untrusted cert!
    #     r = s.post(POWER_AI_VISION_API_URL,
    #                files={'files': (filename, f)},
    #                verify=False)
    #
    # return r.status_code, json.loads(r.text)
    rc1 = 0
    resp_value = None

    retry_count = 0
    while (rc1 != 200) and (retry_count < 5):
        # print("retry_count=%d" % retry_count)
        if retry_count != 0:
            print("retrying upload for  attempt %d" % retry_count)

        # r = requests.post(endpoint, files=myfiles, verify=False)
        # rc = r.status_code
        with open(filename, 'rb') as f:
            try:
                r = s.post(POWER_AI_VISION_API_URL,
                              files={'files': (filename, f)},
                              verify=False, timeout=10)
                rc1 = r.status_code
                # print("status code = %d " %rc1)
            except Exception as exc:
                print('generated an exception: %s' % exc)
                rc1 = 0
                retry_count = retry_count + 1
                continue
            # WARNING! verify=False is here to allow an untrusted cert!

        retry_count = retry_count + 1
        resp_value = json.loads(r.text)
    # finally:
    # lock.release()  # release lock, no matter what
    if r != None:
        rc1 = r.status_code
    else:
        rc1 = 409
    # rs_value = ''
    # if resp_value.get(' != None:
    #     rs_value = resp_value['classified']
    # print(rc)
    return rc1, resp_value


# ## Test the API on a single frame
# Let's look at the result of a single inference operation from the PowerAI Vision Object Detection API. We see a standard HTTP return code, and a JSON response which includes the image URL, and tuples that indicate the confidence and bounding-box coordinates of the objects that we classified.

# In[ ]:


rc, jsonresp = detect_objects('frames/frame_00001.jpg')

print("rc = %d" % rc)
print("jsonresp: %s" % jsonresp)
if 'classified' in jsonresp:
    print("Got back %d objects" % len(jsonresp['classified']))
print(json.dumps(jsonresp, indent=2))

# ## Get object detection results for sampled frames
# Since we've stored all video frames on disk (for easy reference), we can iterate over those files
# and make queries as appropriate to PowerAI Vision's API. We'll store the results in a
# `tracking_results` dictionary, organized by file name. Since we are tracking objects from frame
# to frame, we can use sampling to decide how often to check for new objects.
#
# We're also caching the results so that you can change later code and run the notebook over
# without running the same inference over again.



# Serialize requests, storing them in a "tracking_results" dict

try:
    with open('frames/frame-data-newmodel.json') as existing_results:
        tracking_results = json.load(existing_results)
except Exception:
    # Any fail to read existing results means we start over
    tracking_results = {}

print("Sampling every %sth frame" % SAMPLING)
import os
#print('Check file seprator::::::::::::::::::::::'+os.sep)
i = 0
cache_used = 0
sampled = 0
time_val_current = 0
if IS_ENABLE_DEBUG:
    time_val_current = time.time()/1000
    # time_val = (start_time_value - time.time())/1000
    # print('time taken to make frame::'+str(time_val))

for filename in sorted(glob.glob('frames/frame_*.jpg')):
    #print('fileName::::::::::::::::::'+filename)
    i += 1
    if i > total_frames:
        break

    if not i % SAMPLING == 0:  # Sample every Nth
        continue

    existing_result = tracking_results.get(filename)

    if existing_result and existing_result['result'] == 'success':
        cache_used += 1
    else:
        #rc, results = detect_objects(filename)
        rc, results = detect_objects('frames/'+filename[7:])
        if rc != 200 or results['result'] != 'success':
            print("ERROR rc=%d for %s" % (rc, filename))
            print("ERROR result=%s" % results)
        else:
            sampled += 1
            # Save frequently to cache partial results
            tracking_results[filename] = results
            with open('frames'+os.sep+'frame-data-newmodel.json', 'w') as fp:
                json.dump(tracking_results, fp)

    print("Processed file {num} of {total_frames} (used cache {cache_used} times)".format(
        num=i, total_frames=total_frames, cache_used=cache_used))

if IS_ENABLE_DEBUG:
    time_val = (time.time()/1000) - time_val_current
    print('time taken for web api call::'+str(time_val))


# Finally, write all our results
with open('frames'+os.sep+'frame-data-newmodel.json', 'w') as fp:
    json.dump(tracking_results, fp)

print("\nDone")


# ## Define helper functions for tracking and drawing labels
# Refer to the [OpenCV docs.](https://docs.opencv.org/3.4.1/)

# In[ ]:


def label_object(image, xmax, xmin, ymax, ymin):
    # cv2.rectangle(image, (xmin, ymin), (xmax, ymax),  (0, 255, 0), 2)
    # pos = (xmid - textsize[0] // 2, ymid + textsize[1] // 2)
    cv2.line(image, (line_left_x1, line_left_y1), (line_left_x2, line_left_y2), RED, 4, cv2.LINE_AA)
    cv2.line(image, (line_right_x1, line_right_y1), (line_right_x2, line_right_y2), RED, 4, cv2.LINE_AA)
    # cv2.putText(image, "Person Detected in testing lane", (30, 30), fontface, 1, textcolor, 1, cv2.LINE_AA)


def update_trackers(image, counters):
    left_lane = counters['left_lane']
    right_lane = counters['right_lane']
    boxes = []
    color = (80, 220, 60)
    fontface = cv2.FONT_HERSHEY_SIMPLEX
    fontscale = 1
    thickness = 1

    for n, pair in enumerate(trackers):
        tracker, person = pair
        textsize, _baseline = cv2.getTextSize(
            person, fontface, fontscale, thickness)
        success, bbox = tracker.update(image)

        # if not success:
        #     counters['lost_trackers'] += 1
        #     del trackers[n]
        #     continue

        boxes.append(bbox)  # Return updated box list

        xmin = int(bbox[0])   #(x1,y1,x2,y2)
        ymin = int(bbox[1])
        xmax = int(bbox[2])
        ymax = int(bbox[3])
        # print(xmin,xmax,ymin,ymax)
        xmid = int(round((xmin + xmax) / 2))
        ymid = int(round((ymin + ymax) / 2))

        overlay = image.copy()

        # Shade region of interest (ROI). We're really just using the top line.
        cv2.rectangle(overlay,
                  (0, ROI_YMAX),
                  (FRAME_WIDTH, FRAME_HEIGHT), TRANSPARENT, cv2.FILLED)

        cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)


    return boxes, counters


# In[ ]:


def not_tracked(objects, boxes):
    if not objects:
        return []  # No new classified objects to search for
    if not boxes:
        return objects  # No existing boxes, return all objects

    new_objects = []
    for obj in objects:
        ymin = obj.get("ymin", "")
        ymax = obj.get("ymax", "")
        ymid = int(round((ymin + ymax) / 2))
        xmin = obj.get("xmin", "")
        xmax = obj.get("xmax", "")
        xmid = int(round((xmin + xmax) / 2))
        box_range = ((xmax - xmin) + (ymax - ymin)) / 2
        for bbox in boxes:
            bxmin = int(bbox[0])
            bymin = int(bbox[1])
            bxmax = int(bbox[0] + bbox[2])
            bymax = int(bbox[1] + bbox[3])
            bxmid = int((bxmin + bxmax) / 2)
            bymid = int((bymin + bymax) / 2)
            if math.sqrt((xmid - bxmid) ** 2 + (ymid - bymid) ** 2) < box_range:
                # found existing, so break (do not add to new_objects)
                break
        else:
            new_objects.append(obj)

    return new_objects


# In[ ]:


def in_range(obj):
    ymin = obj['ymin']
    ymax = obj['ymax']
    if ymin < START_LINE or ymax > ROI_YMAX:
        # Don't add new trackers before start or after finish.
        # Start line can help avoid overlaps and tracker loss.
        # Finish line protection avoids counting the car twice.
        return False
    return True


def add_new_object(obj, image, index):
    print("person %d" % index)
    car = str(index)
    xmin = obj['xmin']
    xmax = obj['xmax']
    ymin = obj['ymin']
    ymax = obj['ymax']
    # xmid = int(round((xmin + xmax) / 2))
    # ymid = int(round((ymin + ymax) / 2))
    fontface = cv2.FONT_HERSHEY_SIMPLEX
    fontscale = 1
    thickness = 1
    textsize, _baseline = cv2.getTextSize(
        car, fontface, fontscale, thickness)

    obj_in_roi = algo_obj_collision_detection.Object_in_ROI(xmin, xmax, ymin, ymax, line_left_x1,
                                                            line_left_y1, line_left_x2, line_left_y2,
                                                            line_right_x1, line_right_y1, line_right_x2,
                                                            line_right_y2)

    print(obj_in_roi.isvoilation_with_midpoint())
    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    if obj_in_roi.isvoilation_with_midpoint():
        INDEX_LIST.append(index)
        label_object(image, xmax, xmin, ymax, ymin)




cars = 0
trackers = []
counters = {
    'left_lane': 0,
    'right_lane': 0,
    'lost_trackers': 0,
    'frames': 0,
}

with open('frames/frame-data-newmodel.json') as existing_results:
    tracking_results = json.load(existing_results)
import numpy as np
import datetime
watermark = cv2.imread('logo.png', cv2.IMREAD_UNCHANGED)
(wH, wW) = watermark.shape[:2]
(B, G, R, A) = cv2.split(watermark)
B = cv2.bitwise_and(B, B, mask=A)
G = cv2.bitwise_and(G, G, mask=A)
R = cv2.bitwise_and(R, R, mask=A)
watermark = cv2.merge([B, G, R, A])

# watermark1 = cv2.imread('Capture.png', cv2.IMREAD_UNCHANGED)
# (wH1, wW1) = watermark1.shape[:2]
# (B, G, R, A) = cv2.split(watermark1)
# B = cv2.bitwise_and(B, B, mask=A)
# G = cv2.bitwise_and(G, G, mask=A)
# R = cv2.bitwise_and(R, R, mask=A)
# watermark1 = cv2.merge([B, G, R, A])
if IS_ENABLE_DEBUG:
    time_val_current = time.time() /1000

counter = 1
for filename in sorted(glob.glob('frames/frame_*.jpg')):
    counters['frames'] += 1
    img = cv2.imread(filename)
    cv2.line(img, (line_left_x1, line_left_y1), (line_left_x2, line_left_y2), LIGHT_CYAN, 4, cv2.LINE_AA)
    cv2.line(img, (line_right_x1, line_right_y1), (line_right_x2, line_right_y2), LIGHT_CYAN, 4, cv2.LINE_AA)
    if counter > total_frames:
        break
    boxes, counters = update_trackers(img, counters)

    if filename in tracking_results and 'classified' in tracking_results[filename]:
        jsonresp = tracking_results[filename]
        # for obj in not_tracked(jsonresp['classified'], boxes):

        for obj in jsonresp['classified']:
            # TODO add label object here in add_new_obejct
            # if in_range(obj):
            #     cars += 1
            add_new_object(obj, img, counter)  # Label and start tracking
    counter += 1

    (h, w) = img.shape[:2]
    img = np.dstack([img, np.ones((h, w), dtype="uint8") * 255])
    overlay = np.zeros((h, w, 4), dtype="uint8")
    overlay[10:wH+10, w - wW - 10:w - 10] = watermark
    output = img.copy()
    cv2.addWeighted(overlay, 0.75, output, 1.0, 0, output)
    cv2.imwrite("output/output-" + filename.split(os.sep)[1], img)
    print("Processed file {num} of {total_frames}".format(
        num=counters['frames'], total_frames=total_frames))

print("\nDone")
if IS_ENABLE_DEBUG:
    time_val = time.time() /1000 - time_val_current
    print('processing json response on frame::'+str(time_val))
counter_resize = 1

if IS_ENABLE_DEBUG:
    time_val_current = time.time() /1000

for filename in sorted(glob.glob(os.path.join(os.path.abspath(OUTPUT_DIR),
                                              'output-frame_*.jpg'))):
    if counter_resize > total_frames:
        break
    counter_resize += 1
    frame = cv2.imread(filename)
#    clear_output(wait=True)
    rows, columns, _channels = frame.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    frame = cv2.resize(frame, (int(columns / 2), int(rows / 2)))  # shrink it
    _ret, jpg = cv2.imencode('.jpg', frame)
#    display(Image(data=jpg))

print("\nDone")
if IS_ENABLE_DEBUG:
    time_val = time.time() /1000 - time_val_current
    print('frame resize time taken::'+str(time_val))
# ## Create a video from the annotated frames
#
# This command requires `ffmpeg`. It will combine the annotated
# frames to build an MP4 video which you can play at full speed
#Create ouput video as per index
start_index = 0
end_index =  0
second = 5
count_video = 1
if IS_ENABLE_DEBUG:
    time_val = time.time() /1000 - time_val_current
    # print('processing json response on frame::'+str(time_val))
for index in INDEX_LIST:
    if index > end_index:
        temp_start = index - (second * FRAME_FPS)
        end_index = index + (second * FRAME_FPS)
        if temp_start > 0:
            start_index = temp_start
        else:
            start_index =  1

        if end_index > total_frames:
            end_index = total_frames
        print('***********************')
        print(index)
        print(start_index)
        print(end_index)
        print('***********************')
        # //MAIN OUTPUT_VIDEO   EVENTS  == VTC1  VIDEIO_ID = count_video   FEED_LOCATION ==Location_id entry
        DatabaseDetectCustomerLane.write_output_video_sqllite('vt1',count_video,1,FRAME_FPS)
        # for loop for images start index and end index
        # each frame you will take np_array
        #insert in OUTPUT_VIDEIO_FRAMES  count_video, counter + =1 np_array
        # -start_number 1 - i test_ % d.jpg - vframes 100
        # args = "ffmpeg/ffmpeg.exe -y -r "+ str(FRAME_FPS) +" -start_number "+str(start_index)+" -f image2 -i output/output-frame_%05d.jpg -vframes "+str(end_index)+" -vcodec libx264 -crf 25  -pix_fmt yuvj420p DetectCustomerOutput"+str(count_video)+".mp4"
        # FNULL = open(os.devnull, 'w')  # use this if you want to suppress output to stdout from the subprocess
        # # args = "ffmpeg/ffmpeg.exe -y -r 5 -f image2 -i output/output-frame_%05d.jpg -vcodec libx264 -crf 25  -pix_fmt yuvj420p DetectCustomerOutput.mp4"
        # subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
        temp_count = 1
        for start_index in range(end_index):
            filename = 'output/output-frame_{num:05d}.jpg'.format(num=start_index)
            temp_image = cv2.imread(filename)
            np_array = np.asarray(temp_image)
            str_array = json.dumps(np_array.tolist())
            DatabaseDetectCustomerLane.output_video_frames_sqllite(count_video,temp_count,str_array)
            temp_count += 1

        count_video += 1
if IS_ENABLE_DEBUG:
    time_val = time.time() /1000 - time_val_current
    print('processing with sql lite::'+str(time_val))
# FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
# args = "ffmpeg/ffmpeg.exe -y -r 5 -f image2 -i output/output-frame_%05d.jpg -vcodec libx264 -crf 25  -pix_fmt yuvj420p DetectCustomerOutput.mp4"
# subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
if IS_ENABLE_DEBUG:
    time_val_current = time.time() /1000
    time_val = time_val_current - start_time_value
    print('total time taken::'+str(time_val))