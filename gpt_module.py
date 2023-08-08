import requests
import configparser
import os

class GPTClient:
    def __init__(self):
        self.url, self.header = self.get_config()

    def get_config(self):
        # 读取config.ini配置gpt
        config = configparser.ConfigParser()
        file_dir = os.path.dirname(__file__)
        config_file = os.path.join(file_dir, 'config.ini')
        try:
            if os.path.exists(config_file): 
                config.read(config_file)
                url = config.get('gpt', 'url')
                header = eval(config.get('gpt', 'header'))
                return url, header
            else:
                raise Exception("请配置config.ini")
        except Exception as e:
            print(e)

    def send_request(self, message, temperature = 0.5):
        '''sends requests to openai

        Args:
            message: A dictionary list including dialogue history and new input
            temperature: Randomness of responses

        '''
        data = {
            'model_name': 'gpt-4-32k',
            'message': message,
            'temperature': temperature
        }

        try:
            response = requests.post(url=self.url, headers=self.header, json=data)
            if response.status_code == 200:
                return response.json()['result']
            else:
                raise Exception(f"Request failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request exception: {e}")
        