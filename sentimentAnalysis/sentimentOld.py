import urllib
import pickle
import speech_recognition as sr
# import moviepy.editor as mp
import os
import googleapiclient.discovery
import json
from google.cloud import firestore
from moviepy.editor import *
client = firestore.Client()
r= sr.Recognizer()

# def predict_json(project, model, instances, version=None):
#     GOOGLE_APPLICATION_CREDENTIALS = 'service_account.json'
#     service = googleapiclient.discovery.build('ml', 'v1')
#     name = 'projects/surveyed-549e5/models/sentiment_predict_Survyed'.format(project, model)
#     if version is not None:
#         name += '/versions/Cloud_Predict_1'.format(version)

#     response = service.projects().predict(
#         name=name,
#         body={'instances': [instances]}
#     ).execute()

#     if 'error' in response:
#         raise RuntimeError(response['error in prediction'])

#     return response['predictions']


def test_read_write_tmp(filePath,content):
    file_path = filePath
    content = content#  make sure dir exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()

    return file_path
    
def urlToSentimentConverter(urls):
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
    urllib.request.urlretrieve(urls,'/tmp/downloadedVideo.mp4')
   
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
        interResult=["Audio to text failed",""]
        print(interResult)
        print(type(interResult))
        return str(interResult[0]),text

    else:
        interResult=predict_json(project="surveyed-549e5", model="sentiment_predict_Survyed", instances=text, version="Cloud_Predict_1")
        print(interResult)
        print(type(interResult))
        return str(interResult[0]),text



    
    



# def hello_firestore(event, context):
    """Triggered by a change to a Firestore document.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
resource_string = context.resource
# print out the resource string that triggered the function
print(f"Function triggered by change to: {resource_string}.")
path_parts = context.resource.split('/documents/')[1].split('/')
collection_path = 'aiResults'
document_path = '/'.join(path_parts[1:])
affected_doc = client.collection(collection_path).document(document_path)

# affected_doc.set({
#         u'Ai Result': 'Will Be updating soon'
#     })

z=event["value"]
print(z)
if(z['fields']):
    log=z['fields']
    if(log.get("contributors") and log["contributors"]['mapValue'] and log["contributors"]['mapValue']['fields']):
        contents = log["contributors"]['mapValue']['fields']
        for content in contents.keys():
            inside = contents[content]['mapValue']['fields']
            contributorId = inside['contributorId']['stringValue']
            if(inside.get('responses') and inside['responses']['mapValue'] and inside['responses']['mapValue']['fields']): 
                questions = inside['responses']['mapValue']['fields']  
                for question in questions.keys():  
                    responseId = question            
                    if( questions.get(question) and  questions[question]['mapValue'] and  questions[question]['mapValue']['fields']):
                        questionDetails =  questions[question]['mapValue']['fields']     
                        if( questionDetails.get('video') and  questionDetails['video']['mapValue'] and  questionDetails['video']['mapValue']['fields']):             
                            video = questionDetails['video']['mapValue']['fields']
                            if( video.get('urls') and  video['urls']['mapValue'] and  video['urls']['mapValue']['fields']): 
                                if(video['urls']['mapValue']['fields']['MP4'] and video['urls']['mapValue']['fields']['MP4']['stringValue']):
                                    print(video['urls']['mapValue']['fields']['MP4']['stringValue'])
                                    extractedURL = video['urls']['mapValue']['fields']['MP4']['stringValue']
                                    # affected_doc.set({
                                    #     u'Ai URL': extractedURL
                                    #     })
                                    try:
                                        sentiment,extractedText = urlToSentimentConverter(urls = extractedURL)

                                    except:
                                        sentiment,extractedText = "error in urlToSentiment","error in urlToSentiment"


                                    print("sentiment: "+str(sentiment))
                                    affected_doc.set({
                                        contributorId : {
                                            responseId : {                                                  
                                                "Audio" : extractedText,
                                                "audioSentiment" : sentiment
                                                }
                                        }
                                        }, merge=True)
                        
                        if( questionDetails.get('answer')):
                            try:
                                answerText = questionDetails['answer']['stringValue']
                                print("text answer"+str(answerText))
                                textResult = predict_json(project="surveyed-549e5", model="sentiment_predict_Survyed", instances=answerText, version="Cloud_Predict_1")
                                print("Predicted sentiment for text answer"+str(textResult[0]))
                                affected_doc.set({
                                            contributorId : {
                                                responseId : {                                                  
                                                    "Text" : answerText,
                                                    "TextSentiment" : textResult[0] 
                                                    }
                                            }
                                            }, merge=True)
                            
                            except:
                                print("text to sentiment failed for text")
                            
