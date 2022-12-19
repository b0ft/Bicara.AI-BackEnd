import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
video = cv2.VideoCapture('input.mp4')
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
fps = int(video.get(cv2.CAP_PROP_FPS))
output = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
# duration of the video
# print(video.get(cv2.CAP_PROP_FRAME_COUNT)/fps)

rightCounter = 0
leftCounter = 0
centerCounter = 0

while video.isOpened():
    ret, frame = video.read()

    if ret == True:
        gaze.refresh(frame)

        frame = gaze.annotated_frame()

        # how many seconds each frame
        # print(video.get(cv2.CAP_PROP_POS_MSEC)/1000)
        # print(cv2.CAP_PROP_FRAME_COUNT/fps)        
        text = ""
        text2 = ""
        if gaze.is_right():
            text = "=> right"
            rightCounter += 1/fps
        elif gaze.is_left():
            text = "left <="
            leftCounter += 1/fps
        elif gaze.is_center():
            text = "=center="
            centerCounter += 1/fps

        if gaze.vertical_ratio() != None:
            if gaze.vertical_ratio() < 0.15:
                text2 = "up"
            elif gaze.vertical_ratio() > 0.85:
                text2 = "down"

        # text2 = str(gaze.vertical_ratio())
        # get 2 number after decimal point


        cv2.putText(frame, text, (60, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.putText(frame, text2, (60, 120), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.putText(frame, str(round(leftCounter)), (60, 150), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.putText(frame, str(round(rightCounter)), (60, 200), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.putText(frame, str(round(centerCounter)), (60, 250), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
        cv2.imshow("Eye contact detection", frame)
        output.write(frame)

        if cv2.waitKey(1) == 27:
            break
    else:
        break

video.release()
output.release()

rightCounterInSecond = round(rightCounter)
leftCounterInSecond = round(leftCounter)
centerCounterInSecond = round(centerCounter)

print("rightCounterInSecond: " + str(rightCounterInSecond))
print("leftCounterInSecond: " + str(leftCounterInSecond))
print("centerCounterInSecond: " + str(centerCounterInSecond))

if centerCounterInSecond > rightCounterInSecond or centerCounterInSecond > leftCounterInSecond:
    print("good eye contact")
elif centerCounterInSecond == rightCounterInSecond or centerCounterInSecond == leftCounterInSecond:
    print("eye contact still need an improvement")
else:
    print("eye contact still need an improvement")


cv2.destroyAllWindows()