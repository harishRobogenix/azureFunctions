# import logging

# import azure.functions as func


# def main(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )

import logging

import azure.functions as func
from textblob import TextBlob
import nltk
import os
import json

import urllib
import pickle
import speech_recognition as sr
import os
import json
from moviepy.editor import *
import requests

r= sr.Recognizer()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    
    extractedURL =req_body['url']
    outputSentiment ="Nothing"
    try:
        sentiment,extractedText = urlToSentimentConverter(urls = extractedURL)
        print("final sentiment "+str(sentiment))
        return func.HttpResponse(json.dumps(sentiment), mimetype='application/json' )
    except:
        sentiment,extractedText = "error in urlToSentiment","error in urlToSentiment"
    

    
def urlToSentimentConverter(urls):
    def textToSentiment(text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        outputSentiment ="Nothing"
        if(polarity < -0.1):
            outputSentiment ="NEGATIVE, score =  " +str(polarity)
        elif(-0.1<=polarity<=0.1):
            outputSentiment ="NEUTRAL, score =  " +str(polarity)
        elif(polarity>0.1):
            outputSentiment ="POSITIVE, score =  " +str(polarity)
        print("output sentiment = "+str(outputSentiment))
        return(outputSentiment)
    def startConvertion(path='/tmp/convertedAudio.wav', lang='en-IN'):
        with sr.AudioFile(path) as source:
            print('Fetching File')
            audio_text = r.listen(source)
            # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
            try:

                # using google speech recognition
                print('Converting audio transcripts into text ...')
                text = r.recognize_google(audio_text)
                print('Converted is '+str(text))
                return text

            except:
                print('unable to convert audio to text')
                return "error in text conversion"

    print('Downloading video')
    urllib.request.urlretrieve(urls, '/tmp/downloadedVideo.mp4')

    print('Download completed')

    print("reading video file")
    # my_clip = mp.VideoFileClip(r'/tmp/downloadedVideo.mp4')

    # my_clip.audio.write_audiofile(r"/tmp/my_result.wav")
    # print('writting complete')
    sound = AudioFileClip("/tmp/downloadedVideo.mp4")
    print('writing audio file')
    sound.write_audiofile("/tmp/convertedAudio.wav")
    print('writting complete')

    text = startConvertion(path='/tmp/convertedAudio.wav', lang='en-IN')
    # text = 'that was very nice very very nice keep doing it its great'

    if (text == "error in text conversion"):
        interResult = ["Audio to text failed", ""]
        print(interResult)
        print(type(interResult))
        return str(interResult[0]), text

    else:
        interResult = textToSentiment(text)
        print(interResult)
        print(type(interResult))
        return str(interResult), text

