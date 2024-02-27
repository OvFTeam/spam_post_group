import json
import os
import sys

import requests
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
                             QWidget)
from selenium import webdriver
from selenium.webdriver.common.by import By


class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.stopped = False

    def run(self):
        tai_khoan = self.config['tai_khoan']
        mat_khau = self.config['mat_khau']
        ma_xac_minh = self.config['ma_xac_minh']
        link_group = self.config['link_group'].split('\n')
        noi_dung = self.config['noi_dung']
        duong_dan_anh = self.config['duong_dan_anh']

        driver = webdriver.Chrome()
        driver.get('https://mbasic.facebook.com')

        username_input = driver.find_element(By.ID, 'm_login_email')
        username_input.send_keys(tai_khoan)

        password_input = driver.find_element(By.NAME, 'pass')
        password_input.send_keys(mat_khau)

        login_button = driver.find_element(By.NAME, 'login')
        login_button.click()

        try:
            password_input = driver.find_element(By.NAME, 'pass')
            with open(tai_khoan + '_log.txt', 'a') as f:
                f.write(tai_khoan + ': Sai mật khẩu' + '\n')
            return
        except:
            pass

        response = requests.get(f"https://2fa.live/tok/{ma_xac_minh}")
        data = response.json()
        token = data["token"]

        try:
            code_input = driver.find_element(By.ID, 'approvals_code')
            code_input.send_keys(token)
            submit_button = driver.find_element(
                By.ID, 'checkpointSubmitButton')
            submit_button.click()
        except:
            pass

        for i in range(8):
            if i == 7 or self.stopped:
                with open(tai_khoan + '.txt', 'a') as f:
                    f.write(tai_khoan + ': Nick ngỏm mẹ r :v' + '\n')
                driver.quit()
                self.finished.emit()
                return

            current_url = driver.current_url
            if "checkpoint" in current_url:
                submit_button = driver.find_element(
                    By.ID, 'checkpointSubmitButton')
                submit_button.click()
            else:
                break

        for group_link in link_group:
            if self.stopped:
                driver.quit()
                self.finished.emit()
                return

            try:
                driver.get(group_link)
                try:
                    post_photo = driver.find_element(By.NAME, 'view_photo')
                    post_photo.click()
                    photo_1 = driver.find_element(By.NAME, 'file1')
                    photo_1.send_keys(duong_dan_anh)
                    post_button = driver.find_element(
                        By.NAME, 'add_photo_done')
                    post_button.click()
                    post_input = driver.find_element(By.NAME, 'xc_message')
                    post_input.send_keys(noi_dung)
                    post_status_button = driver.find_element(
                        By.NAME, 'view_post')
                    post_status_button.click()
                    with open(tai_khoan + '_log.txt', 'a') as f:
                        f.write(
                            tai_khoan + ': Post nội dung thành công vào group: ' + group_link + '\n')
                except:
                    pass
            except:
                pass

        driver.quit()
        self.finished.emit()


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadConfig()

    def initUI(self):
        self.setWindowTitle('Facebook Posting Plus')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.label_account = QLabel('Tài khoản:')
        self.input_account = QLineEdit()
        layout.addWidget(self.label_account)
        layout.addWidget(self.input_account)

        self.label_password = QLabel('Mật khẩu:')
        self.input_password = QLineEdit()
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)

        self.label_2fa = QLabel('Mã xác minh hai bước:')
        self.input_2fa = QLineEdit()
        layout.addWidget(self.label_2fa)
        layout.addWidget(self.input_2fa)

        self.label_link_group = QLabel('Link Group:')
        self.input_link_group = QTextEdit()
        layout.addWidget(self.label_link_group)
        layout.addWidget(self.input_link_group)

        self.label_content = QLabel('Nội dung:')
        self.input_content = QTextEdit()
        layout.addWidget(self.label_content)
        layout.addWidget(self.input_content)

        self.label_image = QLabel('Chọn hình ảnh:')
        self.button_image = QPushButton('Chọn')
        self.button_image.clicked.connect(self.chooseImage)
        layout.addWidget(self.label_image)
        layout.addWidget(self.button_image)

        self.button_save_config = QPushButton('Lưu cấu hình')
        self.button_save_config.clicked.connect(self.saveConfig)
        layout.addWidget(self.button_save_config)

        self.button_run = QPushButton('Chạy')
        self.button_run.clicked.connect(self.startExecution)
        layout.addWidget(self.button_run)

        self.button_stop = QPushButton('Dừng')
        self.button_stop.clicked.connect(self.stopExecution)
        layout.addWidget(self.button_stop)

        self.setLayout(layout)

        self.setStyleSheet('''
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
                border-radius: 10px;
            }
            QLabel {
                color: #f8f8f2;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #44475a;
                color: #f8f8f2;
                border: 1px solid #6272a4;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #6272a4;
                color: #f8f8f2;
                padding: 5px 10px;
                border: none;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #778899;
            }
        ''')

    def chooseImage(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Chọn hình ảnh', '.', 'Image files (*.jpg *.png)')
        if filename:
            print("Đã chọn hình ảnh:", filename)
            self.image_path = filename
            _, file_name = os.path.split(filename)
            self.button_image.setText(file_name)

    def saveConfig(self):
        tai_khoan = self.input_account.text().replace(" ", "")
        mat_khau = self.input_password.text().replace(" ", "")
        ma_xac_minh = self.input_2fa.text().replace(" ", "")
        link_group = self.input_link_group.toPlainText().replace(
            " ", "").replace("www.", "mbasic.")
        noi_dung = self.input_content.toPlainText()
        duong_dan_anh = self.image_path if hasattr(self, 'image_path') else ""
        config = {
            "tai_khoan": tai_khoan,
            "mat_khau": mat_khau,
            "ma_xac_minh": ma_xac_minh,
            "link_group": link_group,
            "noi_dung": noi_dung,
            "duong_dan_anh": duong_dan_anh
        }
        formatted_config = json.dumps(
            config, indent=4)
        with open('config.json', 'w') as f:
            f.write(formatted_config)

        self.showSuccessPopup()

    def showSuccessPopup(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Cấu hình đã được lưu thành công!")
        msg.setWindowTitle("Thành công")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def loadConfig(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.input_account.setText(config.get('tai_khoan', ''))
                self.input_password.setText(config.get('mat_khau', ''))
                self.input_2fa.setText(config.get('ma_xac_minh', ''))
                self.input_link_group.setPlainText(
                    config.get('link_group', ''))
                self.input_content.setPlainText(config.get('noi_dung', ''))
                self.image_path = config.get('duong_dan_anh', '')
                if self.image_path:
                    _, file_name = os.path.split(self.image_path)
                    self.button_image.setText(file_name)

    def startExecution(self):
        config = {
            "tai_khoan": self.input_account.text().replace(" ", ""),
            "mat_khau": self.input_password.text().replace(" ", ""),
            "ma_xac_minh": self.input_2fa.text().replace(" ", ""),
            "link_group": self.input_link_group.toPlainText().replace(
                " ", "").replace("www.", "mbasic."),
            "noi_dung": self.input_content.toPlainText(),
            "duong_dan_anh": self.image_path if hasattr(self, 'image_path') else ""
        }
        self.worker = Worker(config)
        self.worker.finished.connect(self.executionFinished)
        self.worker.start()

    def executionFinished(self):
        QMessageBox.information(
            self, "Thành công", "Hoàn tất :>>", QMessageBox.Ok)

    def stopExecution(self):
        QMessageBox.information(self, "Adu",
                                "Đợi chạy nốt nhé, hihi :>>", QMessageBox.Ok)
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stopped = True
        os.system('taskkill /im chromedriver.exe /f')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    icon_location = sys._MEIPASS + "/icon.png"
    app_icon = QtGui.QIcon(icon_location)
    ui.show()
    sys.exit(app.exec_())
