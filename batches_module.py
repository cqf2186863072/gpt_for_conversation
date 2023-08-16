import threading
import csv
import json
import os
from gpt_module import GPTClient
from queue import Queue

class BatchRequestProcessor:
    def __init__(self, prompt_filename, message_filename, num_threads=4):
        self.gpt_client = GPTClient()
        self.prompt_filename = prompt_filename
        self.message_filename = message_filename
        self.num_threads = num_threads
        self.lock = threading.Lock()
        self.results = []

    def process_row(self, q):
        while not q.empty():
            row = q.get()
            keywords = row[1]
            file_name = os.path.join('saved_dialogue_history', self.prompt_filename + '.json')
            with open(file_name, 'r') as file:
                dialogue_history = json.load(file)
            dialogue_history.append({"role": "user", "content": f'{keywords}'})
            response = self.gpt_client.send_request(dialogue_history)
            q.task_done()
            with self.lock:
                self.results.append((row[0], keywords, response))

    def generate_in_batches(self): 
        # 读取csv文件中的所有行数据
        with open(self.message_filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # 创建一个任务队列
        task_queue = Queue()
        for row in rows:
            task_queue.put(row)

        # 创建线程
        threads = [threading.Thread(target=self.process_row, args=(task_queue,)) for _ in range(self.num_threads)]

        # 启动线程
        for thread in threads:
            thread.start()

        # 等待所有任务完成
        task_queue.join()

        # 将结果写到csv文件
        with open(self.message_filename, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.results)

if __name__ == '__main__':
    prompt_filename = "小说家"
    message_filename = "./batches/batches.csv"
    processor = BatchRequestProcessor(prompt_filename, message_filename)
    processor.generate_in_batches()