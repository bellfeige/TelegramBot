import json
import os

import requests


class TeleBot:
    def __init__(self, token):
        self.token = token

    @staticmethod
    def check_config_file(file='config.json', path='.'):
        if not os.path.isfile(f'{path}/{file}'):
            raise Exception(f"No {file} found")

    @staticmethod
    def get_tele_token(file='config.json', path='.'):
        TeleBot.check_config_file(file=file, path=path)
        with open(f"{path}/{file}") as f:
            config = json.load(f)
        token = config["telegram_token"]
        return token

    def send_msg_to(self, msg, token=None):
        if token is None:
            token = self.token
        params = {'chat_id': '808633678', 'text': msg}
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        res = requests.get(url=url, params=params)
        return res.json()

    def send_img_to(self, img, token=None):
        files = {'photo': open(img, 'rb')}
        if token is None:
            token = self.token
        params = {'chat_id': '808633678'}
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        res = requests.post(url=url, params=params, files=files)
        return res.json()
