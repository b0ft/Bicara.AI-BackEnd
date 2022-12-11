# Step 1 : Importing libararies
import speech_recognition as sr 
import moviepy.editor as mp

# Step 2: Video to Audio conversion

VidClip = mp.VideoFileClip("/content/data/video.mp4") 
VidClip.audio.write_audiofile("/content/data/converted.wav")

# Step 3: Speech recognition

reco = sr.Recognizer()
audio = sr.AudioFile("/content/data/converted.wav")
with audio as source:
  audio_file = reco.record(source)
result = reco.recognize_google(audio_file)

# Step 4: Finally exporting the result 

with open('/content/data/SpeechText.txt',mode ='w') as file: 
   file.write("Recognized Speech Text:") 
   file.write("\n") 
   file.write(result) 
   print("Text file ready!")