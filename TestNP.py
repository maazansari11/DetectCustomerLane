import cv2
import numpy as np
import  pickle
import subprocess
# image = cv2.imread('output/output-frame_00001.jpg')
# nparray = np.asarray(image)
# # print("before")
# # print(nparray)
# # s = pickle.dumps(nparray)
# # print(s)

# import numpy as np
import json

# img = np.ones((10, 20))
# img_str = json.dumps(nparray.tolist())
# print(img_str)
# nparray = pickle.loads(s)
# print("after")
# print(nparray)
# int_array = np.fromstring(nparray,dtype=int)
# print(int_array)
import DatabaseDetectCustomerLane
DB_URL_PATH = 'D:/SaranUseCase/ProjectDetectCustomerLane/USECASE.db'
video_id = 1
conn = DatabaseDetectCustomerLane.create_connection(DB_URL_PATH)

# DatabaseDetectCustomerLane.output_video_frames_sqllite(1,114,img_str)

FPS_LIST = DatabaseDetectCustomerLane.read_outptutvideo(conn, video_id)
if FPS_LIST[0] != None:
    FRAME_FPS = FPS_LIST[0]
else:
    print('n0 data');
# print(FPS)

data_list = DatabaseDetectCustomerLane.read_outptutvideoframes(conn, video_id)
# print(data_list)
from PIL import Image
# im = Image.fromarray(A)
# im.save("your_file.jpeg")
count = 1
for data in data_list:
    print(data)
    # if data[0] == 114:
    if data[1] != None and data[1] != 'null':
        img_numpy = np.array(json.loads(str(data[1])))
        print(img_numpy)
        im = Image.fromarray(img_numpy)
        filename = "test/test_{num:05d}.jpg'".format(num=count)
        count += 1
        im.save(filename)
# img_data =
import os
args = "ffmpeg/ffmpeg.exe -y -r "+ str(FRAME_FPS) +" -f image2 -i test/test_%05d.jpg  -vcodec libx264 -crf 25  -pix_fmt yuvj420p DetectCustomerOutput_test.mp4"
FNULL = open(os.devnull, 'w')  # use this if you want to suppress output to stdout from the subprocess
# args = "ffmpeg/ffmpeg.exe -y -r 5 -f image2 -i output/output-frame_%05d.jpg -vcodec libx264 -crf 25  -pix_fmt yuvj420p DetectCustomerOutput.mp4"
subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
