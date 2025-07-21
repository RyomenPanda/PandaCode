import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QInputDialog
from PyQt6.QtGui import QFileSystemModel, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import QRegularExpression
from PyQt6.uic import loadUi
import qdarkstyle

from file_service import FileService
from terminal_service import TerminalService
from ai_service import AIService
from git_service import GitService

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('settings_dialog.ui', self)

        self.config = self.load_config()
        self.api_key_input.setText(self.config.get('gemini_api_key', ''))

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_config(self):
        self.config['gemini_api_key'] = self.api_key_input.text()
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    def accept(self):
        self.save_config()
        super().accept()

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))  # A VS Code-like blue
        keywords = ["and", "as", "assert", "break", "class", "continue", "def",
                    "del", "elif", "else", "except", "False", "finally", "for",
                    "from", "global", "if", "import", "in", "is", "lambda",
                    "None", "nonlocal", "not", "or", "pass", "raise", "return",
                    "True", "try", "while", "with", "yield"]
        for keyword in keywords:
            pattern = QRegularExpression(f"\\b{keyword}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # String format
        quotation_format = QTextCharFormat()
        quotation_format.setForeground(QColor(214, 157, 133))  # A VS Code-like orange
        self.highlighting_rules.append((QRegularExpression("\".*\""), quotation_format))
        self.highlighting_rules.append((QRegularExpression("'.*'"), quotation_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))  # A VS Code-like green
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class PandaCodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('main_window.ui', self)

        self.file_service = FileService('workspace')
        self.terminal_service = TerminalService(self.file_service.workspace_dir)
        self.ai_service = AIService()
        self.git_service = GitService(self.file_service.workspace_dir)
        self.current_file_path = None

        self.setup_ui()
        self.connect_signals()
        self.load_api_key()
        self.update_git_status()

    def setup_ui(self):
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.file_service.workspace_dir)
        self.fileExplorer.setModel(self.file_model)
        self.fileExplorer.setRootIndex(self.file_model.index(self.file_service.workspace_dir))
        self.highlighter = PythonHighlighter(self.editor.document())

    def connect_signals(self):
        self.actionNew.triggered.connect(self.new_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionExit.triggered.connect(self.close)
        self.actionRun_Code.triggered.connect(self.run_code)
        self.fileExplorer.doubleClicked.connect(self.file_explorer_double_clicked)
        self.terminal_input.returnPressed.connect(self.run_terminal_command)
        self.ai_send_button.clicked.connect(self.send_ai_message)
        self.ai_refactor_button.clicked.connect(self.refactor_code)
        self.ai_test_button.clicked.connect(self.generate_tests)
        self.commit_button.clicked.connect(self.commit_changes)
        self.bottom_tabs.currentChanged.connect(self.tab_changed)

    def load_api_key(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('gemini_api_key')
                if api_key:
                    os.environ['GEMINI_API_KEY'] = api_key
                    self.ai_service = AIService() # Re-initialize with new key
        except FileNotFoundError:
            pass

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.load_api_key()

    def send_ai_message(self):
        user_message = self.ai_input.text()
        if not user_message:
            return

        self.ai_input.clear()
        self.ai_chat_history.append(f"You: {user_message}")

        context = {}
        if self.current_file_path:
            content = self.editor.toPlainText()
            language = self.file_service.detect_language(self.current_file_path)
            context['currentFile'] = {
                'path': self.current_file_path,
                'content': content,
                'language': language
            }
        
        response = self.ai_service.chat(user_message, context)
        
        if response.success:
            self.ai_chat_history.append(f"AI: {response.content}")
        else:
            self.ai_chat_history.append(f"AI Error: {response.error}")

    def new_file(self):
        self.editor.clear()
        self.current_file_path = None
        self.setWindowTitle("PandaCode IDE - New File")

    def open_file(self, file_path=None):
        if not isinstance(file_path, str):
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", self.file_service.workspace_dir)
        
        if file_path:
            self.current_file_path = file_path
            content = self.file_service.read_file(file_path)
            self.editor.setPlainText(content)
            self.setWindowTitle(f"PandaCode IDE - {file_path}")

    def save_file(self):
        if self.current_file_path:
            content = self.editor.toPlainText()
            self.file_service.write_file(self.current_file_path, content)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", self.file_service.workspace_dir)
        if file_path:
            self.current_file_path = file_path
            self.save_file()

    def run_code(self):
        if self.current_file_path:
            self.save_file()
            command = f"python {self.current_file_path}"
            result = self.terminal_service.execute_command(command)
            self.terminal_output.append(f"$ {command}\n{result.output}\n{result.error}")

    def run_terminal_command(self):
        command = self.terminal_input.text()
        self.terminal_input.clear()
        result = self.terminal_service.execute_command(command)
        self.terminal_output.append(f"$ {command}\n{result.output}\n{result.error}")
        
    def file_explorer_double_clicked(self, index):
        absolute_path = self.file_model.filePath(index)
        if self.file_model.fileInfo(index).isFile():
            relative_path = os.path.relpath(absolute_path, self.file_service.workspace_dir)
            self.open_file(relative_path)

    def refactor_code(self):
        if not self.current_file_path:
            self.ai_chat_history.append("AI Error: Please open a file to refactor.")
            return

        instruction, ok = QInputDialog.getText(self, 'Refactor Code', 'Enter refactoring instruction:')
        if not ok or not instruction:
            return

        code = self.editor.toPlainText()
        language = self.file_service.detect_language(self.current_file_path)
        response = self.ai_service.refactor_code(code, language, instruction)

        if response.success:
            self.editor.setPlainText(response.content)
            self.ai_chat_history.append("AI: Code refactored successfully.")
        else:
            self.ai_chat_history.append(f"AI Error: {response.error}")

    def generate_tests(self):
        if not self.current_file_path:
            self.ai_chat_history.append("AI Error: Please open a file to generate tests for.")
            return

        code = self.editor.toPlainText()
        language = self.file_service.detect_language(self.current_file_path)
        response = self.ai_service.generate_tests(code, language)

        if response.success:
            test_file_path = self.get_test_file_path(self.current_file_path)
            self.file_service.write_file(test_file_path, response.content)
            self.open_file(test_file_path)
            self.ai_chat_history.append(f"AI: Tests generated and saved to {test_file_path}")
        else:
            self.ai_chat_history.append(f"AI Error: {response.error}")

    def get_test_file_path(self, file_path):
        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        return os.path.join(directory, f"test_{name}{ext}")

    def tab_changed(self, index):
        if self.bottom_tabs.tabText(index) == "Source Control":
            self.update_git_status()

    def update_git_status(self):
        status = self.git_service.get_status()
        self.git_branch_label.setText(f"Branch: {status.branch}")
        self.git_files_list.clear()
        self.git_files_list.addItems(status.modified_files)
        self.git_files_list.addItems(status.untracked_files)

    def commit_changes(self):
        message = self.commit_message_input.text()
        if not message:
            # You might want to show an error message here
            return
        
        # For simplicity, this commits all changes. A more advanced implementation
        # would let the user select which files to commit.
        self.git_service.commit_changes(message)
        self.commit_message_input.clear()
        self.update_git_status()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    window = PandaCodeApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
