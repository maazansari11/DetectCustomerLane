import datetime
import json
import time
import os.path
import sqlite3
from datetime import datetime
FLAG_DEBUG = False
DB_URL_PATH = 'D:/SaranUseCase/ProjectDetectCustomerLane/USECASE.db'

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return None

def create_outputvideo(conn, output_insert_param):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO OUTPUT_VIDEO(EVENTS,VIDEO_ID,FEED_LOCATION_ID,FPS)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, output_insert_param)
    return cur.lastrowid


def create_outputvideoframes(conn, output_insert_param):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO OUTPUT_VIDEO_FRAMES(VIDEO_ID,COUNTER,FRAME_ARRAY)
              VALUES(?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, output_insert_param)
    return cur.lastrowid


def read_outptutvideo(conn, VIDEO_ID):
    sql = "SELECT FPS FROM OUTPUT_VIDEO WHERE VIDEO_ID="+str(VIDEO_ID)
    # print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    return_data = cur.fetchone()
    # print(cur.fetchone())
    return return_data

def read_outptutvideoframes(conn, VIDEO_ID):
    sql = "SELECT COUNTER, FRAME_ARRAY FROM OUTPUT_VIDEO_FRAMES WHERE VIDEO_ID="+str(VIDEO_ID)+" order by COUNTER ASC"
    # print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    return_data = cur.fetchall()
    # print(cur.fetchone())
    return return_data

def read_all(conn):
    # sql = "SELECT ID, TIME_STAMP FROM CAR_PLATE_NUMBERS WHERE PLATE_NUMBER=:plate",{"plate":str(plate_number)}
    # print(sql)
    cur = conn.cursor()
    cur.execute("SELECT * FROM OUTPUT_VIDEO")
    return_data = cur.fetchall()
    # print(cur.fetchone())
    return return_data

def read_all(conn):
    # sql = "SELECT ID, TIME_STAMP FROM CAR_PLATE_NUMBERS WHERE PLATE_NUMBER=:plate",{"plate":str(plate_number)}
    # print(sql)
    cur = conn.cursor()
    cur.execute("SELECT * FROM OUTPUT_VIDEO_FRAMES")
    return_data = cur.fetchall()
    # print(cur.fetchone())
    return return_data




def write_output_video_sqllite(events, video_id, feed_location_id,fps):
    insert_flag = False
    try:
        # create a database connection
        conn = create_connection(DB_URL_PATH)
        # time_stamp = datetime.now()
        with conn:
            # create a new project
            # YYYY - MM - DD
            # HH: MM:SS.SSS
            # time_stamp_str = time_stamp.strftime("%Y-%m-%d %H:%M:%S:%f")
            # if FLAG_DEBUG:
            #     print('time_stamp_str :: %s' % time_stamp_str)
            output_video_param = (events, video_id, feed_location_id,fps );
            car_id = create_outputvideo(conn, output_video_param)
            # if FLAG_DEBUG:
                # print('car id::%d  plate_number::%s time_stamp::%s' %(car_id,plate_number,time_stamp_str))
            insert_flag= True
    except sqlite3.Error  as exc:
        insert_flag = False
    return insert_flag

def output_video_frames_sqllite(video_id,counter,frame_array):
    # insert_flag = False
    car_id = -1
    try:
        # create a database connection
        conn = create_connection(DB_URL_PATH)
        with conn:
            # create a new project
            # YYYY - MM - DD
            # HH: MM:SS.SSS
            # time_stamp_str = time_stamp.strftime("%Y-%m-%d %H:%M:%S:%f")
            # print('time_stamp_str :: %s' % time_stamp_str)
            # plate_number_param = (plate_number,' ');
            output_video_param = (video_id, counter, frame_array);
            car_id = create_outputvideoframes(conn, output_video_param)
            # print(car_id)
            # insert_flag= True
    except sqlite3.Error  as exc:
        # insert_flag = False
        print(exc)
        car_id = -1
    return car_id
