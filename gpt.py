import os
import requests
import re
import configparser
from Azure import SpeechSynthesizer
from Azure import Stt

exit_words = ["退出", "结束", "停止", "exit", "end"]
exit_pattern = "|".join(exit_words)

config = configparser.ConfigParser()
file_dir = os.path.dirname(__file__)
config_file = os.path.join(file_dir, 'config.ini')
if os.path.exists(config_file): 
    config.read(config_file) 
    url = config.get('config_gpt', 'url') 
    header = eval(config.get('config_gpt', 'header'))
    voice_name = config.get('config_Azure', 'voice_name')
else: 
    url = input('请输入 url 的值：') 
    header = input('请输入 header 的值（格式为字典）：') 
    header = eval(header)

def send_message(message):
    data = {
        'model_name': 'gpt-4-32k',
        'message': message,
        'temperature': 0
    }

    try:
        response = requests.post(url=url, headers=header, json=data)
        if response.status_code == 200:
            return response.json()['result']
        else:
            raise Exception(f"Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request exception: {e}")

def get_response(dialogue_history):
    #user_input = input("User: ")
    user_input = "Recognized: {}".format(Stt.recognize().text)
    print(user_input)
    dialogue_history.append({"role": "user", "content": user_input})
    return send_message(dialogue_history)

def print_and_speak(text, synthesizer):
    print(f"AI: {text}")
    synthesizer.speak_text(text)

synthesizer = SpeechSynthesizer(os.environ.get('SPEECH_KEY'), os.environ.get('SPEECH_REGION'), voice_name)

# 初始对话记录
dialogue_history = [{"role": "system", "content": ''}]

exit_flag = False

while not exit_flag:
    try:
        text = get_response(dialogue_history)
    except Exception as e:
        print(f"Error: {e}")
        break
    print_and_speak(text, synthesizer)
    # 将模型返回的文本添加到对话记录中
    dialogue_history.append({"role": "system", "content": text})
    if re.search(exit_pattern, dialogue_history[-2]['content']):
        exit_flag = True

print_and_speak('感谢您使用本程序，再见！', synthesizer)