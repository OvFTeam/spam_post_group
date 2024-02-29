import json
import os
import sys

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
                             QWidget)
from selenium import webdriver
from selenium.webdriver.common.by import By


class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, config, thread_id):
        super().__init__()
        self.config = config
        self.stopped = False
        self.thread_id = thread_id

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
                    if self.check_posted_post(group_link):
                        continue


                    post_photo = driver.find_element(By.NAME, 'view_photo')
                    post_photo.click()
                    for img_path in duong_dan_anh:
                        photo_1 = driver.find_element(By.NAME, 'file1')
                        photo_1.send_keys(img_path)
                        photo_1_posted = True
                        if photo_1_posted:
                            photo_2 = driver.find_element(By.NAME, 'file2')
                            photo_2.send_keys(img_path)
                            photo_2_posted = True
                        elif photo_2_posted:
                            photo_3 = driver.find_element(By.NAME, 'file3')
                            photo_3.send_keys(img_path)
                            photo_3_posted = True
                        elif photo_3_posted:
                            break
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

                    self.save_posted_post(group_link)
                except:
                    pass
            except:
                pass

        driver.quit()
        self.finished.emit()

    def check_posted_post(self, group_link):
        posted_posts = self.load_posted_posts()
        return posted_posts.get(group_link, False)

    def load_posted_posts(self):
        posted_posts = {}
        if os.path.exists('posted_posts.json'):
            with open('posted_posts.json', 'r') as f:
                posted_posts = json.load(f)
        return posted_posts

    def save_posted_post(self, group_link):
        posted_posts = self.load_posted_posts()
        posted_posts[group_link] = True
        with open('posted_posts.json', 'w') as f:
            json.dump(posted_posts, f)


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadConfig()
        self.workers = []

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
        self.button_image.clicked.connect(self.chooseImages)
        layout.addWidget(self.label_image)
        layout.addWidget(self.button_image)

        self.label_threads = QLabel('Số luồng:')
        self.input_threads = QLineEdit()
        layout.addWidget(self.label_threads)
        layout.addWidget(self.input_threads)

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
                background-color: #FCEBB6;
            }

            QLabel {
                font-family: "Comic Sans MS";
                font-size: 16px;
                color: #FF9A8B;
            }

            QLineEdit {
                background-color: #FFF6E8;
                font-size: 14px;
                border: 2px solid #FF9A8B;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:hover {
                background-color: #FFD8C2;
            }

            QTextEdit {
                background-color: #FFF6E8;
                font-size: 14px;
                border: 2px solid #FF9A8B;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton {
                background-color: #FF9A8B;
                color: white;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #FFC4BD;
            }
        ''')


    def chooseImages(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self, 'Chọn hình ảnh', '.', 'Image files (*.jpg *.png)')
        if filenames:
            if len(filenames) > 3:
                QMessageBox.warning(self, "Lỗi",
                                    "Chỉ cho phép chọn tối đa 3 ảnh!", QMessageBox.Ok)
                return
            self.image_paths = filenames
            self.button_image.setText(
                "Đã chọn {} hình ảnh".format(len(filenames)))


    def saveConfig(self):
        tai_khoan = self.input_account.text().replace(" ", "")
        mat_khau = self.input_password.text().replace(" ", "")
        ma_xac_minh = self.input_2fa.text().replace(" ", "")
        link_group = self.input_link_group.toPlainText().replace(
            " ", "").replace("www.", "mbasic.")
        noi_dung = self.input_content.toPlainText()
        duong_dan_anh = self.image_paths if hasattr(
            self, 'image_paths') else []
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
                self.image_paths = config.get('duong_dan_anh', [])
                if self.image_paths:
                    self.button_image.setText(
                        "Đã chọn {} hình ảnh".format(len(self.image_paths)))

    def startExecution(self):
        num_threads = int(self.input_threads.text())
        if num_threads <= 0:
            QMessageBox.warning(self, "Lỗi",
                                "Số luồng phải là một số nguyên dương!", QMessageBox.Ok)
            return
        self.workers = []
        for i in range(num_threads):
            config = {
                "tai_khoan": self.input_account.text().replace(" ", ""),
                "mat_khau": self.input_password.text().replace(" ", ""),
                "ma_xac_minh": self.input_2fa.text().replace(" ", ""),
                "link_group": self.input_link_group.toPlainText().replace(
                    " ", "").replace("www.", "mbasic."),
                "noi_dung": self.input_content.toPlainText(),
                "duong_dan_anh": self.image_paths if hasattr(self, 'image_paths') else []
            }
            worker = Worker(config, i)
            worker.finished.connect(self.executionFinished)
            worker.start()
            self.workers.append(worker)

    def executionFinished(self):
        QMessageBox.information(
            self, "Thành công", "Hoàn tất :>>", QMessageBox.Ok)

    def stopExecution(self):
        QMessageBox.information(self, "Adu",
                                "Đợi chạy nốt nhé, hihi :>>", QMessageBox.Ok)
        for worker in self.workers:
            if worker.isRunning():
                worker.stopped = True
        os.system('taskkill /im chromedriver.exe /f')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
