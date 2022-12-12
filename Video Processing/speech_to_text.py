import speech_recognition as sr 
import moviepy.editor as mp



VidClip = mp.VideoFileClip("final.mp4") 
VidClip.audio.write_audiofile("converted.wav")


reco = sr.Recognizer()
audio = sr.AudioFile("converted.wav")
with audio as source:
  audio_file = reco.record(source)
result = reco.recognize_google(audio_file, language = 'id')

with open('SpeechText.txt',mode ='w') as file: 
   file.write("Recognized Speech Text:") 
   file.write("\n") 
   file.write(result) 
   print("Text file ready!")