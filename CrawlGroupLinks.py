import json
import os
import re
import sys
import time

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QVBoxLayout, QWidget)
from selenium import webdriver
from selenium.webdriver.common.by import By


class CrawlThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, username, password, twofacode, keyword):
        super().__init__()
        self.username = username
        self.password = password
        self.twofacode = twofacode
        self.keyword = keyword

    def run(self):
        link_group = self.crawl_group(
            self.username, self.password, self.twofacode, self.keyword.strip())

        self.finished.emit(link_group)

    def crawl_group(self, username, password, twofacode, keyword):
        driver = webdriver.Chrome()
        driver.get('https://mbasic.facebook.com')

        username_input = driver.find_element(By.ID, 'm_login_email')
        username_input.send_keys(username)

        password_input = driver.find_element(By.NAME, 'pass')
        password_input.send_keys(password)

        login_button = driver.find_element(By.NAME, 'login')
        login_button.click()

        response = requests.get(f"https://2fa.live/tok/{twofacode}")
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
            if i == 7:
                return []

            current_url = driver.current_url
            if "checkpoint" in current_url:
                submit_button = driver.find_element(
                    By.ID, 'checkpointSubmitButton')
                submit_button.click()
            else:
                break

        driver.get(f"https://mbasic.facebook.com/search/groups/?q={keyword}")
        try:
            see_more_button = driver.find_element(
                By.XPATH, '//*[@id="see_more_pager"]/a/span')
            see_more_button.click()
            time.sleep(3)
            see_more_button.click()
        except:
            pass

        group_links = driver.find_elements(
            By.XPATH, "//a[contains(@href, '/groups/')]")

        link_group = []
        for link in group_links:
            url = link.get_attribute("href")
            group_id = extract_group_id(url)
            if group_id:
                url = f"https://mbasic.facebook.com/groups/{group_id}"
                link_group.append(url)

        driver.quit()
        return link_group


class CrawlThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, username, password, twofacode, keyword):
        super().__init__()
        self.username = username
        self.password = password
        self.twofacode = twofacode
        self.keyword = keyword

    def run(self):
        link_group = self.crawl_group(
            self.username, self.password, self.twofacode, self.keyword.strip())

        self.finished.emit(link_group)

    def crawl_group(self, username, password, twofacode, keyword):
        driver = webdriver.Chrome()
        driver.get('https://mbasic.facebook.com')

        username_input = driver.find_element(By.ID, 'm_login_email')
        username_input.send_keys(username)

        password_input = driver.find_element(By.NAME, 'pass')
        password_input.send_keys(password)

        login_button = driver.find_element(By.NAME, 'login')
        login_button.click()

        response = requests.get(f"https://2fa.live/tok/{twofacode}")
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
            if i == 7:
                return []

            current_url = driver.current_url
            if "checkpoint" in current_url:
                submit_button = driver.find_element(
                    By.ID, 'checkpointSubmitButton')
                submit_button.click()
            else:
                break

        driver.get(f"https://mbasic.facebook.com/search/groups/?q={keyword}")
        try:
            see_more_button = driver.find_element(
                By.XPATH, '//*[@id="see_more_pager"]/a/span')
            see_more_button.click()
        except:
            pass

        group_links = driver.find_elements(
            By.XPATH, "//a[contains(@href, '/groups/')]")

        link_group = []
        for link in group_links:
            url = link.get_attribute("href")
            group_id = extract_group_id(url)
            if group_id:
                url = f"https://mbasic.facebook.com/groups/{group_id}"
                link_group.append(url)

        driver.quit()
        return link_group


def extract_group_id(url):
    pattern = r'\/groups\/(\d+)\/?'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


class FacebookGroupCrawler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facebook Group Link Crawler")
        self.setGeometry(100, 100, 400, 400)
        self.init_ui()
        self.read_config()

    def init_ui(self):
        layout = QVBoxLayout()

        self.keyword_label = QLabel("Từ Khóa:")
        self.keyword_input = QLineEdit()
        layout.addWidget(self.keyword_label)
        layout.addWidget(self.keyword_input)

        self.username_label = QLabel("Tài Khoản:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Mật Khẩu:")
        self.password_input = QLineEdit()
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.twofa_label = QLabel("Mã Xác Minh:")
        self.twofa_input = QLineEdit()
        layout.addWidget(self.twofa_label)
        layout.addWidget(self.twofa_input)

        self.log_label = QLabel("Log:")
        layout.addWidget(self.log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.submit_button = QPushButton("Bắt Đầu Crawl")
        self.submit_button.clicked.connect(self.start_crawling)
        layout.addWidget(self.submit_button)

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

    def read_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                config_data = json.load(config_file)
                self.username_input.setText(config_data.get("tai_khoan", ""))
                self.password_input.setText(config_data.get("mat_khau", ""))
                self.twofa_input.setText(config_data.get("ma_xac_minh", ""))

    def start_crawling(self):
        keyword = self.keyword_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        twofacode = self.twofa_input.text()

        self.submit_button.setEnabled(False)
        self.log_output.clear()
        self.log_output.append("Bắt đầu crawl...")

        self.crawl_thread = CrawlThread(username, password, twofacode, keyword)
        self.crawl_thread.finished.connect(self.crawl_finished)
        self.crawl_thread.start()

    def crawl_finished(self, link_group):
        link_group_string = '\n'.join(link_group)
        with open("linkgroup.txt", "a") as file:
            for link in link_group:
                file.write(link + "\n")

        config_data = {
            "tai_khoan": self.username_input.text(),
            "mat_khau": self.password_input.text(),
            "ma_xac_minh": self.twofa_input.text(),
            "link_group": link_group_string,
            "noi_dung": "",
            "duong_dan_anh": ""
        }

        with open("config.json", "w") as config_file:
            json.dump(config_data, config_file, indent=4)

        self.log_output.append("Crawl hoàn thành!")
        self.submit_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FacebookGroupCrawler()
    window.show()
    sys.exit(app.exec_())


def extract_group_id(url):
    pattern = r'\/groups\/(\d+)\/?'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


class FacebookGroupCrawler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facebook Group Link Crawler")
        self.setGeometry(100, 100, 400, 400)
        self.init_ui()
        self.read_config()

    def init_ui(self):
        layout = QVBoxLayout()

        self.keyword_label = QLabel("Từ Khóa:")
        self.keyword_input = QLineEdit()
        layout.addWidget(self.keyword_label)
        layout.addWidget(self.keyword_input)

        self.username_label = QLabel("Tài Khoản:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Mật Khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.twofa_label = QLabel("Mã Xác Minh:")
        self.twofa_input = QLineEdit()
        layout.addWidget(self.twofa_label)
        layout.addWidget(self.twofa_input)

        self.log_label = QLabel("Log:")
        layout.addWidget(self.log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.submit_button = QPushButton("Bắt Đầu Crawl")
        self.submit_button.clicked.connect(self.start_crawling)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def read_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                config_data = json.load(config_file)
                self.username_input.setText(config_data.get("tai_khoan", ""))
                self.password_input.setText(config_data.get("mat_khau", ""))
                self.twofa_input.setText(config_data.get("ma_xac_minh", ""))

    def start_crawling(self):
        keyword = self.keyword_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        twofacode = self.twofa_input.text()

        self.submit_button.setEnabled(False)
        self.log_output.clear()
        self.log_output.append("Bắt đầu crawl...")

        self.crawl_thread = CrawlThread(username, password, twofacode, keyword)
        self.crawl_thread.finished.connect(self.crawl_finished)
        self.crawl_thread.start()

    def crawl_finished(self, link_group):
        config_data = {
            "tai_khoan": self.username_input.text(),
            "mat_khau": self.password_input.text(),
            "ma_xac_minh": self.twofa_input.text(),
            "link_group": link_group,
            "noi_dung": "Hello AE"
        }

        with open("config.json", "w") as config_file:
            json.dump(config_data, config_file, indent=4)

        self.log_output.append("Crawl hoàn thành!")
        self.submit_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FacebookGroupCrawler()
    app_icon = "icon.png"
    app_icon = QIcon(app_icon)
    app.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec_())
