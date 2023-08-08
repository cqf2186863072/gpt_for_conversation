# gpt_for_conversation

## 一、配置

### 1. 配置gpt

在根目录创建`config.ini`，按照以下格式配置好url和token

```ini
[gpt]
url = 
header = {
    'Content-Type': 'application/json',
    'token': ''
    }
```

### 2. 配置Azure(可选)

依照[官网教程](https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python)配置环境变量，支持语言可在根目录`language_and_voice.csv`中添加

### 3. 配置批处理关键词

在`./batches/batches.csv`中

## 二、启动

### 1. 运行`__main__.py`
