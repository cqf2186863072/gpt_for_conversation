'''用于批量向gpt发送请求的脚本

'''

import multiprocessing
import csv
import json
import os
import configparser
from gpt_module import GPTClient

# 全局配置
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
prompt_filename = "小说家"

def process_row(row):
    keywords = row[1]
    file_name = os.path.join('saved_dialogue_history', prompt_filename + '.json')
    with open(file_name, 'r') as file:
        dialogue_history = json.load(file)
    dialogue_history.append({"role": "user", "content": f'{keywords}'})
    response = gpt_client.send_request(dialogue_history)
    # 返回更新后的行数据
    return row[0], keywords, response

def generate_in_batches(message_filename): 
    # 读取csv文件中的所有行数据
    with open(message_filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 创建一个进程池，指定进程数为4（可以根据实际情况调整）
    pool = multiprocessing.Pool(4)

    # 使用map方法将process_row函数和rows列表分配给不同的进程，并收集返回结果
    results = pool.map(process_row, rows)

    # 关闭进程池，释放资源
    pool.close()
    pool.join()

    # 将结果写到csv文件
    with open(message_filename, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)

if __name__ == '__main__':
    message_filename = "./batches/batches.csv"
    generate_in_batches(message_filename)
