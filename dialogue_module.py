import re
from enum import Enum
from gpt_module import GPTClient


class InputMode(Enum):
    KEYBOARD = 0
    VOICE = 1

class OutputMode(Enum):
    PRINT = 0
    SPEAK = 1

class Message:
    '''This is a class that orgnize a message'''
    def __init__(self, role, content):
        self.role = role
        self.content = content


    def __dic__(self):
        '''This is a method that converts the message role and content into a dictionary'''
        return {"role": f"{self.role}", "content": self.content}

class DialogueManager:
    def __init__(self, gpt_client, synthesizer=None, recognizer=None):
        '''This is the constructor of the class

        Args:
        gpt_client: A GPTClient object that communicates with the GPT-4-32k API
        synthesizer: A Synthesizer object that converts text to speech (optional)
        recognizer: A Recognizer object that converts speech to text (optional)
        
        '''
        self.gpt_client = gpt_client
        self.synthesizer = synthesizer
        self.recognizer = recognizer
        self.set_prompts()
        

        # 配置对话模式和指令词
        #TODO 给指令一个特殊的格式
        self.InputMode = InputMode.KEYBOARD
        self.OutputMode = OutputMode.PRINT
        self.multiline_words = ["多行", "multiline"]
        self.multiline_pattern = "|".join([f"^({word})[。.]?\s*$" for word in self.multiline_words])
        self.switch_output_words = ["切换输出模式", "语音"]
        self.switch_output_pattern = "|".join([f"^({word})[。.]?\s*$" for word in self.switch_output_words])
        self.switch_input_words = ["切换输入模式", "切换", "switch", "change", "toggle"]
        self.switch_input_pattern = "|".join([f"^({word})[。.]?\s*$" for word in self.switch_input_words])
        self.exit_words = ["退出", "结束", "停止", "exit", "end", "quit"]
        self.exit_pattern = "|".join([f"^({word})[。.]?\s*$" for word in self.exit_words])

    #TODO 配置对话历史的方法
    def set_prompts(self):
        self.dialogue_history = [{"role": "system", "content": ''}]

    def get_multiline_input(self):
        '''This is a method that gets multiple lines of input from the user

        Return:
            A string that contains the user input with newline characters
    
        '''    
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

    def run(self):
        self.exit_flag = False
        while not self.exit_flag:
            try:
                if self.InputMode == InputMode.VOICE:
                    print("User: ")
                    user_input = f"{self.recognizer.speech_to_text_microphone()}"
                    print(user_input)
                else:
                    user_input = input("User: ")

                if re.match(self.multiline_pattern, user_input):
                    user_input = self.get_multiline_input()
                if re.match(self.switch_output_pattern, user_input):
                    self.switch_OutputMode()
                    continue
                if re.match(self.switch_input_pattern, user_input):
                    self.switch_InputMode()
                    continue
                if re.match(self.exit_pattern, user_input):
                    self.exit_flag = True
                    break

                user_message = Message("user", user_input)
                self.dialogue_history.append(user_message.__dic__())
                text = self.gpt_client.send_message(self.dialogue_history)
                self.output(text)
                system_message = Message("system", text)
                self.dialogue_history.append(system_message.__dic__())

            except Exception as e:
                print(f"Error: {e}")
                break
        print('感谢您使用本程序，再见！')


if __name__ == '__main__':
    url = "https://gpt-4-32k-api.com/" # replace with your own url
    header = {"Authorization": "Bearer xxx"} # replace with your own header
    gpt_client = GPTClient(url, header)
    dialogue_manager = DialogueManager(gpt_client)
    dialogue_manager.run()
