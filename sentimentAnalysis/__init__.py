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


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    
    text =req_body['text']
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    print("polarity is")
    print(polarity)
    outputSentiment ="Nothing"
    if(polarity < -0.1):
        outputSentiment ="NEGATIVE, score =  " +str(polarity)
    elif(-0.1<=polarity<=0.1):
        outputSentiment ="NEUTRAL, score =  " +str(polarity)
    elif(polarity>0.1):
        outputSentiment ="POSITIVE, score =  " +str(polarity)
    print(outputSentiment)
    return func.HttpResponse(json.dumps(outputSentiment), mimetype='application/json' )
    # return func.HttpResponse(json.dumps(polarity), mimetype='application/json' )