import json

import requests

from tele_bot.tele_bot import TeleBot


class XMR(TeleBot):
    def __init__(self, add):
        self.add = add
        super().__init__(self)

    @staticmethod
    def get_xmr_add(file='config.json', path='.'):
        TeleBot.check_config_file(file=file, path=path)
        with open(f"{path}/{file}") as f:
            config = json.load(f)
        token = config["add"]
        return token

    def check_moneroOcean_stats(self, timeout=20):
        url = f"https://api.moneroocean.stream/miner/{self.add}/stats/"
        try:
            r = requests.get(url=url, timeout=(float(timeout), 5))
            data = r.json()
            # print(data)
            return data
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_stats_item(data, item='amtDue'):
        if data is None:
            raise Exception(f"No stats data found")
        print(f"getting {item} : {data[item]}")
        return data[item]


if __name__ == '__main__':
    bot = XMR(XMR.get_xmr_add())
    bot.token = XMR.get_tele_token()
    stats = bot.check_moneroOcean_stats()
    due_payment = float(XMR.get_stats_item(stats, item='amtDue')) / 1000000000000
    bot.send_msg_to(due_payment)
