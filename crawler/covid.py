# coding=utf-8

# @Author : Lucas
# @Date   : 2021/1/5 3:42 pm
# @Last Modified by:  Lucas
# @Last Modified time:
import datetime

import pandas as pd
import requests
from openpyxl import load_workbook

country_dic = {'Russia': '俄罗斯', 'United States': '美国', 'India': '印度', 'Brazil': '巴西', 'Peru': '秘鲁', 'Colombia': '哥伦比亚',
               'Mexico': '墨西哥', 'Spain': '西班牙', 'South Africa': '南非', 'Argentina': '阿根廷', 'France': '法国', 'Chile': '智利',
               'Iran': '伊朗',
               'UK': '英国', 'Italy': '意大利', 'Germany': '德国', 'Canada': '加拿大', 'Japan': '日本本土'}

pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 100)


# pd.set_option('display.max_columns', None)


def data_reader():
    save_path = 'generated/疫情數據.xlsx'
    pre_data = pd.DataFrame(pd.read_excel(save_path, index_col=0))
    book = load_workbook(save_path)
    new_data_rows = pre_data.shape[0]  # 获取原数据的行数

    # 找到日期起点终点
    pre_date = pre_data.iloc[new_data_rows - 1, :].name.date()
    # print(head_date)
    now = datetime.date.today()
    head_date = pre_date + datetime.timedelta(days=1)
    tail_date = now - datetime.timedelta(days=1)
    print(f'head{head_date}->tail->{tail_date}')

    new_data = data_fetch()
    # print(new_data)
    needed = new_data[head_date:tail_date]
    print(needed)
    writer = pd.ExcelWriter(save_path, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    # 写入数据
    # needed.reset_index()
    # index=True把索引也写入
    needed.to_excel(writer, startrow=new_data_rows + 1, index=True,
                    header=False, sheet_name='疫情数据')  # 将数据写入excel中的geshi表,从第一个空行开始写

    writer.save()  # 保存
    book.close()


def data_fetch() -> pd.DataFrame:
    static_url = 'https://api.inews.qq.com/newsqa/v1/automation/foreign/daily/list?country='

    big = pd.DataFrame(columns=[i for i in country_dic.keys()], )
    # TODO 后面把flag的索引日期用pandas生成而不是把美国的填进去
    flag_data = requests.post(static_url + '美国').json()["data"]
    flag_df = pd.DataFrame(flag_data)

    flag_df['tmp'] = flag_df['y'].str.cat(flag_df['date'])
    flag_df['date'] = pd.to_datetime(flag_df['tmp'], format="%Y%m.%d")
    big['date'] = flag_df['date']
    big['date'] = big['date'].dt.date

    big.set_index(['date'], inplace=True)

    for k, v in country_dic.items():
        url = f'{static_url}{v}'
        print(url)
        data = requests.post(url)
        json_data = data.json()["data"]
        # 生成dataframe
        df = pd.DataFrame(json_data)

        # 拼接转换成日期
        df['tmp'] = df['y'].str.cat(df['date'])
        df['date'] = pd.to_datetime(df['tmp'], format="%Y%m.%d")
        df.set_index(['date'], inplace=True)
        big[k] = df['confirm_add']
    return big


def adapt_data():
    pd.DataFrame()
    pass


if __name__ == '__main__':
    data_reader()
    # adapt_data()
