import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
video = cv2.VideoCapture('input.mp4')
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
output = cv2.VideoWriter('testreso.mp4',cv2.VideoWriter_fourcc('m','p','4','v'), 10, (width,height))

while True:
    _, frame = video.read()

    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_right():
        text = "=> right"
    elif gaze.is_left():
        text = "left <="
    elif gaze.is_center():
        text = "=center="

    cv2.putText(frame, text, (60, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
    cv2.imshow("Eye contact detection", frame)
    output.write(frame)

    if cv2.waitKey(1) == 27:
        break

video.release()

cv2.destroyAllWindows()