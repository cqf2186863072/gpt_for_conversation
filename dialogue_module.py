# main.py
import re
from enum import Enum
from gpt_module import GPTClient

class Mode(Enum):
    KEYBOARD = 0
    VOICE = 1



class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def __dic__(self):
        return {"role": f"{self.role}", "content": self.content}

class DialogueManager:
    def __init__(self, gpt_client, synthesizer=None, recognizer=None):
        self.gpt_client = gpt_client
        self.synthesizer = synthesizer
        self.recognizer = recognizer

        self.dialogue_history = [{"role": "system", "content": ''}]
        self.mode = Mode.KEYBOARD
        self.switch_words = ["切换模式", "切换", "switch", "change", "toggle"]
        self.switch_pattern = "|".join([f"^({word})[。.]?\s*$" for word in self.switch_words])
        self.exit_words = ["退出", "结束", "停止", "exit", "end", "quit"]
        self.exit_pattern = "|".join([f"^({word})[。.]?\s*$" for word in self.exit_words])

    def print_and_speak(self, text):
        if self.synthesizer:
            self.synthesizer.text_to_speech_async(text)
        print(f"AI: {text}")

    def switch_mode(self):
        if self.mode == Mode.KEYBOARD:
            if self.recognizer:
                self.mode = Mode.VOICE
                self.print_and_speak("已切换到语音输入模式，请说话")
            else:
                print("抱歉，语音输入模式不可用，请使用键盘输入")
        else:
            self.mode = Mode.KEYBOARD
            print("已切换到键盘输入模式，请输入")

    def run(self):
        exit_flag = False

        while not exit_flag:
            try:
                if self.mode == Mode.VOICE:
                    print("User: ")
                    user_input = f"{self.recognizer.speech_to_text()}"
                    print(user_input)
                else:
                    user_input = input("User: ")

                if re.match(self.switch_pattern, user_input):
                    self.switch_mode()
                    continue

                if re.match(self.exit_pattern, user_input):
                    exit_flag = True
                    break

                user_message = Message("user", user_input)
                self.dialogue_history.append(user_message.__dic__())

                text = self.gpt_client.send_message(self.dialogue_history)

                self.print_and_speak(text)

                system_message = Message("system", text)
                self.dialogue_history.append(system_message.__dic__())

            except Exception as e:
                print(f"Error: {e}")
                break

        print('感谢您使用本程序，再见！')

# for test
if __name__ == '__main__':
    url = "https://gpt-4-32k-api.com/" # replace with your own url
    header = {"Authorization": "Bearer xxx"} # replace with your own header
    gpt_client = GPTClient(url, header)
    dialogue_manager = DialogueManager(gpt_client)
    dialogue_manager.run()
