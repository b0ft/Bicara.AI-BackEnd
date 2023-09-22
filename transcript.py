import speech_recognition as sr 

def speechToText(filename):
    reco = sr.Recognizer()
    audio = sr.AudioFile(filename+".wav")
    with audio as source:
        audio_file = reco.record(source)
        try:
            result = reco.recognize_google(audio_file, language='en' , with_confidence=True )\
           
        except  Exception as e:
                return "Error in speech to text"
        
    # with open(filename+'SpeechToText.txt',mode ='w') as file: 
    #     file.write("Recognized Speech Text:") 
    #     file.write("\n") 
    #     file.write(result) 
    print(result[0])
    return "Text file ready!"

speechToText(r"C:\Users\FATHAN\Downloads\WIN_20230914_08_12_44_Pro")