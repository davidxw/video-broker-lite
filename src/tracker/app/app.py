from re import L
import subprocess
import cv2
from inference import analyse_video_fast
import time
import os

RTMP_IN_URL = os.environ["RTMP_IN_URL"]
RTMP_OUT_URL = os.environ["RTMP_OUT_URL"]
MODEL_FREQUENCY = float(os.environ["MODEL_FREQUENCY"])

streamAvailable = False
connectWaitSeconds = 2

while not streamAvailable:
    print(f"Attempting to connect to: {RTMP_IN_URL}")

    cap = cv2.VideoCapture(RTMP_IN_URL)

    # gather video info to ffmpeg
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps != 0:
        print(f"... connected.")
        streamAvailable = True
    else:
        print(f"Connection failed, retyring in {connectWaitSeconds} second(s) ...")
        time.sleep(connectWaitSeconds)

print(f"fps: {fps}")
print(f"W: {width} x H: {height}")


def main():
    # command and params for ffmpeg
    # command = ['ffmpeg',
    #         '-re',
    #         '-f', 'rawvideo',  # Apply raw video as input - it's more efficient than encoding each frame to PNG
    #         '-s', f'{width}x{height}',
    #         '-pixel_format', 'bgr24',
    #         '-r', f'{fps}',
    #         '-i', '-',
    #         '-pix_fmt', 'yuv420p',
    #         '-c:v', 'libx264',
    #         '-bufsize', '64M',
    #         '-maxrate', '8M',
    #         # '-rtsp_transport', 'tcp',
    #         '-preset', 'ultrafast',
    #         '-f', 'rtsp',
    #         '-timeout','3600',
    #           '-muxdelay', '0.1',

    # this one works
    command =  ['ffmpeg',
                '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', "{}x{}".format(width, height),
                '-r', str(fps),
                '-i', '-',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-bufsize', '128M',
                '-maxrate', '8M',
                '-preset', 'slow',
                '-f', 'rtsp',
                '-timeout','7200',
                RTMP_OUT_URL]

    # using subprocess and pipe to fetch frame data
    p = subprocess.Popen(command, stdin=subprocess.PIPE)

    async def sendImage(frame):
        global p
        try:
            p.stdin.write(frame.tobytes())
        except:
            print('Could not send image ... will attempt to establish comms again')
            time.sleep(1)
            p = subprocess.Popen(command, stdin=subprocess.PIPE)
        
    while True:
        analyse_video_fast(RTMP_IN_URL,send=sendImage,local=True,analyse_freq=int(fps*MODEL_FREQUENCY))
        print('Will replay video')
        time.sleep(1)

if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            print('Failed. Restarting...')
            time.sleep(3)
