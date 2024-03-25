Summary:
This repository has python code sample which will do the following.
•	Converting audio from the computer microphone to text using Azure Speech Service.
•	Recognize multiple speakers as Guest 1, Guest 2, etc.
•	Summarize the speech text using Azure Open AI
•	Do sentiment analysis using Azure Text Analyzer

![image](https://github.com/sashgeorge/Speech2Text2Summary/assets/22481246/632e37fb-675a-4fed-b66e-5733ec22fbdc)

 
Setup and Install
1.	Run the requirements.txt file to install the necessary libraries.
  $ pip install -r requirements.txt

2.	Update the .env file with the your Azure Speech, Azure Open AI and Text Analyzer values.
3.	Run the SpeechTranscriptionNSummary.py file. 

FYI Once the speech transcription starts, it will wait for 5 seconds of silence to end the session.





