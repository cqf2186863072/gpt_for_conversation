import re
import os
import configparser
import json
import threading
import time
import azure_module
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

        self.set_prompt_words = ["设置", "set"]
        self.set_prompt_pattern = self.build_pattern(self.set_prompt_words)

        self.save_dialogue_words = ["保存", "save"]
        self.save_dialogue_pattern = self.build_pattern(self.save_dialogue_words)

        self.switch_OutputMode_words = ["切换输出模式", "语音"]
        self.switch_OutputMode_pattern = self.build_pattern(self.switch_OutputMode_words)

        self.switch_InputMode_words = ["切换输入模式", "切换", "switch", "change", "toggle"]
        self.switch_InputMode_pattern = self.build_pattern(self.switch_InputMode_words)

        self.multiline_words = ["多行", "multiline"]
        self.multiline_pattern = self.build_pattern(self.multiline_words)

        self.exit_words = ["退出", "结束", "停止", "exit", "end", "quit"]
        self.exit_pattern = self.build_pattern(self.exit_words)

    def build_pattern(self, words):
        return "|".join([f"^({word})[。.]?\s*$" for word in words])

    def check_key_words(self):
        self.CheckResult = None

        if re.match(self.set_prompt_pattern, self.user_input):
            prompt_text = input("请输入prompt(system's content)（不需要就Enter）：")
            prompt_file = input("请输入对话记录文件名（不需要就Enter）：")
            self.set_prompt(prompt_text=prompt_text, prompt_file=prompt_file)
            self.CheckResult = CheckResult.CONTINUE
        if re.match(self.save_dialogue_pattern, self.user_input):
            self.save_dialogue()
            self.CheckResult = CheckResult.CONTINUE
        if re.match(self.switch_OutputMode_pattern, self.user_input):
            self.switch_OutputMode()
            self.CheckResult = CheckResult.CONTINUE
        if re.match(self.switch_InputMode_pattern, self.user_input):
            self.switch_InputMode()
            self.CheckResult = CheckResult.CONTINUE


        if re.match(self.multiline_pattern, self.user_input):
            self.user_input = self.get_multiline_input()

        if re.match(self.exit_pattern, self.user_input):
            self.exit_flag = True
            self.CheckResult = CheckResult.BREAK

    def set_prompt(self, prompt_text=None, prompt_file=None):
        '''用来设置prompt的方法

        Args:
            prompt_text: 文本形式的prompt
            prompt_file: 文件形式的prompt

        '''
        if prompt_file:
            try:
                file_name = os.path.join('saved_dialogue_history', prompt_file + '.json')
                if os.path.exists(file_name):
                    # with open(file_name, 'r', encoding='utf-8') as file:
                    with open(file_name, 'r') as file:
                        self.dialogue_history = json.load(file)
                    print(f"'{file_name}'初始化成功")
                else:
                    raise Exception(f'未找到文件{file_name}')
            except Exception as e:
                print(e)
        elif prompt_text:
            self.dialogue_history = [{"role": "system", "content": f'{prompt_text}'}]
            print(f"'{prompt_text}'初始化成功")
        else:
            self.dialogue_history = [{"role": "system", "content": ''}]
            print("未设置prompt")

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

    def get_multiline_input(self):
        print("请输入多行内容，以END结束")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        return "\n".join(lines)

    def show_loading(self):
        start_time = time.time()
        while self.loading_flag:
            print('加载中...', end='\r')
            time.sleep(2)
            if time.time() - start_time > 60:
                print('长时间未响应，建议结束程序')
                break

    def output(self, text):
        if self.synthesizer and self.OutputMode == OutputMode.SPEAK:
            self.synthesizer.text_to_speech_speaker(text)
        print(f"assistant: {text}")

    def send_and_receive(self):
        text = self.gpt_client.send_request(self.dialogue_history)
        self.loading_flag = False
        self.output(text)
        assistant_message = Message("assistant", text)
        self.dialogue_history.append(assistant_message.to_dict())

    def run(self):
        self.exit_flag = False
        self.loading_flag = False
        while not self.exit_flag:
            try:
                # 获取用户输入
                if self.InputMode == InputMode.VOICE:
                    print("User: ")
                    self.user_input = self.recognizer.speech_to_text_microphone()
                    print(self.user_input)
                else:
                    self.user_input = input("User: ")

                # 检查关键词
                self.check_key_words()
                if self.CheckResult == CheckResult.BREAK:
                    break
                elif self.CheckResult == CheckResult.CONTINUE:
                    continue

                # 将用户输入加入对话历史
                user_message = Message("user", self.user_input)
                self.dialogue_history.append(user_message.to_dict())
                
                # 启动并等待线程结束
                self.loading_flag = True
                t1 = threading.Thread(target=self.send_and_receive)
                t1.start()
                t2 = threading.Thread(target=self.show_loading)
                t2.start()
                t1.join()
                t2.join()

            except Exception as e:
                print(f"Error: {e}")
                break
        print('感谢您使用本程序，再见！')

if __name__ == '__main__':
    gpt_client = GPTClient()

    # # 配置azure
    # selector = azure_module.LanguageAndVoiceSelector(timeout=3)
    # language, voice = selector.choose_language_and_voice()
    # speech_synthesizer = azure_module.SpeechSynthesizer(language, voice)
    # speech_recognizer = azure_module.SpeechRecognizer(language)

    # 带有语音系统的对话助手
    # dialogue_manager = DialogueManager(gpt_client, speech_synthesizer, speech_recognizer)

    # 运行对话系统
    dialogue_manager = DialogueManager(gpt_client)
    dialogue_manager.run()