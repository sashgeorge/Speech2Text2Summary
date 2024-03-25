Summary:
This repository has python code sample which will do the following.
1. Converting audio from the computer microphone to text using Azure Speech Service.
2. Recognize multiple speakers as Guest 1, Guest 2, etc.
3. Summarize the speech text using Azure Open AI
4. Do sentiment analysis using Azure Text Analyzer

![image](https://github.com/sashgeorge/Speech2Text2Summary/assets/22481246/d27bb9fc-8d80-44f4-a86f-7ef923f83e3c)

 
Setup and Install
1.	Run the requirements.txt file to install the necessary libraries.
   
       $ pip install -r requirements.txt

2.	Update the .env file with your Azure Speech, Azure Open AI and Text Analyzer values.
   
3.	Run the SpeechTranscriptionNSummary.py file. 

FYI. Once the speech transcription starts, it will wait for 5 seconds of silence to end the session.





