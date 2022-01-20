# timelapse

A simple tool leveraging the Raspberry Pi `libcamera` camera stack to record timelapses of sunrises and sunsets.

## Workflow

1. a `cron` entry runs the script every 5 minutes, checking if the criteria for timelapse taking is met

    `*/5 * * * * cd /home/pi/timelapse && ./main.py >> /dev/null`

2. the script takes the pictures needed and saves them in a specific folder format:

    `/home/pi/timelapse/output/year/month/day/sunriseorsunset`

3. at the end of the session, the script stitches the files together into a single timelapse file using `ffmpeg`

4. this file is also saved in the same folder and uploaded to YouTube

## Credits

Sunrise and sunset times kindly provided by the sunrise-sunset API (https://sunrise-sunset.org/api)
