#!/usr/bin/env python

# timelapse - a simple script that captures sunrises and sunsets
# TODO: take daylight saving time into account

import time
import datetime as dt
import os
import subprocess
import yaml
from pathlib import Path
import sys
import signal

config = {}

def main():
    signal.signal(signal.SIGINT, exit_gracefully)

    # check LOCK file
    if Path("lock").is_file():
        sys.exit(0)

    # read config
    CONFIG_PATH = Path('config.yaml')
    try:
        with open(CONFIG_PATH, "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
    except FileNotFoundError as e:
        print(e)

    # use local cache OR fallback values
    DB_PATH = Path('db.yaml')
    try:
        with open(DB_PATH, "r") as f:
            try:
                db = yaml.safe_load(f)
                sunrise = format_dt(db.get("sunrise"))
                sunset = format_dt(db.get("sunset"))
            except yaml.YAMLError as exc:
                print(exc)
    except FileNotFoundError as e:
        # use config
        sunrise = time_to_dt(config.get("sunrise"))
        sunset = time_to_dt(config.get("sunset"))

    # time check
    padding = dt.timedelta(hours=1, minutes=30)
    TIMELAPSE_INTERVAL = config.get("timelapse_interval", 3)
    count = round((padding * 2).total_seconds() / TIMELAPSE_INTERVAL)
    is_sunrise = has_triggered(sunrise, padding)
    is_sunset = has_triggered(sunset, padding)
    if is_sunrise:
        start_timelapse("sunrise", count)
    elif is_sunset:
        start_timelapse("sunset", count)
    return


def exit_gracefully(signum, frame):
    # delete lock if exists
    if Path("lock").is_file():
        os.remove("lock")
    sys.exit()


def time_to_dt(t_raw):
    now = dt.datetime.now()
    t = dt.time.fromisoformat(t_raw)
    return now.replace(hour=t.hour, minute=t.minute)


def format_dt(raw_t):
    # drop the unnecessary precision of the second's place, use naive dt
    return dt.datetime.fromisoformat(raw_t).replace(second=0, tzinfo=None)


def has_triggered(mid_dt, pad):
    """
    checks if the current time is within a range specified by a midpoint and equal padding around the midpoint

    mid - datetime object
    pad - padding around the midpoint, filming triggers after (mid - pad) and stops after (mid + pad)
    """
    now = dt.datetime.now()
    trigger_time = mid_dt - pad
    end_time = mid_dt + pad
    return now > trigger_time and now < end_time


def start_timelapse(type, count):
    # constants
    TIMELAPSE_INTERVAL = config.get("timelapse_interval", 3)
    OUTPUT_FOLDER = config.get("output_folder", "output")

    # create LOCK file
    open("lock", 'a').close()

    # create folder structure
    now = dt.datetime.now()
    file_path = f"{OUTPUT_FOLDER}/{now.year}/{now.month}/{now.day}/{type}"
    os.makedirs(file_path, exist_ok=True)

    for i in range(count):
        # take photo
        args = ['libcamera-jpeg', '-n', '-q', '100', '--width', '1920', '--height', '1080', '-t', '1', '-o', f'{file_path}/image-{i}.jpg']
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if i % 10 == 0:
            print(f'{round(100*i/count)}% -- {i}/{count}')
        # rest for a bit
        time.sleep(TIMELAPSE_INTERVAL)

    # remove LOCK file
    os.remove("lock")

    # when done, stitch the photos together
    # subprocess.run(['ffmpeg', '-framerate 30', '-pattern_type glob',
     #              '-i "{file_path}/*.JPG"', '-c:v libx264', '-crf 17', '-pix_fmt yuv420p', f'output.mp4'])


if __name__ == "__main__":
    main()
