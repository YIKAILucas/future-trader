import pandas as pd
from openpyxl import load_workbook

col = ['Date', 'Washington DC', 'New York City', 'Los Angeles', 'San Francisco', 'Berlin', 'London', 'Paris',
       'Rome']


def write_data(data_online: pd.DataFrame):
    super_frame = []
    for i in col[1:]:
        data_num = data_online[[i]]
        data_num.rename(columns={i: 'mobility'}, inplace=True)
        df_date = data_online[[col[0]]]
        df2 = pd.DataFrame(columns=['City'], index=data_num.index.values,
                           data=[i, i, i, i, i, i, i])
        name_l = ['Han'] * 7
        df_name = pd.DataFrame(columns=['Creator'], index=data_num.index.values,
                               data=name_l)
        # print(df2)
        df_none = pd.DataFrame(columns=['Ne'], index=data_num.index.values,
                               data=[None]*7)

        new_frame = pd.concat([df_none, df_date, df2, data_num, df_name], axis=1)
        # new_frame=pd.concat([new_frame,df1], axis=1)

        super_frame.append(new_frame)

    df = pd.concat(
        [super_frame[0], super_frame[1], super_frame[2], super_frame[3], super_frame[4], super_frame[5],
         super_frame[6],super_frame[7]], axis=0)

    df['City'] = df['City'].map(lambda x: '华盛顿' if x == col[1] else x)
    df['City'] = df['City'].map(lambda x: '纽约' if x == col[2] else x)
    df['City'] = df['City'].map(lambda x: '洛杉矶' if x == col[3] else x)
    df['City'] = df['City'].map(lambda x: '旧金山' if x == col[4] else x)
    df['City'] = df['City'].map(lambda x: '柏林' if x == col[5] else x)
    df['City'] = df['City'].map(lambda x: '伦敦' if x == col[6] else x)
    df['City'] = df['City'].map(lambda x: '巴黎' if x == col[7] else x)
    df['City'] = df['City'].map(lambda x: '罗马' if x == col[8] else x)

    # print(df)
    # for i in new_frame:
    #     super_frame
    # result2 = [(1, 'a', '2', 'ss'), (2, 'b', '2', '33'), (3, 'c', '4', 'bbb')]  # 需要新写入的数据
    # df = pd.DataFrame(result2, columns=['ID', 'ReportDate', 'City', 'name'])  # 列表数据转为数据框
    df1 = pd.DataFrame(pd.read_excel('世界主要城市活动指数.xlsx', sheet_name='geshi'))  # 读取原数据文件和表
    writer = pd.ExcelWriter('世界主要城市活动指数.xlsx', engine='openpyxl')
    book = load_workbook('世界主要城市活动指数.xlsx')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df_rows = df1.shape[0]  # 获取原数据的行数
    # print(df_rows)
    df.to_excel(writer, sheet_name='geshi', startrow=df_rows + 1, index=False,
                header=False)  # 将数据写入excel中的geshi表,从第一个空行开始写
    writer.save()  # 保存


if __name__ == '__main__':
    # data_online = pd.read_csv('Citymapper_Mobility_Index_20201215 (1).csv').tail(7)
    data_online = pd.read_csv('Citymapper_Mobility_Index_20201215 (1).csv')

    # print(data_online)
    print(data_online.tail())
    # data_online.drop(data_online.index[[0, 1, 2]], inplace=True)
    # data_online.to_csv('city.csv')
    # data_online = pd.read_csv('city.csv').head(7)
    # print(data_online.head())

    # print(data_online.index.values)
    # print(type(data_online))
    data_online = data_online.loc[:, col].tail(7)
    # for y in data_online.values:
    #   print(y)
    print(data_online)
    # write_data(data_online)
    # writer.save()  # 保存
    write_data(data_online)
