import json
import sqlite3
import os
from datetime import date, datetime
from pprint import pprint
import random
import string
from itertools import groupby
from operator import itemgetter

import numpy
import numpy as np
import requests
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt
import argparse

from notification import send_msg_to, send_img_to

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--timeout", required=False, default=30,
                help="Request timeout")
ap.add_argument("-f", "--figure", required=False,
                help="Figure Title")
args = vars(ap.parse_args())


def index_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def check_moneroOcean(add):
    url = f"https://api.moneroocean.stream/miner/{add}/stats"
    r = requests.get(url=url)
    data = r.json()
    return data


def check_moneroOcean_worker(worker='', add='', timeout=20):
    url = f"https://api.moneroocean.stream/miner/{add}/stats/{worker}"
    try:
        print(f"requesting for {worker}")
        r = requests.get(url=url, timeout=(float(timeout), 5))
        print(f"returnned from {worker}")
        data = r.json()
        # print(data)
        return data
    except Exception as e:
        print(e)
        return None


def check_supportXMR(add):
    url = f"https://supportxmr.com/api/miner/{add}/stats"
    r = requests.get(url=url)
    data = r.json()
    return data


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)


def init(db):
    sql_create_xmr_table = '''
    CREATE TABLE IF NOT EXISTS moneroocean (
                                        id integer PRIMARY KEY,
                                        dt text NOT NULL,
                                        worker_name text NOT NULL,
                                        worker_hash2 text NOT NULL,
                                        verify text NOT NULL
                                    ); 
    '''

    conn = create_connection(db)

    if conn is not None:
        with conn:
            create_table(conn, sql_create_xmr_table)
    else:
        print("Error! cannot create the database connection.")


def insert_into_table(conn, table, data):
    sql = f''' INSERT INTO {table}(dt,worker_name,worker_hash2,verify)
                  VALUES(?,?,?,?) '''
    if conn is not None:
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            conn.commit()
    else:
        print("Error! cannot create the database connection.")


def select_from_table(conn, table):
    sql = f'''SELECT * FROM {table}'''

    if conn is not None:
        with conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            # for row in rows:
            #     print(dict(row))
            return rows
    else:
        print("Error! cannot create the database connection.")
        return None


def checkKey(the_dict, key):
    if key in the_dict.keys():
        return True
    else:
        return False


def def_data_range(rows):
    lines_qty = 0
    verify_list = []
    for r in reversed(rows):
        # print(r)
        if len(verify_list) == 8:
            break
        lines_qty += 1
        verify_list.append(r[4])
        verify_list = list(dict.fromkeys(verify_list))
    data = rows[-lines_qty:]
    return data, lines_qty


def check_config_file(file='config.json', path='.'):
    if not os.path.isfile(f'{path}/{file}'):
        raise Exception(f"No {file} found")


def build_matrix(rows, cols, init_value='0.0'):
    matrix = []

    for r in range(0, rows):
        matrix.append([init_value for c in range(0, cols)])

    return matrix


def def_pattern(rows_groupby):
    pattern = []
    tms = 1
    for rg in rows_groupby:
        if len(rg[1].split(',')) >= 1 and rg[1].split(',')[0] != '0':
            for w in rg[1].split(','):
                if w not in pattern:
                    pattern.append(w)
        if len(rg[1].split(',')) == 1 and rg[1].split(',')[0] == '0' and tms < 1:
            tms -= 1
            pattern.append('0')
            return pattern

def sort_workers_pattern(workers, wp):
    ws_index = []
    for w in wp:
        if w == '0':
            continue
        ws_index.append(workers[w][1])
    import copy
    temp_wp = copy.deepcopy(wp)
    if '0' in temp_wp:
        temp_wp.remove('0')
    zipped_ws = sorted(zip(ws_index, temp_wp))
    temp_wp = [e for _, e in zipped_ws]
    if '0' in wp:
        temp_wp.append('0')
    return temp_wp

if __name__ == '__main__':

    check_config_file()
    with open('config.json') as f:
        config = json.load(f)
    add = config["add"]
    db = config["db"]
    workers = config["workers"]
    workers_list = [k for k, v in workers.items()]
    bar_color = [v[0] for k, v in workers.items()]
    table = config["table"]

    init(db=db)

    current_data = []

    for w in workers_list:
        rest = check_moneroOcean_worker(worker=w, add=add, timeout=args["timeout"])
        if rest is None:
            print(f'skip {w}, due to timeout')
            continue
        if rest['lts'] is None or rest['lts'] == 'null':
            print(f'skip {w}, due to no such worker')
            continue
        current_data.append(rest)

    ws_dict = {}
    for c in current_data:
        ws_dict[c['identifer']] = round(float(c['hash2']), 1)

    # pprint(current_data)

    if not ws_dict:
        print(f'Not ws to be inserted')
    else:
        pprint(ws_dict)

    workerName_to_insert = []
    workerHash2_to_insert = []
    for k, v in ws_dict.items():
        # data_to_insert.append(f'{k}:{v}')
        workerName_to_insert.append(f'{k}')
        workerHash2_to_insert.append(f'{v}')

        # print(f'{k}:{v}')
    # print(data_to_insert)

    # dt, da = [], []
    rows = None
    conn = create_connection(db_file=db)
    with conn:
        # table = 'moneroocean'
        t = datetime.now().strftime("%m/%d, %H:%M")
        i = f'{index_generator()}'
        if not ws_dict:
            insert_into_table(conn, table, [t, '0', '0', i])
        else:
            for n, h in zip(workerName_to_insert, workerHash2_to_insert):
                insert_into_table(conn, table, [t, n, h, i])
        rows = select_from_table(conn, table)
        # pprint(rows)

    rows, line_qty = def_data_range(rows)
    pprint(rows)
    print(line_qty)

    # time_line
    x_dt = sorted(list(dict.fromkeys([x[1] for x in rows])))
    print(x_dt)

    workers_pattern = sorted(list(dict.fromkeys([x[2] for x in rows])), reverse=True)
    # workers_pattern = [x for _, x in sorted(zip(workers_pattern, workers_list))]
    workers_pattern=sort_workers_pattern(workers,workers_pattern)
    print(workers_pattern)

    hashs_table = build_matrix(8, len(workers_pattern))

    pre_verify = None
    hashs_table_h = 0
    for r in rows:
        verify = r[4]
        hashs_table_v = workers_pattern.index(r[2])
        if verify != pre_verify and pre_verify is not None:
            hashs_table_h += 1
        pre_verify = verify
        hashs_table[hashs_table_h][hashs_table_v] = r[3]
        # print(f'({hashs_table_h}, {hashs_table_v})')
    hashs_table = [[float(y) for y in x] for x in hashs_table]
    hashs_table = np.array(hashs_table)
    pprint(hashs_table)
    hashs_table = np.transpose(hashs_table)
    pprint(hashs_table)

    fig, ax = plt.subplots()

    legend_one_time = 0
    ind = [x for x, _ in enumerate(x_dt)]
    for hs, i in zip(hashs_table, ind):
        # if i == 1:
        #     plt.legend(loc="upper left")

        print(hs)
        # print(i)

        pre_h = 0
        bottom = 0
        round = 0
        # e= [x for x, _ in enumerate(hs)]
        for e, h in enumerate(hs):
            # print(h)
            if i == 0 and e == 0:
                plt.legend(loc="upper left")

            if h <= 0.0:
                round += 1
                continue
            if bottom != 0:
                bottom = h + pre_h
            # if pre_h != 0.0:
            pre_h = h
            round += 1
            p = ax.bar(e, height=h, width=0.4, label=workers_pattern[i], color=bar_color[i], bottom=bottom),
            if legend_one_time == i:
                plt.legend(loc="upper left")
            legend_one_time += 1
            # plt.bar_label(p[0], label_type='center')
            plt.bar_label(p[0])
            # if round == len(workers_pattern):
            #     plt.bar_label(p[0])


        # if legend_one_time == i:
        #     plt.legend(loc="upper left")
        # legend_one_time += 1

    plt.gcf().set_size_inches(16, 6)
    plt.xticks(ind, x_dt)
    plt.ylabel("Worker hash2")
    plt.xlabel("Date Time")
    # plt.legend(loc="upper left", framealpha=0)
    if args["figure"]:
        plt.title(args["figure"])
    else:
        plt.title("!!!DEBUG!!! Monero Ocean Mining  !!!DEBUG!!!")
    # plt.grid()

    if not os.path.exists('xmrChart'):
        os.makedirs('xmrChart')
    plt.savefig(f"xmrChart\\latest", bbox_inches='tight')
    # plt.show()
    plt.clf()
    r = send_img_to(f"xmrChart\\latest.png")
