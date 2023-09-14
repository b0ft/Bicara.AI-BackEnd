import cv2
from AI.gaze_tracking import GazeTracking
import speech_recognition as sr 
import moviepy.editor as mp
import re
from collections import Counter
import os
import time
from datetime import datetime
from gpt import grammar_check
mysp=__import__("my-voice-analysis") 

def videoProcess(filename, email):
    start_time = time.time()
    gaze = GazeTracking()
    video = cv2.VideoCapture('static/uploads/'+filename)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    output = cv2.VideoWriter('output'+filename,cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
    duration= video.get(cv2.CAP_PROP_FRAME_COUNT)/fps
    frames = 0
    seconds = 0
    speech = 0
    filler_words=["so", "like","then","maybe"]
    filler_total= 0
    x,y,w,h = 0,0,width,75
    rightCounterInSecond = 0
    leftCounterInSecond = 0
    centerCounterInSecond = 0


    while True:
        ret, frame = video.read()
        if speech == 0 and seconds > 0:
            speech = 1
            # VidClip = mp.VideoFileClip("static/uploads/" + filename).subclip(0,seconds) 
            # VidClip.audio.write_audiofile(filename+"audio.wav")
            # reco = sr.Recognizer()
            # audio = sr.AudioFile(filename+"audio.wav")
            # with audio as source:
            #     audio_file = reco.record(source)
            #     try:
            #         result = reco.recognize_google(audio_file, language='en' )
            #     except  Exception as e:
            #             continue
            
            # with open(filename+'SpeechToText.txt',mode ='w') as file: 
            #     file.write("Recognized Speech Text:") 
            #     file.write("\n") 
            #     file.write(result) 
            #     print("Text file ready!")
            # with open(filename+'SpeechToText.txt', "r",encoding="utf8") as external_file:
            #     words = external_file.read().lower().split()
            #     string = dict(Counter(words))
            #     pacing = sum(string.values()) / duration*60

            # filler_count={key:value for key,value in string.items() if key in filler_words}
            # filler_total=sum(filler_count.values())
        if ret == True:
            frames += 1
            if frames%fps == 0  and frames >= fps:
                seconds += 1
                speech = 0
            gaze.refresh(frame)
            frame = gaze.annotated_frame()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (181,224,79), -1)
            text = ""
            # text2 = ""

            if gaze.is_right():
                text = "=> right"
                rightCounterInSecond += 1/fps
            elif gaze.is_left():
                text = "left <="
                leftCounterInSecond += 1/fps
            elif gaze.is_center():
                text = "=center="
                centerCounterInSecond += 1/fps
            # if gaze.vertical_ratio() != None:
            #     if gaze.vertical_ratio() < 0.15:
            #         text2 = "up"
            #     elif gaze.vertical_ratio() > 0.85:
            #         text2 = "down"

            
            
            # text_filler = f"Filler Words: {filler_total}"
            # if 4*width > 3*height and width > 992:
            #     cv2.putText(frame, text_filler, (int(width*0.75), 45), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
            # else:
            #     cv2.putText(frame, text_filler, (int(width*0.5), 45), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
            # cv2.putText(frame, text2, (60, 120), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 2)
            if seconds > duration - 2:
                if centerCounterInSecond > rightCounterInSecond or centerCounterInSecond > leftCounterInSecond:
                    message = "good eye contact"
                    cv2.putText(frame, message,  (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
                else:
                    message = "eye contact still\nneed an improvement"
                    cv2.putText(frame, message,  (20, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(frame, text, (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
            output.write(frame)

        else:
            break


    video.release()
    output.release()
    VidClip = mp.VideoFileClip("static/uploads/" + filename)
    VidClip.audio.write_audiofile(filename+"audio.wav")
    reco = sr.Recognizer()
    audio = sr.AudioFile(filename+"audio.wav")
    with audio as source:
        audio_file = reco.record(source)
        try:
            result = reco.recognize_google(audio_file, language='en' )
        except  Exception as e:
            print(e)
    
    with open(filename+'SpeechToText.txt',mode ='w') as file: 
        file.write("Recognized Speech Text:") 
        file.write("\n") 
        file.write(result) 
        print("Text file ready!")
    with open(filename+'SpeechToText.txt', "r",encoding="utf8") as external_file:
        words = external_file.read().lower().split()
        string = dict(Counter(words))
        pacing = sum(string.values()) / duration*60

    filler_count={key:value for key,value in string.items() if key in filler_words}
    filler_total=sum(filler_count.values())

    ResClip = mp.VideoFileClip(r"output"+filename)
    FinAudio = mp.AudioFileClip(filename+"audio.wav")
    ResClip.write_videofile("result"+filename)
    FinClip = mp.VideoFileClip(r"result"+filename)
    fin_clip=FinClip.set_audio(FinAudio)
    fin_clip.write_videofile('static/results/'+filename,audio=True, audio_codec='aac')
    checked = grammar_check(result)
    os.remove('output'+filename)
    os.remove('result'+filename)
    voiceAnalysis = mysp.mysptotal(filename+"audio",r"D:/final-project/Bicara.AI-BackEnd")
    try:
        # os.remove(filename+"audio.wav")
        os.remove(filename+'SpeechToText.txt')
    except:
        pass
    print("--- %s seconds ---" % (time.time() - start_time))
    print(voiceAnalysis)
    if message == "good eye contact":
        eyeContactMessage = "Good"
    else:
        eyeContactMessage = "Need Improvement"

    data = {
        "filename": filename,
        "duration": int(duration),
        "filler": filler_total,
        "eyeContact": eyeContactMessage,
        "email": email,
        "pacing": int(pacing),
        "date": datetime.now(),
        "fillerWords": filler_count,
        "transcript": result,
        "review": checked,
        # "voiceAnalysis": voiceAnalysis
    }
    return data 
