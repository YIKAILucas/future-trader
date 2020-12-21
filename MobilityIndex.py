from typing import List

import numpy as np
import pandas as pd
from openpyxl import load_workbook

col: List[str] = ['Date', 'Washington DC', 'New York City', 'Los Angeles', 'San Francisco', 'Berlin', 'London', 'Paris',
                  'Rome']


def write_data(main_data: pd.DataFrame):
    pds = pd.Series(main_data['Date'].values)
    pdd = pds
    # 初始化日期
    for i in range(len(col) - 2):
        pdd = pdd.append(pds)
    new_data: pd.DataFrame = pd.DataFrame({'Date': pdd})
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

    print(new_data)
    new_data = new_data[['ID', 'Date', 'City', 'Mobility Index', 'Creator']]

    # TODO 调整excel 右对齐
    # new_data.style.set_properties(**{'text-align': 'right'})

    pre_data = pd.DataFrame(pd.read_excel('世界主要城市活动指数.xlsx', sheet_name='geshi'))
    writer = pd.ExcelWriter('世界主要城市活动指数.xlsx', engine='openpyxl')
    book = load_workbook('世界主要城市活动指数.xlsx')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    new_data_rows = pre_data.shape[0]  # 获取原数据的行数
    new_data.to_excel(writer, sheet_name='geshi', startrow=new_data_rows + 1, index=False,
                      header=False)  # 将数据写入excel中的geshi表,从第一个空行开始写
    # writer.save()  # 保存


if __name__ == '__main__':
    # 网址 https://citymapper.com/cmi
    data_online = pd.read_csv('Citymapper_Mobility_Index_20201215 (1).csv')

    data_online = data_online.loc[:, col].tail(7)
    write_data(data_online)
