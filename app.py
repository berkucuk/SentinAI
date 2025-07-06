import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QStatusBar, QListWidget,
    QStackedWidget, QProgressBar, QMessageBox, QGroupBox, QSplitter, QStyle,
    QComboBox
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon, QGuiApplication

from custom_widgets import SimpleSwitch
from passgenai import passgen
from osintai import osint

DARK_MODE_STYLESHEET = """
    QWidget {
        background-color: #2e2f30;
        color: #e0e0e0;
        font-family: Arial;
    }
    QMainWindow {
        background-color: #242526;
    }
    QComboBox {
        border: 1px solid #555;
        border-radius: 3px;
        padding: 1px 18px 1px 3px;
        min-width: 6em;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left-width: 1px;
        border-left-color: #555;
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #555;
        background-color: #3a3b3c;
        selection-background-color: #4c8be8;
    }
    QGroupBox {
        font-size: 11pt;
        font-weight: bold;
        border: 1px solid #444;
        border-radius: 8px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
    }
    QSplitter::handle {
        background-color: #444;
    }
    QSplitter::handle:vertical {
        height: 5px;
    }
    QTextEdit, QListWidget {
        background-color: #3a3b3c;
        border: 1px solid #555555;
        border-radius: 5px;
        padding: 5px;
        font-size: 10pt;
    }
    QPushButton {
        background-color: #4c8be8;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        font-size: 10pt;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5a9eff;
    }
    QPushButton:disabled {
        background-color: #555555;
        color: #999999;
    }
    QLabel {
        font-size: 10pt;
    }
    QStatusBar {
        color: #cccccc;
    }
    QProgressBar {
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
        background-color: #3a3b3c;
    }
    QProgressBar::chunk {
        background-color: #4c8be8;
    }
"""

LANGUAGES = {
    "en": {
        "window_title": "Cybersecurity Assistant",
        "language_label": "Language:",
        "groupbox_input_title": "1. Select Mode and Enter Data",
        "groupbox_results_title": "2. Results",
        "passgen_label": "PassGen",
        "osint_label": "OSINT",
        "run_button": " Execute",
        "copy_button": "Copy Selected",
        "status_ready": "Ready",
        "status_running_osint": "Running OSINT Investigator...",
        "status_running_passgen": "Running Wordlist Generator...",
        "status_finished": "Task finished. Ready.",
        "status_error": "An error occurred.",
        "status_no_password_selected": "No password selected to copy.",
        "status_copied": "Copied '{text}' to clipboard.",
        "error_input_empty_title": "Input Error",
        "error_input_empty_msg": "Input cannot be empty.",
        "error_execution_title": "Execution Error",
        "placeholder_passgen": "Enter personal information to generate a wordlist...\nExample: name=Berk, surname=Küçük, birthdate=2001, team=trabzonspor, pet=sushi, min_len=6, max_len=12",
        "placeholder_osint": "Enter a full name, username, or keywords for OSINT investigation...\nExample: John Doe, johndoe99, software developer new york"
    },
    "tr": {
        "window_title": "Siber Güvenlik Asistanı",
        "language_label": "Dil:",
        "groupbox_input_title": "1. Mod Seç ve Veri Gir",
        "groupbox_results_title": "2. Sonuçlar",
        "passgen_label": "Parola Üretici",
        "osint_label": "OSINT Aracı",
        "run_button": " Çalıştır",
        "copy_button": "Seçileni Kopyala",
        "status_ready": "Hazır",
        "status_running_osint": "OSINT Araştırması Yürütülüyor...",
        "status_running_passgen": "Kelime Listesi Oluşturuluyor...",
        "status_finished": "Görev tamamlandı. Hazır.",
        "status_error": "Bir hata oluştu.",
        "status_no_password_selected": "Kopyalamak için parola seçilmedi.",
        "status_copied": "'{text}' panoya kopyalandı.",
        "error_input_empty_title": "Girdi Hatası",
        "error_input_empty_msg": "Girdi alanı boş olamaz.",
        "error_execution_title": "Çalıştırma Hatası",
        "placeholder_passgen": "Kelime listesi oluşturmak için kişisel bilgi girin...\nÖrnek: isim=Berk, soyisim=Küçük, dogum=2001, takim=trabzonspor, evcilhayvan=sushi, min_uzunluk=6, max_uzunluk=12",
        "placeholder_osint": "OSINT araştırması için bir tam isim, kullanıcı adı veya anahtar kelime girin...\nÖrnek: John Doe, johndoe99, yazılım geliştirici new york"
    },
    "ru": {
        "window_title": "Ассистент по кибербезопасности",
        "language_label": "Язык:",
        "groupbox_input_title": "1. Выберите режим и введите данные",
        "groupbox_results_title": "2. Результаты",
        "passgen_label": "Генератор паролей",
        "osint_label": "Инструмент OSINT",
        "run_button": " Выполнить",
        "copy_button": "Копировать",
        "status_ready": "Готово",
        "status_running_osint": "Выполняется OSINT-расследование...",
        "status_running_passgen": "Создание списка слов...",
        "status_finished": "Задача завершена. Готово.",
        "status_error": "Произошла ошибка.",
        "status_no_password_selected": "Пароль для копирования не выбран.",
        "status_copied": "Скопировано '{text}' в буфер обмена.",
        "error_input_empty_title": "Ошибка ввода",
        "error_input_empty_msg": "Поле ввода не может быть пустым.",
        "error_execution_title": "Ошибка выполнения",
        "placeholder_passgen": "Введите личную информацию для создания списка слов...\nПример: имя=Иван, фамилия=Иванов, датарождения=1990, команда=спартак, питомец=шарик, мин_длина=6, макс_длина=12",
        "placeholder_osint": "Введите полное имя, имя пользователя или ключевые слова для OSINT-расследования...\nПример: Иван Иванов, ivanivanov90, разработчик москва"
    }
}


class Worker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_lang = "en"
        self.setGeometry(100, 100, 850, 750)
        
        icon_filename = "icon.png" 
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", icon_filename)

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"UYARI: Özel ikon '{icon_path}' adresinde bulunamadı. Varsayılan ikon kullanılıyor.")
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.language_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Türkçe", "tr")
        self.lang_combo.addItem("Русский", "ru")
        lang_layout.addWidget(self.language_label)
        lang_layout.addWidget(self.lang_combo)
        main_layout.addLayout(lang_layout)

        self.input_groupbox = QGroupBox()
        input_layout = QVBoxLayout(self.input_groupbox)
        input_layout.setSpacing(10)
        input_layout.setContentsMargins(10, 20, 10, 10)
        
        selector_layout = QHBoxLayout()
        selector_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.passgen_label = QLabel()
        self.passgen_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.agent_selector = SimpleSwitch()
        self.osint_label = QLabel()
        self.osint_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        selector_layout.addWidget(self.passgen_label)
        selector_layout.addWidget(self.agent_selector)
        selector_layout.addWidget(self.osint_label)
        input_layout.addLayout(selector_layout)

        self.input_text = QTextEdit()
        input_layout.addWidget(self.input_text)
        
        action_layout = QHBoxLayout()
        self.run_button = QPushButton()
        self.run_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.run_button.setMinimumHeight(35)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        action_layout.addWidget(self.run_button)
        action_layout.addWidget(self.progress_bar)
        input_layout.addLayout(action_layout)
        
        self.output_groupbox = QGroupBox()
        output_layout = QVBoxLayout(self.output_groupbox)
        output_layout.setContentsMargins(10, 20, 10, 10)

        self.output_stack = QStackedWidget()
        self.setup_passgen_output()
        self.setup_osint_output()
        output_layout.addWidget(self.output_stack)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.input_groupbox)
        splitter.addWidget(self.output_groupbox)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        main_layout.addWidget(splitter)

        self.setCentralWidget(main_widget)
        self.setStatusBar(QStatusBar(self))

        self.run_button.clicked.connect(self.run_agent_task)
        self.copy_button.clicked.connect(self.copy_selected_password)
        self.agent_selector.stateChanged.connect(self.switch_output_view)
        
        self.lang_combo.currentIndexChanged.connect(self.switch_language_by_index)

        self.switch_language("en")

    def switch_language_by_index(self, index: int):
        lang_code = self.lang_combo.itemData(index)
        if lang_code:
            self.switch_language(lang_code)

    def switch_language(self, lang_code: str):
        self.current_lang = lang_code
        lang = LANGUAGES[lang_code]

        index = self.lang_combo.findData(lang_code)
        if index != -1:
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentIndex(index)
            self.lang_combo.blockSignals(False)

        self.setWindowTitle(lang["window_title"])
        self.language_label.setText(lang["language_label"])
        self.input_groupbox.setTitle(lang["groupbox_input_title"])
        self.output_groupbox.setTitle(lang["groupbox_results_title"])
        self.passgen_label.setText(lang["passgen_label"])
        self.osint_label.setText(lang["osint_label"])
        self.run_button.setText(lang["run_button"])
        self.copy_button.setText(lang["copy_button"])
        self.statusBar().showMessage(lang["status_ready"])
        self.switch_output_view()

    def setup_passgen_output(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 0)
        
        self.passgen_list_widget = QListWidget()
        self.copy_button = QPushButton()
        self.copy_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.copy_button.setFixedWidth(180)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button)
        
        layout.addWidget(self.passgen_list_widget)
        layout.addLayout(button_layout)
        
        self.output_stack.addWidget(container)

    def setup_osint_output(self):
        self.osint_result_text = QTextEdit()
        self.osint_result_text.setReadOnly(True)
        self.osint_result_text.setAcceptRichText(True) 
        self.output_stack.addWidget(self.osint_result_text)

    def switch_output_view(self):
        lang = LANGUAGES[self.current_lang]
        if self.agent_selector.isChecked():
            self.output_stack.setCurrentIndex(1)
            self.input_text.setPlaceholderText(lang["placeholder_osint"])
        else:
            self.output_stack.setCurrentIndex(0)
            self.input_text.setPlaceholderText(lang["placeholder_passgen"])

    def run_agent_task(self):
        lang = LANGUAGES[self.current_lang]
        is_osint_mode = self.agent_selector.isChecked()
        user_input = self.input_text.toPlainText().strip()

        if not user_input:
            QMessageBox.warning(self, lang["error_input_empty_title"], lang["error_input_empty_msg"])
            return

        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) 

        if is_osint_mode:
            self.statusBar().showMessage(lang["status_running_osint"])
            self.worker = Worker(osint, user_input, self.current_lang)
        else:
            self.statusBar().showMessage(lang["status_running_passgen"])
            self.worker = Worker(passgen, user_input)
        
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.error.connect(self.display_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_task_finished(self, result):
        lang = LANGUAGES[self.current_lang]
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.statusBar().showMessage(lang["status_finished"])
        
        if self.agent_selector.isChecked():
            self.osint_result_text.setMarkdown(result)
        else:
            self.passgen_list_widget.clear()
            if "Success!" in result:
                try:
                    filename = result.split("'")[1]
                    with open(filename, 'r', encoding='utf-8') as f:
                        passwords = [line.strip() for line in f if line.strip()]
                    self.passgen_list_widget.addItems(passwords)
                    status_msg = f"{lang['status_finished']} {len(passwords)} passwords generated."
                    if self.current_lang == 'tr':
                        status_msg = f"{lang['status_finished']} {len(passwords)} adet parola oluşturuldu."
                    elif self.current_lang == 'ru':
                        status_msg = f"{lang['status_finished']} Сгенерировано {len(passwords)} паролей."
                    self.statusBar().showMessage(status_msg)
                except (IOError, IndexError) as e:
                    self.passgen_list_widget.addItem(f"Could not read result file: {e}")
            else:
                self.passgen_list_widget.addItem(result)

    def copy_selected_password(self):
        lang = LANGUAGES[self.current_lang]
        selected_items = self.passgen_list_widget.selectedItems()
        if not selected_items:
            self.statusBar().showMessage(lang["status_no_password_selected"])
            return
        
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(selected_items[0].text())
        self.statusBar().showMessage(lang["status_copied"].format(text=selected_items[0].text()))

    def display_error(self, error_message):
        lang = LANGUAGES[self.current_lang]
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.statusBar().showMessage(lang["status_error"])
        QMessageBox.critical(self, lang["error_execution_title"], error_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_MODE_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())