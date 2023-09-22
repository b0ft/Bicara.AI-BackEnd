import g4f
from g4f.Provider import (
    Aichat,
)

def grammar_check(text):
    try:
        message= "Can you fix the following grammar?" + text
        response = g4f.ChatCompletion.create(model='gpt-3.5-turbo', provider=g4f.Provider.Aichat, messages=[
                                            {"role": "user", "content": message}], stream=False)
        
        return response
    except:
        return "Sorry, I couldn't understand that. Please try again."