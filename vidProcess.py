import cv2
from gaze_tracking import GazeTracking
import speech_recognition as sr 
import moviepy.editor as mp
import re
from collections import Counter
import os

def videoProcess(filename):
    gaze = GazeTracking()
    video = cv2.VideoCapture('static/uploads/'+filename)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    output = cv2.VideoWriter('output_filler#2.mp4',cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
    duration= video.get(cv2.CAP_PROP_FRAME_COUNT)/fps
    frames = 0
    seconds = 0
    speech = 0
    past_second = 0
    filler_words=["jadi", "kayak","terus","mungkin"]
    filler_total= 0



    while True:
        ret, frame = video.read()
        if speech == 0 and seconds > 0:
            speech = 1
            VidClip = mp.VideoFileClip("static/uploads/" + filename).subclip(0,seconds) 
            VidClip.audio.write_audiofile("converted.wav")
            reco = sr.Recognizer()
            audio = sr.AudioFile("converted.wav")
            with audio as source:
                audio_file = reco.record(source)
            try:
                result = reco.recognize_google(audio_file, language= 'id')
            except Exception as e:
                try:
                    result = reco.recognize_google(audio_file, language='en' )
                except  Exception as e:
                        continue
            
            with open('SpeechTextFiller.txt',mode ='w') as file: 
                file.write("Recognized Speech Text:") 
                file.write("\n") 
                file.write(result) 
                print("Text file ready!")
            with open("SpeechTextFiller.txt", "r",encoding="utf8") as external_file:
                words = external_file.read().lower().split()
                string = dict(Counter(words))

            filler_count={key:value for key,value in string.items() if key in filler_words}
            filler_total=sum(filler_count.values())
        if ret == True:
            frames += 1
            if frames%fps == 0  and frames >= fps:
                seconds += 1
                speech = 0
            gaze.refresh(frame)
            frame = gaze.annotated_frame()
            text = ""

            if gaze.is_right():
                text = "=> right"
            elif gaze.is_left():
                text = "left <="
            elif gaze.is_center():
                text = "=center="
            elif gaze.is_up():
                text = "up"
            elif gaze.is_down():
                text = "down"
            
            
            text_filler = f"Filler Words: {filler_total}"
            cv2.putText(frame, text_filler, (400, 60), cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 0, 0), 2)


            cv2.putText(frame, text, (60, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)

            output.write(frame)

        else:
            break


    video.release()
    output.release()


    ResClip = mp.VideoFileClip(r"output_filler#2.mp4")
    FinAudio = mp.AudioFileClip('converted.wav')
    ResClip.write_videofile("result_filler#2.mp4")
    FinClip = mp.VideoFileClip(r"result_filler#2.mp4")
    fin_clip=FinClip.set_audio(FinAudio)
    fin_clip.write_videofile('static/results/'+filename,audio=True, audio_codec='aac')
    os.remove('converted.mp3')
    os.remove('converted.wav')
    os.remove('output_filler#2.mp4')
    os.remove('result_filler#2.mp4')
    os.remove('SpeechTextFiller.txt')



