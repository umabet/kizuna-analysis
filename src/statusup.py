import re
import matplotlib.pyplot as plt
import numpy as np
import os
import json

log_folder = folder = os.path.join(os.getenv('UserProfile'), 'Umamusume', 'KizunaData', 'log')
plt.rcParams['font.family'] = "MS Gothic"


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
    event = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and not x['story_id'] in race_story_id + succession_story_id + nickname_story_id])  # 称号取得や継承、二つ名イベント以外のすべてのイベント
    race = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and x['story_id'] in race_story_id])
    succession = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and x['story_id'] in succession_story_id])
    nickname = StatusUpLog([x for x in json_log['log'] if 'story_id' in x and x['story_id'] in nickname_story_id])
    goods = StatusUpLog([x for x in json_log['log'] if 'use_num' in x])  # アイテムを使用した時に"use_num": 1になる

    print('トレーニング回数（通常）:{}'.format(len(training.statuses)))
    print('トレーニング回数（合宿）:{}'.format(len(training_summer.statuses)))
    print('レース:{}戦{}勝'.format(len(json_log['chara_info']['race_result_list']), len([x for x in json_log['chara_info']['race_result_list'] if x['result_rank'] == 1])))
    print('お休み回数:{}'.format(len([x for x in json_log['log'] if 'command_id' in x and x['command_id'] == 701])))

    labels = '初期値', 'トレーニング', 'トレーニング(夏合宿)', 'イベント', 'レース', '継承', '称号', 'アイテム'
    data = [initial.sum(), training.sum(), training_summer.sum(), event.sum(), race.sum(), succession.sum(), nickname.sum(), goods.sum()]  # 条件ごとのステータス上昇値を計算してグラフ用のデータを作成

    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels=labels, autopct=lambda p: round(np.sum(data) * p / 100), startangle=90, counterclock=False)

    image_folder = os.path.join(log_folder, 'image')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # plt.show()
    plt.savefig(os.path.join(image_folder, single_mode_chara_id.zfill(6) + '.png'))


print('最新のsingle_mode_chara_id: ' + [x for x in os.listdir(log_folder) if re.match('^[0-9]', x)][-1].replace('.json', ''))
while True:
    main(input('解析したいsingle_mode_chara_idを入力してください:'))
