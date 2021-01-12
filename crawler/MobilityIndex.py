import datetime
from typing import List

import numpy as np
import pandas as pd
import requests
from openpyxl import load_workbook

pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 100)
pd.set_option('display.max_columns', None)

col: List[str] = ['Date', 'Washington DC', 'New York City', 'Los Angeles', 'San Francisco', 'Berlin', 'London', 'Paris',
                  'Rome']


def write_data(main_data: pd.DataFrame):
    pds = pd.Series(main_data['Date'].values)
    new_df = pds
    # 初始化日期
    for i in range(len(col) - 2):
        new_df = new_df.append(pds)
    new_data: pd.DataFrame = pd.DataFrame({'Date': new_df})
    new_data['City'] = np.nan
    new_data['ID'] = '  '

    new_data['Mobility Index'] = np.nan
    new_data['Creator'] = 'Han'
    # 循环修改城市名
    single = 0
    for i in range(len(col) - 1):
        new_data.iloc[single:single + 7, 1] = col[i + 1]
        single += 7
    # main_data.reindex(index=pd.date_range('2020-12-08', periods=6))
    main_data.set_index('Date', inplace=True)
    new_data.set_index('Date', inplace=True, drop=False)
    for i in range(len(col) - 1):
        new_data.loc[new_data.loc[:, 'City'] == col[i + 1], 'Mobility Index'] = main_data.loc[:, col[i + 1]]
    # new_data.set_index('ID', inplace=True)
    # new_data.reset_index(drop=True)
    new_data['City'] = new_data['City'].map(lambda x: '华盛顿' if x == 'Washington DC' else x)
    new_data['City'] = new_data['City'].map(lambda x: '纽约' if x == 'New York City' else x)
    new_data['City'] = new_data['City'].map(lambda x: '洛杉矶' if x == 'Los Angeles' else x)
    new_data['City'] = new_data['City'].map(lambda x: '旧金山' if x == 'San Francisco' else x)
    new_data['City'] = new_data['City'].map(lambda x: '柏林' if x == 'Berlin' else x)
    new_data['City'] = new_data['City'].map(lambda x: '伦敦' if x == 'London' else x)
    new_data['City'] = new_data['City'].map(lambda x: '巴黎' if x == 'Paris' else x)
    new_data['City'] = new_data['City'].map(lambda x: '罗马' if x == 'Rome' else x)

    new_data = new_data[['ID', 'Date', 'City', 'Mobility Index', 'Creator']]
    print(f'newdata{new_data}')
    # TODO 调整excel 右对齐
    # new_data.style.set_properties(**{'text-align': 'right'})
    save_path = 'generated/世界主要城市活动指数.xlsx'

    pre_data = pd.DataFrame(pd.read_excel(save_path, sheet_name='geshi'))
    writer = pd.ExcelWriter(save_path, engine='openpyxl')
    book = load_workbook(save_path)
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    # 筛选数据，找到tail日期
    new_data_rows = pre_data.shape[0]  # 获取原数据的行数
    # 找到日期起点终点
    old_date = pre_data.iloc[new_data_rows - 1, :].ReportDate.date()
    head_date = old_date + datetime.timedelta(days=1)
    candidate = new_data[(new_data['Date'] >= str(old_date))]
    print(f'head->{head_date}')
    # print(f'newdata{new_data}')
    # print(f'new_data\n{candidate}')

    # candidate.to_excel(writer, sheet_name='geshi', startrow=new_data_rows + 1, index=False,
    #                   header=False)  # 将数据写入excel中的geshi表,从第一个空行开始写
    # writer.save()  # 保存


def download(path):
    today = datetime.date.today()
    single_day = datetime.timedelta(days=1)
    yesterday = today - single_day
    yesterday = yesterday.strftime('%Y%m%d')
    print(yesterday)
    url = f'https://cdn.citymapper.com/data/cmi/Citymapper_Mobility_Index_{yesterday}.csv'
    # url = f'https://cdn.citymapper.com/data/cmi/Citymapper_Mobility_Index_{20201215}.csv'
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)


if __name__ == '__main__':
    file_path = './downloadFile/Citymapper_Mobility.csv'
    # 下载网络csv数据
    # 网址 https://citymapper.com/cmi
    # download(file_path)
    data_online = pd.read_csv(file_path, header=3)

    data_online = data_online.loc[:, col]
    # print(f'data_online{data_online}')
    write_data(data_online)
