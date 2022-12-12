import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
video = cv2.VideoCapture('video.mp4')
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
fps = int(video.get(cv2.CAP_PROP_FPS))
output = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

while video.isOpened():
    ret, frame = video.read()

    if ret == True:
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_right():
            text = "=> right"
        elif gaze.is_left():
            text = "left <="
        elif gaze.is_center():
            text = "=center="

        if gaze.vertical_ratio() < 0.15:
            text2 = "up"
        elif gaze.vertical_ratio() > 0.85:
            text2 = "down"

        cv2.putText(frame, text, (60, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.putText(frame, text2, (60, 120), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.imshow("Eye contact detection", frame)
        output.write(frame)

        if cv2.waitKey(1) == ord('q'):
            break
    else:
        break


video.release()
output.release()

cv2.destroyAllWindows()