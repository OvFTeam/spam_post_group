import json
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def read_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        tai_khoan = config['tai_khoan']
        mat_khau = config['mat_khau']
        ma_xac_minh = config['ma_xac_minh']
        link_group = config['link_group'].split('\n')
        noi_dung = config['noi_dung']
        duong_dan_anh = config['duong_dan_anh']
        return tai_khoan, mat_khau, ma_xac_minh, link_group, noi_dung, duong_dan_anh


def post_status():
    driver = webdriver.Chrome()
    tai_khoan, mat_khau, ma_xac_minh, link_group, noi_dung, duong_dan_anh = read_config()

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
        return 0
    except:
        pass
    response = requests.get(f"https://2fa.live/tok/{ma_xac_minh}")
    data = response.json()
    token = data["token"]
    try:
        code_input = driver.find_element(By.ID, 'approvals_code')
        code_input.send_keys(token)
        submit_button = driver.find_element(By.ID, 'checkpointSubmitButton')
        submit_button.click()
    except:
        pass
    for i in range(8):
        if i == 7:
            with open(tai_khoan + '.txt', 'a') as f:
                f.write(tai_khoan + ': Nick ngỏm mẹ r :v' + '\n')
            return 0
        current_url = driver.current_url

        if "checkpoint" in current_url:
            submit_button = driver.find_element(
                By.ID, 'checkpointSubmitButton')
            submit_button.click()
        else:
            break
    for group_link in link_group:
        try:
            driver.get(group_link)
            try:
                post_photo = driver.find_element(By.NAME, 'view_photo')
                post_photo.click()
                photo_1 = driver.find_element(By.NAME, 'file1')
                photo_1.send_keys(duong_dan_anh)
                post_button = driver.find_element(By.NAME, 'add_photo_done')
                post_button.click()
                post_input = driver.find_element(By.NAME, 'xc_message')
                post_input.send_keys(noi_dung)
                post_status_button = driver.find_element(By.NAME, 'view_post')
                post_status_button.click()
                with open(tai_khoan + '_log.txt', 'a') as f:
                    f.write(tai_khoan +': Post nội dung thành công vào group: ' + group_link + '\n')
            except:
                pass
            time.sleep(10000)
        except:
            pass
    time.sleep(100)
post_status()
