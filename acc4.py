import json
import os
import sys

from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
                             QWidget)


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
        self.button_run.clicked.connect(self.run)
        layout.addWidget(self.button_run)

        self.setLayout(layout)

        self.setStyleSheet('''
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
                border-radius: 10px; /* Bo góc cho cửa sổ */
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
                border-radius: 5px; /* Bo góc cho ô nhập liệu */
            }
            QPushButton {
                background-color: #6272a4;
                color: #f8f8f2;
                padding: 5px 10px;
                border: none;
                font-weight: bold;
                border-radius: 5px; /* Bo góc cho nút */
            }
            QPushButton:hover {
                background-color: #778899; /* Đổi màu khi hover */
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
        link_group = self.input_link_group.toPlainText().replace(" ", "")
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
        with open('config4.json', 'w') as f:
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
        if os.path.exists('config4.json'):
            with open('config4.json', 'r') as f:
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

    def run(self):
        os.system("python run.py")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
