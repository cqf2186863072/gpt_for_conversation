import os
import azure.cognitiveservices.speech as speechsdk
import configparser

class SpeechSynthesizer:
    def __init__(self, subscription, region, voice_name):
        self.speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
        self.speech_config.speech_synthesis_voice_name = voice_name
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

    def speak_text(self, text):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()
        # # 处理结果
        # if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        #     print("Speech synthesized for text [{}]".format(text))
        # elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        #     cancellation_details = speech_synthesis_result.cancellation_details
        #     print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
        #         if cancellation_details.error_details:
        #             print("Error details: {}".format(cancellation_details.error_details))
        #             print("Did you set the speech resource key and region values?")

class Stt:
    def __init__(self, subscription, region, voice_name):
        self.speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
        self.speech_config.speech_recognition_language="zh-CN"
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)
    def recognize(self):
        speech_recognition_result = self.speech_recognizer.recognize_once_async().get()
        return speech_recognition_result

def main():
    subscription = os.environ.get('SPEECH_KEY')
    region = os.environ.get('SPEECH_REGION')
    config = configparser.ConfigParser()
    file_dir = os.path.dirname(__file__)
    config_file = os.path.join(file_dir, 'config.ini')
    if os.path.exists(config_file): 
        config.read(config_file) 
        voice_name = config.get('config_Azure', 'voice_name')

    synthesizer = SpeechSynthesizer(subscription, region, voice_name)
    print("Enter some text that you want to speak >")
    text = input()
    synthesizer.speak_text(text)

if __name__ == '__main__':
    main()
