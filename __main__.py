import os
import configparser
import csv
import json
from azure_module import SpeechSynthesizer
from azure_module import SpeechRecognizer
from azure_module import LanguageAndVoiceSelector
from gpt_module import GPTClient
from dialogue_module import DialogueManager


def generate_in_batches(gpt_client:GPTClient, prompt_filename, message_filename): 
    '''用gpt批量处理文本的方法
    
    用预设好的prompt批量处理同类型文本，比如批量生成微小说

    Args:
        dialogue_manager: DialogueManager实例
        prompt_filename: 预设的prompt文件路径
        message_filename: 需要批量处理的文本的文件路径

    '''
    with open(message_filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        keywords_list = [row[1] for row in rows]
        for row, keywords in zip(rows, keywords_list):
            if not row[2]:    
                file_name = os.path.join('saved_dialogue_history', prompt_filename + '.json')
                with open(file_name, 'r') as file:
                    dialogue_history = json.load(file)
                dialogue_history.append({"role": "user", "content": f'{keywords}'})
                response = gpt_client.send_request(dialogue_history)
                # Update the row with the response
                row[2] = response
            else:
                continue

    # 将结果写到csv文件
    with open(message_filename, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def set_csv_file(filename):
    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        name = ['top', 'left']
        writer.writerow(name)
        z = [
            [0, 31],
            [1, 30],
            [2, 29],
        ]
        writer.writerows(z)
        f.close()

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
    # dialogue_manager = DialogueManager(gpt_client)
    # dialogue_manager.run()

    # 批处理
    prompt_filename = "小说家"
    message_filename = "./batches/batches.csv"
    generate_in_batches(gpt_client=gpt_client, prompt_filename=prompt_filename, message_filename=message_filename)

