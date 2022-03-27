import argparse
import json
from datetime import datetime

from db_controller.db_controller import DBcontroller
from checkXMR import XMR

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--timeout", required=False, default=30,
                help="Request timeout")
ap.add_argument("-f", "--figure", required=False,
                help="Figure Title")
args = vars(ap.parse_args())

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)
    db_name = config['db']
    table_name = config['table']
    db = DBcontroller(db_name=db_name)
    db.init_db(create_table_sql=f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
                                            id integer PRIMARY KEY,
                                            duepay text NOT NULL,
                                            log_datetime text NOT NULL
                                        ); 
    ''')

    bot = XMR(XMR.get_xmr_add())
    bot.token = XMR.get_tele_token()
    stats = bot.check_moneroOcean_stats()
    due_payment = float(XMR.get_stats_item(stats, item='amtDue')) / 1000000000000

    db.insert_into_table(insert_sql=f"INSERT INTO {table_name} (duepay,log_datetime) VALUES(?,?)"
                         , data=[due_payment, datetime.now()])

    rows = db.select_from_table(select_sql=f"SELECT * FROM {table_name}")
    print(rows)
