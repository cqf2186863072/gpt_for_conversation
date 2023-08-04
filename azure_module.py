import os
import csv
import re
import time
import msvcrt
import azure.cognitiveservices.speech as speechsdk

class SpeechSynthesizer:
    def __init__(self, language, voice):
        self.language = language
        self.voice = voice
        self.speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        self.speech_config.speech_synthesis_language = language
        self.speech_config.speech_synthesis_voice_name = voice

    def text_to_speech_speaker(self, text):
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()
        self.print_info()
    
    def text_to_speech_file(self, text, output_filename):
        self.audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()
        self.print_info()
        
    def print_info(self):
        if self.speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif self.speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = self.speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

class SpeechRecognizer:
    def __init__(self, language):
        self.speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        self.speech_config.speech_recognition_language = language

    def speech_to_text_microphone(self):
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)
        self.speech_recognition_result = self.speech_recognizer.recognize_once_async().get()
        self.print_info()
        return self.speech_recognition_result.text
    
    def print_info(self):
        if self.speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(self.speech_recognition_result.text))
        elif self.speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(self.speech_recognition_result.no_match_details))
        elif self.speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = self.speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

class LanguageAndVoiceSelector:
    def __init__(self, timeout):
        self.timeout = timeout

    def choose_language_and_voice(self):
        print("摁下enter进入选择语言和声色界面，否则使用默认配置...")
        start_time = time.time()
        while True:
            if msvcrt.kbhit():
                i = input()
                with open("language_and_voice.csv", "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    for i, row in reversed(list(enumerate(rows))):
                        print(f"{i}  {row[0]}")
                    print("Choose voice for synthesizer(enter the corresponding number):")
                    i = input()

                    try:
                    
                        i = int(i)
                        if not 0 <= i < len(rows):
                            raise ValueError("Invalid input. Please enter a valid row number.")
                        row = rows[i]
                        match = re.search(r"(\w{2}-\w{2})-(\w+Neural)", row[0])
                        if not match:
                            raise ValueError("Invalid format. Please check the csv file.")
                        language = match.group(1)
                        voice = f"{match.group(1)}-{match.group(2)}"
                        return (language, voice)
                    except ValueError as e:
                        print(e)
                break
            elif time.time() - start_time > self.timeout:
                print("No input from user.")
                language = "ja-JP" 
                voice ="ja-JP-NaokiNeural"
                return (language, voice)

if __name__ == '__main__':
    #! Summary
    #   Test

    #* Choose language and voice
    selector = LanguageAndVoiceSelector(timeout=3)
    language, voice = selector.choose_language_and_voice()

    #* Test for synthesizer 
    synthesizer = SpeechSynthesizer(language, voice)
    text = "This is a test.衬衫的价格是9磅15便士。"
    synthesizer.text_to_speech_speaker(text)
    input("Press any key to continue...")
    print("Please say something to test recognizer...")
    recognizer = SpeechRecognizer(language)
    print(recognizer.speech_to_text_microphone())

    #* Test for recognizer
    # with open("text_list.csv", "r", encoding="utf-8") as f:
    #     reader = csv.reader(f)
    #     rows = list(reader)
    #     texts = [row[0] for row in rows]
    #     text_list = texts
    # synthesizer = SpeechSynthesizer(language, voice)
    # for i, text in enumerate(text_list):
    #     output_filename = f"e:/Azure/output/test_{i}.wav"
    #     synthesizer.text_to_speech_file(text, output_filename)