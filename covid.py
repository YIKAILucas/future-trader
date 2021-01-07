# coding=utf-8

# @Author : Lucas
# @Date   : 2021/1/5 3:42 pm
# @Last Modified by:  Lucas
# @Last Modified time:
import datetime

import pandas as pd
import requests
from openpyxl import load_workbook, Workbook

country_dic = {'Russia': '俄罗斯', 'United States': '美国', 'India': '印度', 'Brazil': '巴西', 'Peru': '秘鲁', 'Colombia': '哥伦比亚',
               'Mexico': '墨西哥', 'Spain': '西班牙', 'South Africa': '南非', 'Argentina': '阿根廷', 'France': '法国', 'Chile': '智利',
               'Iran': '伊朗',
               'UK': '英国', 'Italy': '意大利', 'Germany': '德国', 'Canada': '加拿大', 'Japan': '日本本土'}

pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 100)
pd.set_option('display.max_columns', None)


def data_writer(new_data):
    save_path = 'generated/疫情數據.xlsx'

    pre_data = pd.DataFrame(pd.read_excel(save_path, index_col=0))
    ## 访问指定sheet页的方法：
    book = load_workbook(save_path)
    sheet: Workbook = book['疫情数据']
    print(sheet)

    new_data_rows = pre_data.shape[0]  # 获取原数据的行数
    # new_data.to_excel(writer, startrow=new_data_rows + 1, index=False,
    #                   header=False)  # 将数据写入excel中的geshi表,从第一个空行开始写
    date = pre_data.iloc[new_data_rows - 1, :].name.date()
    print(date)
    now = datetime.date.today()
    print((now - date) > datetime.timedelta())

    # date = pre_data.iloc[new_data_rows-1,1].index
    # print(date)
    # writer.save()  # 保存

    writer = pd.ExcelWriter(save_path, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    pass


def data_fetch() -> pd.DataFrame:
    static_url = 'https://api.inews.qq.com/newsqa/v1/automation/foreign/daily/list?country='
    big = pd.DataFrame(columns=[i for i in country_dic.keys()], )
    for k, v in country_dic.items():
        url = f'{static_url}{v}'
        print(url)
        # print(k)
        data = requests.post(url)
        json_data = data.json()["data"]

        df = pd.DataFrame(json_data)

        df['tmp'] = df['y'].str.cat(df['date'])
        df['date'] = pd.to_datetime(df['tmp'], format="%Y%m.%d")

        big[k] = df['confirm_add']

    return big


def adapt_data():
    pd.DataFrame()
    pass


if __name__ == '__main__':
    new_data = data_fetch()
    print(new_data)
    # adapt_data()
    # data_writer(None)
