from gpt_module import GPTClient
from dialogue_module import Message
from dialogue_module import DialogueManager
from batches_module import BatchRequestProcessor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, QInputDialog, QPlainTextEdit, QSplitter, QDialog, QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import traceback
import sys
import os

class GPTWorker(QRunnable):
    def __init__(self, dialogue_manager, user_message):
        super(GPTWorker, self).__init__()
        self.dialogue_manager = dialogue_manager
        self.user_message = user_message

    @pyqtSlot()
    def run(self):
        try:
            # 将用户输入加入对话历史
            user_message_obj = Message("user", self.user_message)
            self.dialogue_manager.dialogue_history.append(user_message_obj.to_dict())

            # 获取AI助手的回复
            assistant_message = self.dialogue_manager.gpt_client.send_request(self.dialogue_manager.dialogue_history)
            assistant_message_obj = Message("assistant", assistant_message)
            self.dialogue_manager.dialogue_history.append(assistant_message_obj.to_dict())

            self.dialogue_manager.parent.receive_message(assistant_message)

        except Exception as e:
            print("Error in GPTWorker:", e)
            traceback.print_exc()

class GPTBatchWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, batches_generator):
        super(GPTBatchWorker, self).__init__()
        self.batches_generator = batches_generator

    def run(self):
        try:
            self.batches_generator.generate_in_batches()
        except Exception as e:
            print("Error in GPTBatchWorker:", e)
            traceback.print_exc()
        finally:
            self.finished.emit()

class CustomPlainTextEdit(QPlainTextEdit):
    def __init__(self, app, parent=None):
        super(CustomPlainTextEdit, self).__init__(parent)
        self.app = app

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter: 插入换行符
                self.textCursor().insertText('\n')
            else:
                # Enter: 发送消息
                self.app.send_message()
        else:
            super().keyPressEvent(event)

class App(QMainWindow):
    def __init__(self, dialogue_manager):
        # QMetaType.registerMetaType(QTextCursor, "QTextCursor")

        super().__init__()
        self.dialogue_manager = dialogue_manager
        self.dialogue_manager.parent = self
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GUI")

        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建一个分隔条
        splitter = QSplitter(Qt.Vertical)
        
        # 设置字体和大小
        font = QFont("Cascadia Code", 11)

        # 创建一个文本编辑器来显示对话历史
        self.conversation_history = QTextEdit()
        self.conversation_history.setFont(font)  # 设置字体
        self.conversation_history.setReadOnly(True)
        splitter.addWidget(self.conversation_history)

        # 创建一个输入框供用户输入文本
        self.user_input = CustomPlainTextEdit(self, self)
        self.user_input.setFont(font)  # 设置字体
        splitter.addWidget(self.user_input)

        layout.addWidget(splitter)

        # 创建一个发送按钮来触发消息发送
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # 创建功能按钮
        self.init_feature_buttons(layout)

        # 设置窗口的布局
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_feature_buttons(self, layout):
        # 创建一个水平布局
        hbox = QHBoxLayout()

        # 创建设置Prompt按钮
        self.set_prompt_button = QPushButton("设置Prompt")
        self.set_prompt_button.clicked.connect(self.set_prompt)
        hbox.addWidget(self.set_prompt_button)

        # 创建保存对话按钮
        self.save_dialogue_button = QPushButton("保存对话")
        self.save_dialogue_button.clicked.connect(self.save_dialogue)
        hbox.addWidget(self.save_dialogue_button)

        # 创建批量生成按钮
        self.generate_in_batches_button = QPushButton("批量生成")
        self.generate_in_batches_button.clicked.connect(self.generate_in_batches)
        hbox.addWidget(self.generate_in_batches_button)

        # # 创建切换输入模式按钮
        # switch_input_mode_button = QPushButton("切换输入模式")
        # switch_input_mode_button.clicked.connect(self.switch_input_mode)
        # hbox.addWidget(switch_input_mode_button)

        # # 创建切换输出模式按钮
        # switch_output_mode_button = QPushButton("切换输出模式")
        # switch_output_mode_button.clicked.connect(self.switch_output_mode)
        # hbox.addWidget(switch_output_mode_button)

        layout.addLayout(hbox)

    def send_message(self):
        user_message = self.user_input.toPlainText()
        if not user_message:
            return

        self.conversation_history.append(f"User: {user_message}\n")
        self.user_input.clear()

        # 禁用发送和设置Prompt按钮
        self.send_button.setEnabled(False)
        self.set_prompt_button.setEnabled(False)

        # 创建GPTWorker并将其添加到线程池
        gpt_worker = GPTWorker(self.dialogue_manager, user_message)
        QThreadPool.globalInstance().start(gpt_worker)

    @pyqtSlot(str)
    def receive_message(self, assistant_message):
        # GPT请求完成后更新UI
        self.conversation_history.append(f"Assistant: {assistant_message}\n")
        self.send_button.setEnabled(True)
        self.set_prompt_button.setEnabled(True)

    def set_prompt(self):
        # 创建一个自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("设置Prompt")
        dialog_layout = QVBoxLayout()

        # 从文本输入
        text_input_layout = QHBoxLayout()
        text_input_label = QLabel("文本：")
        text_input_edit = QPlainTextEdit()
        text_input_edit.setFixedHeight(50)
        text_input_confirm_button = QPushButton("确认")
        text_input_layout.addWidget(text_input_label)
        text_input_layout.addWidget(text_input_edit)
        text_input_layout.addWidget(text_input_confirm_button)
        dialog_layout.addLayout(text_input_layout)

        # 从文件加载
        file_input_layout = QHBoxLayout()
        file_input_label = QLabel("文件：")
        file_input_combo = QComboBox()
        saved_history_path = os.path.join(os.getcwd(), 'saved_dialogue_history')
        prompt_files = [f[:-5] for f in os.listdir(saved_history_path) if f.endswith('.json')]
        file_input_combo.addItems(prompt_files)
        file_input_confirm_button = QPushButton("确认")
        file_input_layout.addWidget(file_input_label)
        file_input_layout.addWidget(file_input_combo)
        file_input_layout.addWidget(file_input_confirm_button)
        dialog_layout.addLayout(file_input_layout)

        # 设置对话框布局
        dialog.setLayout(dialog_layout)

        # 连接信号和槽
        text_input_confirm_button.clicked.connect(lambda: self.dialogue_manager.set_prompt(prompt_text=text_input_edit.text()))
        text_input_confirm_button.clicked.connect(dialog.accept)
        file_input_confirm_button.clicked.connect(lambda: self.dialogue_manager.set_prompt(prompt_file=file_input_combo.currentText()))
        file_input_confirm_button.clicked.connect(dialog.accept)

        # 显示对话框
        dialog.exec_()

    def save_dialogue(self):
        file_name, ok = QInputDialog.getText(self, "保存对话", "请输入要保存的文件名：")
        if ok and file_name:
            self.dialogue_manager.save_dialogue(file_name)
        elif ok:
            self.dialogue_manager.save_dialogue()

    # 切换语音模式，需配置azure
    def switch_input_mode(self):
        self.dialogue_manager.switch_InputMode()
    def switch_output_mode(self):
        self.dialogue_manager.switch_OutputMode()

    def generate_in_batches(self):
        # 获取要读取的CSV文件名
        message_filename, _ = QFileDialog.getOpenFileName(self, "打开CSV文件", "", "CSV Files (*.csv)")

        # 获取要使用的prompt文件名
        prompt_filename, ok = QInputDialog.getText(self, "设置Prompt文件", "请输入要使用的Prompt文件名：")
        
        self.batches_generator = BatchRequestProcessor(message_filename=message_filename, prompt_filename=prompt_filename)
        if ok and prompt_filename:
            # 创建GPTBatchWorker并将其添加到线程池
            self.batch_worker = GPTBatchWorker(self.batches_generator)
            self.batch_worker.finished.connect(self.on_batch_finished)
            self.batch_worker.start()

            # 禁用批量生成按钮
            self.generate_in_batches_button.setEnabled(False)

    @pyqtSlot()
    def on_batch_finished(self):
        # 批量生成结束后，启用批量生成按钮
        self.generate_in_batches_button.setEnabled(True)


if __name__ == "__main__":
    gpt_client = GPTClient()
    dialogue_manager = DialogueManager(gpt_client)

    app = QApplication(sys.argv)
    main_window = App(dialogue_manager)
    main_window.show()
    sys.exit(app.exec_())