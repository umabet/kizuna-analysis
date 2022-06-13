import sqlite3
import subprocess

import matplotlib.pyplot as plt
import numpy as np
import os
import json

log_folder = folder = os.path.join(os.getenv('UserProfile'), 'Umamusume', 'KizunaData', 'log')
master_file = os.path.join(os.getenv("UserProfile"), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
plt.rcParams['font.family'] = "MS Gothic"

conn = sqlite3.connect(master_file)
cur = conn.cursor()


class Status:

    def __init__(self):
        self.speed = self.stamina = self.power = self.guts = self.wiz = self.skill_point = self.vital = 0

    def sum(self):
        return self.speed + self.stamina + self.power + self.guts + self.wiz


class StatusUpLog:

    def __init__(self, logs):
        self.statuses = list()
        for log in logs:
            status = Status()
            if 'speed' in log and isinstance(log['speed'], int):
                status.speed = log['speed']
            if 'stamina' in log and isinstance(log['stamina'], int):
                status.stamina = log['stamina']
            if 'power' in log and isinstance(log['power'], int):
                status.power = log['power']
            if 'guts' in log and isinstance(log['guts'], int):
                status.guts = log['guts']
            if 'wiz' in log and isinstance(log['wiz'], int):
                status.wiz = log['wiz']
            if 'skill_point' in log and isinstance(log['skill_point'], int):
                status.skill_point = log['skill_point']
            if 'vital' in log and isinstance(log['vital'], int):
                status.vital = log['vital']
            self.statuses.append(status)

    def sum(self):
        return sum([x.sum() for x in self.statuses])


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

    base_id = 500000000 + int(json_log['chara_info']['card_id'] / 100) * 1000
    race_story_id = [400000035, 400000036, 400004013, 400004051, 400004061, 400004071, base_id + 600, base_id + 601, base_id + 708, base_id + 709, base_id + 710, base_id + 711]  # レース関連のstory id　オアハルシナリオがないなど完璧ではない
    succession_story_id = [400000040]  # 継承イベントのstory id
    nickname_story_id = [400004014, 400004015, 400004016]  # 称号取得イベントのstory id

    # 条件を満たすlogを抽出
    initial = StatusUpLog(json_log['log'][0: 1])  # 1つ目が初期値
    training = StatusUpLog([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [101, 102, 103, 105, 106]])  # 100番台のcommand_idは通常トレーニング
    training_summer = StatusUpLog([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [601, 602, 603, 604, 605]])  # 100番台のcommand_idは夏合宿トレーニング
    event = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and not x['story_id'] in race_story_id + succession_story_id + nickname_story_id + [0]])  # 称号取得や継承、二つ名イベント以外のすべてのイベント
    race = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and x['story_id'] in race_story_id])
    succession = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and x['story_id'] in succession_story_id])
    nickname = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and x['story_id'] in nickname_story_id])
    goods = StatusUpLog([x for x in json_log['log'] if 'use_num' in x or 'use_item_info_array' in x])  # アイテムを使用した時

    print('トレーニング回数（通常）:{}'.format(len(training.statuses)))
    print('トレーニング回数（合宿）:{}'.format(len(training_summer.statuses)))
    print('レース:{}戦{}勝'.format(len(json_log['chara_info']['race_result_list']), len([x for x in json_log['chara_info']['race_result_list'] if x['result_rank'] == 1])))
    print('お休み回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] == 701])))
    print('スピード練習回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [101, 601]])))
    print('スタミナ練習回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [105, 602]])))
    print('パワー練習回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [102, 603]])))
    print('根性練習回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [103, 604]])))
    print('賢さ練習回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] in [106, 605]])))
    # TODO:お出かけと夏合宿のcommand_idを調べる

    labels = '初期値', 'トレーニング', 'トレーニング(夏合宿)', 'イベント', 'レース', '継承', '称号', 'アイテム'
    data = [initial.sum(), training.sum(), training_summer.sum(), event.sum(), race.sum(), succession.sum(), nickname.sum(), goods.sum()]  # 条件ごとのステータス上昇値を計算してグラフ用のデータを作成

    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels=labels, autopct=lambda p: round(np.sum(data) * p / 100), startangle=90, counterclock=False)

    image_folder = os.path.join(log_folder, 'image')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # plt.show()

    output_filename = os.path.join(image_folder, single_mode_chara_id.zfill(6) + '.png')
    plt.savefig(output_filename)
    subprocess.Popen(['start', output_filename], shell=True)


def print_list():
    try:
        fp = open(os.path.join(log_folder, 'index.json'), 'r')
    except FileNotFoundError:
        print('ログがありません')
        return
    index_json = json.load(fp)
    sorted_id = sorted(sorted(index_json, reverse=True)[0: 200])

    print('{:6} | {:5} | {:19} | {}'.format('id', 'score', 'create_time', 'chara_name'))
    for i in sorted_id:
        cur.execute('SELECT text FROM text_data WHERE category = 4 and `index` = {}'.format(index_json[i]['card_id']))
        name = cur.fetchone()[0]
        print('{} | {:5} | {} | {}'.format(i, index_json[i]['rank_score'], index_json[i]['create_time'], name))


print_list()
while True:
    chara_id = input('解析したいidを入力してください:')
    if chara_id.isalpha():
        print('プログラムを終了します')
        break
    main(chara_id)

cur.close()
conn.close()
