import requests

class GPTClient:
    def __init__(self, url, header):
        self.url = url
        self.header = header

    def send_message(self, message):
        data = {
            'model_name': 'gpt-4-32k',
            'message': message,
            'temperature': 0
        }

        try:
            response = requests.post(url=self.url, headers=self.header, json=data)
            if response.status_code == 200:
                return response.json()['result']
            else:
                raise Exception(f"Request failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request exception: {e}")
