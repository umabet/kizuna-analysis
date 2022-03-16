import json
import os
import sqlite3
import subprocess

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

log_folder = folder = os.path.join(os.getenv('UserProfile'), 'Umamusume', 'KizunaData', 'log')
master_file = os.path.join(os.getenv("UserProfile"), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
plt.rcParams['font.family'] = "MS Gothic"

conn = sqlite3.connect(master_file)
cur = conn.cursor()


class SupportCard:
    def __init__(self, support_card_id):
        self.id = support_card_id
        cur.execute('SELECT text FROM text_data WHERE category = 75 and `index` = {}'.format(self.id))
        self.name = cur.fetchone()[0]
        self.counter = [0, 0, 0, 0, 0]  # 左からスピード、スタミナ、パワー、根性、賢さの練習に現れた数をカウント

    def print(self):
        total = sum(self.counter)
        print('{} 合計{}回 {}'.format(self.counter, total, self.name))


def main(single_mode_chara_id):
    try:
        fp = open(os.path.join(log_folder, single_mode_chara_id.zfill(6) + '.json'), 'r')
    except FileNotFoundError:
        print('該当するデータはありません')
        return
    json_log = json.load(fp)
    fp.close()

    if 'chara_info' not in json_log:
        print('このデータは育成が終わっていません')
        return

    support_card_list = [SupportCard(x['support_card_id']) for x in json_log['chara_info']['support_card_list']]

    for command_info in json_log['command_info']:
        for i in range(5):
            for partner_id in command_info[i]['training_partner_array']:
                if partner_id <= 6:  # 理事長などサポートカード以外は対象外
                    support_card_list[partner_id - 1].counter[i] += 1

    [x.print() for x in support_card_list]

    fig, ax = plt.subplots()
    x = np.arange(5)
    width = 0.15

    for i in range(6):
        rects = ax.bar(x + width * (i - 2.5), support_card_list[i].counter, width, label=support_card_list[i].name)
        ax.bar_label(rects)
    ax.set_xticks(x, ['スピード', 'スタミナ', 'パワー', '根性', '賢さ'])
    ax.legend(bbox_to_anchor=(0, -0.1), loc='upper left')
    fig.tight_layout()
    ax.yaxis.set_major_locator(MultipleLocator(5))

    image_folder = os.path.join(log_folder, 'image')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # plt.show()

    output_filename = os.path.join(image_folder, '得意率' + single_mode_chara_id.zfill(6) + '.png')
    plt.savefig(output_filename)
    subprocess.Popen(['start', output_filename], shell=True)


def print_list():
    try:
        fp = open(os.path.join(log_folder, 'index.json'), 'r')
    except FileNotFoundError:
        print('ログがありません')
        return
    index_json = json.load(fp)
    sorted_id = sorted(sorted(index_json, reverse=True)[0: 10])

    print('{:6} | {:5} | {:19} | {}'.format('id', 'score', 'create_time', 'chara_name'))
    for i in sorted_id:
        cur.execute('SELECT text FROM text_data WHERE category = 4 and `index` = {}'.format(index_json[i]['card_id']))
        name = cur.fetchone()[0]
        print('{} | {:5} | {} | {}'.format(i, index_json[i]['rank_score'], index_json[i]['create_time'], name))


print_list()
while True:
    chara_id = input('解析したいidを入力してください:')
    if not chara_id.isdigit():
        break
    main(chara_id)

cur.close()
conn.close()
