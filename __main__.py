import os
import configparser
from azure_module import SpeechSynthesizer
from azure_module import SpeechRecognizer
from azure_module import LanguageAndVoiceSelector
from gpt_module import GPTClient
from dialogue_module import DialogueManager

if __name__ == '__main__':
    # 配置GPT
    config = configparser.ConfigParser()
    file_dir = os.path.dirname(__file__)
    config_file = os.path.join(file_dir, 'config.ini')
    if os.path.exists(config_file): 
        config.read(config_file)
        url = config.get('gpt', 'url')
        header = eval(config.get('gpt', 'header'))
    else:
        print("请配置config.ini")
    gpt_client = GPTClient(url, header)

    # 配置语音合成器和语音识别器
    # selector = LanguageAndVoiceSelector(timeout=3)
    # language, voice = selector.choose_language_and_voice()
    # synthesizer = SpeechSynthesizer(language, voice)
    # recognizer = SpeechRecognizer(language)

    # 运行对话系统
    dialogue_manager = DialogueManager(gpt_client)
    dialogue_manager.run()
