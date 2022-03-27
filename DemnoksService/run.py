import argparse
import json
from datetime import datetime

from db_controller.db_controller import DBController
from checkXMR import XMR
from chart_controller.chart_controller import ChartController

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--figure", required=False,
                help="Figure Title")
ap.add_argument("-a", "--action", required=False,
                help="show or save")
args = vars(ap.parse_args())

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)
    db_name = config['db']
    table_name = config['table']
    db = DBController(db_name=db_name)
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
    due_payment = XMR.formated_duepay(XMR.get_stats_item(stats, item='amtDue'))

    db.insert_into_table(insert_sql=f"INSERT INTO {table_name} (duepay,log_datetime) VALUES(?,?)"
                         , data=[due_payment, datetime.now()])

    rows = db.select_from_table(select_sql=f"SELECT * FROM {table_name}")
    rows = DBController.rows_sorted(rows)
    print(rows)

    x_dt = sorted([r[2][:16] for r in rows][:8], reverse=False)
    y_dt = sorted([float(r[1][:]) for r in rows][:8], reverse=False)
    print(x_dt)
    print(y_dt)

    figure_title = ''
    if args["figure"]:
        figure_title = args["figure"]
    else:
        figure_title = "!!!DEBUG!!! Monero Ocean Mining Due payment !!!DEBUG!!!"
    ChartController.init_chart(size_x=16, size_y=6, title=figure_title, label_x="Date Time", label_y="Due payment")
    ChartController.fill_chart(x_dt, y_dt)
    # plt.legend(loc="upper left", framealpha=0)
    save_path = 'xmrChart'
    img_name = 'latest'

    if args["action"]:
        ChartController.chart_result(action=args["action"], save_path=save_path, img_name=img_name)

        bot.send_img_to(img=f"{save_path}\\{img_name}.png")
    else:
        ChartController.chart_result(action='show', save_path=save_path, img_name=img_name)
