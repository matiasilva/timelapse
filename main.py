#!/usr/bin/env python

# timelapse - a simple script that captures sunrises and sunsets
# TODO: take daylight saving time into account

import time
import datetime as dt
import os
import subprocess
import yaml

IMAGE_STRING = "-o image-{}"
config = {}


def main():
    # read config
    with open("config.yaml", "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)

    # fetch data from API or local cache
    with open("db.yaml", "r") as f:
        try:
            db = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
    sunrise = format_dt(db.get("sunrise"))
    sunset = format_dt(db.get("sunset"))
    if sunrise is None or sunset is None:
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

    # create folder structure
    now = dt.datetime.now()
    file_path = f"{OUTPUT_FOLDER}/{now.year}/{now.month}/{now.day}/f{type}"
    os.makedirs(file_path, exist_ok=True)

    for i in range(count):
        # take photo
        subprocess.run(
            ['libcamera-jpeg', IMAGE_STRING.format(i), '-n', '-q 100'])
        # rest for a bit
        time.sleep(TIMELAPSE_INTERVAL)

    # when done, stitch the photos together
    subprocess.run(['ffmpeg', '-framerate 30', '-pattern_type glob',
                   '-i "{file_path}/*.JPG"', '-s:v 1440x1080', '-c:v libx264', '-crf 17', '-pix_fmt yuv420p', f'output.mp4'])


if __name__ == "__main__":
    main()
