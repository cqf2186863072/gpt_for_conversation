import re
import os
import configparser
import json
from datetime import datetime
from enum import Enum
from gpt_module import GPTClient

class InputMode(Enum):
    KEYBOARD = 0
    VOICE = 1

class OutputMode(Enum):
    PRINT = 0
    SPEAK = 1

class CheckResult(Enum):
    BREAK = 0
    CONTINUE = 1

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": f"{self.role}", "content": self.content}

class DialogueManager:
    def __init__(self, gpt_client, synthesizer=None, recognizer=None):
        self.gpt_client = gpt_client
        self.synthesizer = synthesizer
        self.recognizer = recognizer
        self.set_prompt()
        self.init_keywords()

    def init_keywords(self):
        self.InputMode = InputMode.KEYBOARD
        self.OutputMode = OutputMode.PRINT
        self.save_dialogue_words = ["保存", "save"]
        self.save_dialogue_pattern = self.build_pattern(self.save_dialogue_words)
        self.multiline_words = ["多行", "multiline"]
        self.multiline_pattern = self.build_pattern(self.multiline_words)
        self.switch_output_words = ["切换输出模式", "语音"]
        self.switch_output_pattern = self.build_pattern(self.switch_output_words)
        self.switch_input_words = ["切换输入模式", "切换", "switch", "change", "toggle"]
        self.switch_input_pattern = self.build_pattern(self.switch_input_words)
        self.exit_words = ["退出", "结束", "停止", "exit", "end", "quit"]
        self.exit_pattern = self.build_pattern(self.exit_words)

    def build_pattern(self, words):
        return "|".join([f"^({word})[。.]?\s*$" for word in words])

    def set_prompt(self, file_name=None):
        '''Method to set prompt and send diologue history
        
        请在调用run方法前调用该方法

        '''
        if file_name:
            try:
                file_name = os.path.join('saved_dialogue_history', file_name)
                if os.path.exists(file_name):
                    # with open(file_name, 'r', encoding='utf-8') as file:
                    with open(file_name, 'r') as file:
                        self.dialogue_history = json.load(file)
                    print("prompt初始化成功")
                else:
                    raise Exception(f'未找到文件{file_name}')
            except Exception as e:
                print(e)
        else:
            self.dialogue_history = [{"role": "system", "content": ''}]

    def save_dialogue(self):
        file_name = input("请输入要保存的文件名：")
        if not file_name:
            file_name = datetime.now().strftime("%Y%m%d_%H%M%S")  # 默认命名为日期+时间

        # 创建'saved_dialogue_history'文件夹
        if not os.path.exists('saved_dialogue_history'):
            os.makedirs('saved_dialogue_history')

        # 将对话记录保存为json文件
        with open(os.path.join('saved_dialogue_history', file_name + '.json'), 'w') as file:
            json.dump(self.dialogue_history, file)

        # 将对话记录保存为txt文件
        with open(os.path.join('saved_dialogue_history', file_name + '.txt'), 'w', encoding='utf-8') as file:
            for message in self.dialogue_history:
                file.write(f"{message['role']}: {message['content']}\n")

        print("对话记录已保存")

    def get_multiline_input(self):
        print("请输入多行内容，以END结束")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        return "\n".join(lines)

    def output(self, text):
        if self.synthesizer and self.OutputMode == OutputMode.SPEAK:
            self.synthesizer.text_to_speech_speaker_async(text)
        print(f"AI: {text}")

    def switch_InputMode(self):
        if self.InputMode == InputMode.KEYBOARD:
            if self.recognizer:
                self.InputMode = InputMode.VOICE
                self.output("已切换到语音输入模式，请说话")
            else:
                print("抱歉，语音输入模式不可用，请使用键盘输入")
        else:
            self.InputMode = InputMode.KEYBOARD
            print("已切换到键盘输入模式，请输入")

    def switch_OutputMode(self):
        if self.OutputMode == OutputMode.PRINT:
            if self.synthesizer:
                self.OutputMode = OutputMode.SPEAK
                self.output("已切换到语音输出模式")
            else:
                print("抱歉，语音输出模式不可用")
        else:
            self.OutputMode = OutputMode.PRINT
            print("已切换到文本输出模式，请输入")

    def check_key_words(self):
        self.CheckResult = None

        if re.match(self.save_dialogue_pattern, self.user_input):
            self.save_dialogue()
            self.CheckResult = CheckResult.CONTINUE
        if re.match(self.switch_output_pattern, self.user_input):
            self.switch_OutputMode()
            self.CheckResult = CheckResult.CONTINUE
        if re.match(self.switch_input_pattern, self.user_input):
            self.switch_InputMode()
            self.CheckResult = CheckResult.CONTINUE
        if re.match(self.multiline_pattern, self.user_input):
            self.user_input = self.get_multiline_input()

        if re.match(self.exit_pattern, self.user_input):
            self.exit_flag = True
            self.CheckResult = CheckResult.BREAK

    def run(self):
        self.exit_flag = False
        while not self.exit_flag:
            try:
                if self.InputMode == InputMode.VOICE:
                    print("User: ")
                    self.user_input = f"{self.recognizer.speech_to_text_microphone()}"
                    print(self.user_input)
                else:
                    self.user_input = input("User: ")

                self.check_key_words()
                if self.CheckResult == CheckResult.BREAK:
                    break
                elif self.CheckResult == CheckResult.CONTINUE:
                    continue

                user_message = Message("user", self.user_input)
                self.dialogue_history.append(user_message.to_dict())
                text = self.gpt_client.send_message(self.dialogue_history)
                self.output(text)
                assistant_message = Message("assistant", text)
                self.dialogue_history.append(assistant_message.to_dict())

            except Exception as e:
                print(f"Error: {e}")
                break
        print('感谢您使用本程序，再见！')


if __name__ == '__main__':
    # 用配置文件配置gpt
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

    # 手动配置gpt
    # url = "https://gpt-4-32k-api.com/" # replace with your own url
    # header = {"Authorization": "Bearer xxx"} # replace with your own header
    # gpt_client = GPTClient(url, header)

    # 运行对话系统
    dialogue_manager = DialogueManager(gpt_client)
    dialogue_manager.set_prompt('编程高手.json')
    dialogue_manager.run()
