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

    def display_languages_and_voices(self, rows):
        for i, row in reversed(list(enumerate(rows))):
            print(f"{i}  {row[0]}")

    def get_user_input(self):
        index = input("Choose voice for synthesizer (enter the corresponding number): ")
        return index

    def validate_and_extract_data(self, index, rows):
        try:
            index = int(index)
            if not 0 <= index < len(rows):
                raise ValueError("Invalid input. Please enter a valid row number.")
            row = rows[index]
            match = re.search(r"(\w{2}-\w{2})-(\w+Neural)", row[0])

            if not match:
                raise ValueError("Invalid format. Please check the csv file.")
            language = match.group(1)
            voice = f"{match.group(1)}-{match.group(2)}"
            return (language, voice)
        
        except ValueError as e:
            print(e)
            return None

    def choose_language_and_voice(self):
        print("Press Enter to enter the language and voice selection screen, or wait for the default configuration...")
        start_time = time.time()
        while True:
            if msvcrt.kbhit():
                input()
                with open("language_and_voice.csv", "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    self.display_languages_and_voices(rows)
                    index = self.get_user_input()
                    result = self.validate_and_extract_data(index, rows)
                    if result:
                        return result
                break
            elif time.time() - start_time > self.timeout:
                print("No input from user.")
                # 比较合适的有34/20
                language = "en-US"
                voice = "en-US-TonyNeural"
                return (language, voice)

if __name__ == '__main__':
    # Choose language and voice
    selector = LanguageAndVoiceSelector(timeout=3)
    language, voice = selector.choose_language_and_voice()

    # 测试合成到麦克风功能
    synthesizer = SpeechSynthesizer(language, voice) 

    character = "healer"

    # 测试批量合成到文件功能
    with open(f"./batches/{character}.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        texts = [row[0] for row in rows]
        text_list = texts
    synthesizer = SpeechSynthesizer(language, voice)
    for i, text in enumerate(text_list):
        output_filename = f"./tts_outputs/{character}/{i}.wav"
        synthesizer.text_to_speech_file(text, output_filename)

    # text = "这是一段测试。我是一个成熟的男人但你是个小赤佬。"
    # text = "This is a test. I'm a mature man and you are a silly boy."
    # text = "场景：一个中国女孩和一个美国男孩在上海相遇，他们相互喜欢，但是因为语言和文化的差异，他们之间有很多误会和冲突。女孩：你知道吗？我一直很喜欢你，但是你总是让我觉得你不在乎我，你不了解我，你不尊重我的文化。你为什么总是说些让我难过的话呢？男孩：I’m sorry, I didn’t mean to hurt you. I really like you too, but I don’t know how to express myself in your language. I’m trying to learn more about you and your culture, but sometimes I make mistakes. Please don’t be mad at me.女孩：那你为什么不多花点时间和我沟通呢？你为什么总是忙着工作，忙着玩，忙着跟别的女孩子聊天呢？男孩：That’s not true, I only have eyes for you. I work hard because I want to give you a better life. I play games because I want to relax with you. I talk to other girls because I want to make friends with them. You are the only one in my heart.女孩：真的吗？你不是在骗我吗？男孩：Of course it’s true. Trust me, I love you. 我爱你。"
    # synthesizer.text_to_speech_speaker(text)

    # # 测试合成到文件功能
    # filename = input("请输入要保存的文件名（无后缀）：")
    # filename = f"./tts_outputs/{filename}.wav"
    # synthesizer.text_to_speech_file(text, filename)

    # 测试识别功能
    # print("Please say something to test recognizer...")
    # recognizer = SpeechRecognizer(language)
    # print(recognizer.speech_to_text_microphone())

