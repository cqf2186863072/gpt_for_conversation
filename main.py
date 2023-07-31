import os
import configparser
from azure_module import SpeechSynthesizer
from azure_module import SpeechRecognizer
from gpt_module import GPTClient
from dialogue_module import DialogueManager

if __name__ == '__main__':
    config = configparser.ConfigParser()
    file_dir = os.path.dirname(__file__)
    config_file = os.path.join(file_dir, 'config.ini')
    if os.path.exists(config_file): 
        config.read(config_file) 
        url = config.get('gpt', 'url') 
        header = eval(config.get('gpt', 'header'))
        voice_name_SpeechSynthesizer = config.get('Azure_SpeechSynthesizer', 'voice_name_SpeechSynthesizer')
        voice_name_SpeechRecognizer = config.get('Azure_SpeechRecognizer', 'voice_name_SpeechRecognizer')
    else:
        print("请配置config.ini")

    synthesizer = SpeechSynthesizer(os.environ.get('SPEECH_KEY'), os.environ.get('SPEECH_REGION'), voice_name_SpeechSynthesizer)
    recognizer = SpeechRecognizer(os.environ.get('SPEECH_KEY'), os.environ.get('SPEECH_REGION'), voice_name_SpeechRecognizer)
    gpt_client = GPTClient(url, header)

    dialogue_manager = DialogueManager(gpt_client, synthesizer, recognizer)
    dialogue_manager.run()
