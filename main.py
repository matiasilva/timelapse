# timelapse - a simple script that captures sunrises and sunsets

import time
from datetime import timedelta, datetime
import os
import subprocess

SUNRISE = "07:50"
SUNSET = "16:25"
OUTPUT_FOLDER = "output"
IMAGE_STRING = "image-{}"
TIMELAPSE_INTERVAL = 3


def main():
    # time check
    padding = timedelta(hours=1, minutes=30)
    count = round((padding * 2).total_seconds() / TIMELAPSE_INTERVAL)
    is_sunrise = has_triggered(SUNRISE, padding)
    is_sunset = has_triggered(SUNSET, padding)
    if is_sunrise:
        start_timelapse("sunrise", count)
    elif is_sunset:
        start_timelapse("sunset", count)
    return


def has_triggered(mid, pad):
    """
    checks if the current time is within a range specified by a midpoint and equal padding around the midpoint

    mid - ISO-formatted time
    pad - padding around the midpoint, filming triggers after (mid - pad) and stops after (mid + pad)
    """
    now = datetime.now()
    mid_t = time.fromisoformat(mid)
    mid_dt = now.replace(hour=mid_t.hour, minute=mid_t.minute)
    trigger_time = mid_dt - pad
    end_time = mid_dt + pad
    return now > trigger_time and now < end_time


def start_timelapse(type, count):
    # create folder structure
    now = datetime.now()
    file_path = f"{OUTPUT_FOLDER}/{now.year}/{now.month}/{now.day}/f{type}"
    os.makedirs(file_path, exist_ok=True)

    for i in range(count):
        # take photo
        subprocess.run(['libcamera-jpeg', '-o ' +
                       IMAGE_STRING.format(i), '-n', '-q 100'])
        # rest for a bit
        time.sleep(TIMELAPSE_INTERVAL)

    # when done, stitch the photos together
    subprocess.run(['ffmpeg', '-framerate 30', '-pattern_type glob' '-i "{file_path}/*.JPG"',
                   '-s:v 1440x1080', '-c:v libx264', '-crf 17', '-pix_fmt yuv420p', f'output.mp4'])


if __name__ == "__main__":
    main()
