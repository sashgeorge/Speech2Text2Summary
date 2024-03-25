from pydash import retry
from tenacity import stop_after_attempt, wait_random_exponential
import azure.cognitiveservices.speech as speechsdk
import os
from openai import AzureOpenAI, BadRequestError
import time
from datetime import datetime
from dotenv import load_dotenv

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

#Load the environment variables
load_dotenv()

#---------------------------------------------------------------------------------------------#
# Capture audio from the computer microphone and convert to text using Azure Azure Speech API
# Converted text will recognize multiple speakers as Guest 1, Guest 2, etc.
#---------------------------------------------------------------------------------------------#

def Start_recording():
    # Set your Azure Speech API key and region
    speech_key = os.getenv("AZURE_SPEECH_KEY")  
    service_region = os.getenv("AZURE_SPEECH_REGION")

        # Initialize variables
    results = []
    done = False
    lastSpoken=0

    # update the last time speech was detected.
    def speech_detected(evt):
        nonlocal lastSpoken
        lastSpoken = int(datetime.now().timestamp() * 1000)

    def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
        print('Canceled event')

    def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStopped event')

    def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        import json
        nonlocal results
        nonlocal lastSpoken

        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print('Transcription is in progress.....')
            #results.append(evt.result.speaker_id + " :" + evt.result.text)
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

        speech_detected(evt)


    def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStarted event')

    #callback that signals to stop continuous recognition upon receiving an event `evt`
    def stop_cb(evt: speechsdk.SessionEventArgs):
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # # Callback function to collect recognized speech
    def collectResult(evt):
        global result
        results.append(evt.result.speaker_id + " :" + evt.result.text)
        #print(results)

    # Configure the Speech SDK
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "en-US"

    # Initialize the speech recognizer
    #speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config)

    transcribing_stop = False
 

     # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
    conversation_transcriber.transcribed.connect(lambda evt: collectResult(evt))
    conversation_transcriber.transcribing.connect(speech_detected)
    conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
    conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
    conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)

    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    
    # Start the transcription
    conversation_transcriber.start_transcribing_async()

    lastSpoken = int(datetime.now().timestamp() * 1000)


    # Wait for speech recognition to complete
    while not done:
        time.sleep(1)
        now = int(datetime.now().timestamp() * 1000)
        inactivity = now - lastSpoken

        # Close the recoding session if no input is detected after 5 Seconds
        if (inactivity > 5000):  
            print('Pause detected for {} milliseconds.'.format(inactivity))
            conversation_transcriber.stop_transcribing_async()
            done = True

    return results

# Calling the function to start recording
rtn = Start_recording()
print(rtn)

SpeechText = ""
for i in rtn:
    SpeechText += i + "\n "

#if speech is empty then exit
if SpeechText == "":
    print("No speech detected, exiting...")
    exit()



#----------------------------------------------#
# Speech Text summarization using Azure OpenAI
#----------------------------------------------#
        
#Calling Azure Open AI for Summarization
SUMMARY_PROMPT = "Summarize the given text below. Use Bullet points to summarize multiple data points efficiently.  Identify the guest speaker and the host in the summary."

#@retry(
#    stop=stop_after_attempt(5),
#    wait=wait_random_exponential(multiplier=1, max=10)
#)

def generate_response(client, content, prompt, deployment_name):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content}
    ]

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            temperature=0.0,
        )
    except BadRequestError as err:
        print(err.message)
        print(content)
        return None
        

    return response.choices[0].message.content


# Calling Azure Open AI for Summarization
CLIENT = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = 'gpt-35-turbo-16k'
print("Summarizing the text...")
summary = generate_response(CLIENT, SpeechText, SUMMARY_PROMPT, DEPLOYMENT_NAME)
print("Summary: ")
print(summary)


#----------------------------------------------#
# Sentiment Analysis using Azure Text Analytics
#----------------------------------------------#

def SentimentAnalysis(text):

    #setting the environment variables
    key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
    endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")

    try:

        # Initialize the client
        text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))

        # Prepare the documents
        documents = [
            {"id": "1", "text": {text}},
        ]

        # Analyze sentiment
        response = text_analytics_client.analyze_sentiment(documents)
        successful_responses = [doc for doc in response if not doc.is_error]

        print("Sentiment Analysis................. ")
        for doc in successful_responses:
            print(f"Document ID: {doc.id}")
            print(f"Sentiment: {doc.sentiment}")
            print(f"Confidence score: {doc.confidence_scores[doc.sentiment]}")
            print("\n")
    except Exception as e:
        print("Error in Sentiment Analysis: ", e)
        return None

# Calling the function to perform Sentiment Analysis
SentimentAnalysis(SpeechText)