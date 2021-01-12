


import pyodbc
import sys,os,io
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import time,datetime
from bs4 import BeautifulSoup
import traceback
from math import floor, ceil

from  multiprocessing import Pool
import multiprocessing
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
import pypyodbc
import os


sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')



class getDataQH:
#初始化
    def __init__(self):
        self.url = 'http://www.czce.com.cn/cn/index.htm'
        self.pwd =  os.path.abspath(os.path.dirname(__file__))

        # driver_path = pwd+r'\geckodriver-v0.25.0-win64\geckodriver'
        # os.environ['PATH'] = os.environ['PATH']+';'+driver_path

        self.firefox_path = self.pwd+r'\firefox'

        
        os.environ['PATH'] = os.environ['PATH']+';'+self.firefox_path

        self.browserOption=webdriver.FirefoxOptions()
        # self.browserOption.add_argument('-headless')

        self.driver = webdriver.Firefox(options = self.browserOption)
        # self.driver = webdriver.Firefox()

        self.recordFileName = "getQHdata_Record.txt"
        self.errorRecordFileName = "getQHdata_Record.txt"
        #self.recordFileName = "getRecord.txt"
        #self.errorRecordFileName = "getError.txt"


# 随机等待时间
    def timeSleepRandom(self,start,stop):
        timeQuantum = random.randint(start,stop)/10
        time.sleep(timeQuantum)


#文件操作
    # 
    def record(self,recordFileName,record,start):
        now = time.asctime( time.localtime(time.time()))
        f = open(recordFileName,'a')
        if start == 1:
            f.write('*'*100+'\n') 
        elif start >1 :
            f.write('-'*50+'\n') 
        f.write(record) 
        f.write('\n') 
        f.write('time:\t'+now+'\n')  
        if(start==3):
            f.write('*'*100+'\n')   
        f.close()	

    def toText(self,recordFileName,dataList):
        f = open(recordFileName,'a',encoding='utf-8')
        for ele in dataList:
            string = ''
            for key in ele:
                string = string + key+':'+ele[key]+'\n'
            f.write(string) 
            f.write('\n')     
        f.close()	

    # error 记录
    def recordError(self,recordFileName,remark):
        now = time.asctime( time.localtime(time.time()))
        f = open(recordFileName,'a')
        f.write('*'*100+'\n') 
        traceback.print_exc(file=f)
        f.write(remark) 
        f.write('\n') 
        f.write('time:\t'+now+'\n')  
        f.close()	


    def dateToString(self,value):
        result = str(value.year)
        if len(str(value.month)) == 1:
            result = result + '0' +str(value.month)
        else:
            result = result +str(value.month)
        if len(str(value.day)) == 1:
            result = result + '0' +str(value.day)
        else:
            result = result +str(value.day)
        return result


    def priceDic(self):
        priceItem = {}
        priceItem['FutureContract']=''
        priceItem['TradingDate']=''
        priceItem['LastSettlementPrice']=''
        priceItem['OpeningPrice']=''
        priceItem['HighestPrice']=''
        priceItem['LowestPrice']=''
        priceItem['ClosingPrice']=''
        priceItem['SettlementPrice']=''
        priceItem['D_price1']=''
        priceItem['D_price2']=''
        priceItem['Volume']=''
        priceItem['OpenInterest']=''
        priceItem['Increase']=''
        priceItem['VolumeTotalAmount']=''
        priceItem['DeliveryPrice']=''

        return priceItem


    def getNUM(self, d, value):
        return [k for k, v in d.items() if value in v]


    def allDateSave(self, contractList):
        # print(contractList)
        # a1 = getNUM(contractList[1], "空盘")
        # b1 = a1[0]
        # a2 = getNUM(contractList[1], "成交")
        # b2 = a2[0]
        # a3 = getNUM(contractList[1], "今收盘")
        # b3 = a3[0]
        print(contractList[0]['TradingDate'])
        #print(type(contractList[0]['OpenInterest']))
        errorFileName = 'QHcontractErrorprice#.txt'
        connectCode = 'DRIVER={SQL Server Native Client 11.0};SERVER=61.153.191.193;DATABASE=CottonDB;UID=cotton;PWD=@yanfa123456'
        # connectCode = 'DRIVER={SQL Server Native Client 11.0};SERVER=(local);DATABASE=CottonDB_12_31;UID=sa;PWD=123123'
        conn = pyodbc.connect(connectCode)
        if (len(contractList) < 1):
            return -3
        try:
            cur = conn.cursor()
            #cur.execute(' SELECT * FROM dbo.Price_Futures_ZCE_PriceDetail WHERE ReportDate = ? ', (contractList[0]['TradingDate']))
            cur.execute(' SELECT * FROM dbo.Price_Technical_ZCE_OpenInterest WHERE ReportDate = ? ',
                        (contractList[0]['TradingDate']))
            IDList = cur.fetchall()
            cur.close()
            if len(IDList) > 0:
                conn.close()
                return '-2'
            else:
                cur1 = conn.cursor()
                for i in range(0, len(contractList)-1):
                    cur1.execute('INSERT INTO Price_Futures_ZCE_PriceDetail(ReportDate,Contract,Price,MaxPrice,MinPrice,OpenInterest,TradingVolume,Creator)\
                                    VALUES(?,?,?,?,?,?,?,?)', \
                                 (contractList[i]['TradingDate'], contractList[i]['FutureContract'], contractList[i]['ClosingPrice'],
                                  contractList[i]['HighestPrice'], contractList[i]['LowestPrice'],
                                  int(contractList[i]['OpenInterest']), int(contractList[i]['Volume']), 'Henry',))  # 根据表格调整
                    cur1.execute('INSERT INTO Price_Technical_ZCE_OpenInterest(ReportDate,Contract,OpenInterest,TradingVolume,Creator)\
                                                        VALUES(?,?,?,?,?)', \
                                 (contractList[i]['TradingDate'], contractList[i]['FutureContract'],
                                  int(contractList[i]['OpenInterest']),
                                  int(contractList[i]['Volume']), 'Henry',))
                cur1.close()
                conn.commit()
                conn.close()
                print(contractList[0]['TradingDate'] + ' successful!')
                return '-1'
        except:
            conn.rollback()
            conn.close()
            self.recordError(errorFileName, contractList[0]['TradingDate'])
            print(contractList[0]['TradingDate'] + ' error!')
            return '-3'
#数据获取
    def websearch(self,dateSearch):
        try:
            #获取当月第几天
            intDay = int(dateSearch.day)  
            
            #初始页面                      
            self.driver.get(self.url)
            time.sleep(2)

            # 每日行情页面
            ac = self.driver.find_element_by_link_text("每日行情")
            ActionChains(self.driver).move_to_element(ac).click(ac).perform()
            time.sleep(5)

            #----页面切换 和 关闭操作-----------------------------------------------
            windows = self.driver.window_handles
            if len(windows) > 1:
                self.driver.switch_to.window(windows[1])
                # self.driver.close()
            #----------------------------------------------------

            # 选择日期控件
            calender = self.driver.find_element_by_class_name('rendezvous-datepicker-calendar-body')
            # 选定当月日期
            calenderSelect = calender.find_elements_by_xpath('./button')
            ac = calenderSelect[intDay-1]
            ActionChains(self.driver).move_to_element(ac).click(ac).perform()
            time.sleep(5)


            # 选择棉花品种
            itemSelect = self.driver.find_element_by_name('commodity')
            Select(itemSelect).select_by_visible_text('棉花CF')
            time.sleep(5)

            # 点击查询
            searchButton = self.driver.find_element_by_class_name('seach')
            ActionChains(self.driver).move_to_element(searchButton).click(searchButton).perform()
            time.sleep(5)

            # 切换到数据页
            self.driver.switch_to.frame('czcehqWin')

            # 解析
            html = BeautifulSoup(self.driver.page_source,'lxml')

            # 数据收集
            table = html.find('table',{'id':'tab1'})
            print(table)
            if table != None:
                contractList = []
                trList = table.findAll("tr")
                for i in range(1,len(trList)-1):
                    contractInfo = self.priceDic()
                    tdList = trList[i].find_all("td")
                    print(tdList)

                    contractInfo['FutureContract'] = "".join(tdList[0].text.split()).replace(',','')
                    contractInfo['LastSettlementPrice'] = "".join(tdList[1].text.split()).replace(',','')
                    contractInfo['OpeningPrice'] = "".join(tdList[2].text.split()).replace(',','')
                    contractInfo['HighestPrice'] = "".join(tdList[3].text.split()).replace(',','')
                    contractInfo['LowestPrice'] = "".join(tdList[4].text.split()).replace(',','')
                    contractInfo['ClosingPrice'] = "".join(tdList[5].text.split()).replace(',','')
                    contractInfo['SettlementPrice'] = "".join(tdList[6].text.split()).replace(',','')
                    contractInfo['D_price1'] = "".join(tdList[7].text.split()).replace(',','')
                    contractInfo['D_price2'] = "".join(tdList[8].text.split()).replace(',','')
                    contractInfo['Volume'] = "".join(tdList[9].text.split()).replace(',', '')
                    contractInfo['OpenInterest'] = "".join(tdList[10].text.split()).replace(',','')
                    contractInfo['Increase'] = "".join(tdList[11].text.split()).replace(',','')
                    contractInfo['VolumeTotalAmount'] = "".join(tdList[12].text.split()).replace(',','')
                    contractInfo['DeliveryPrice'] = "".join(tdList[13].text.split()).replace(',','')
                    contractInfo['TradingDate'] = str(dateSearch)
                    if (contractInfo['ClosingPrice'] == ""):
                        contractInfo['ClosingPrice'] = None
                    if (contractInfo['HighestPrice'] == ""):
                        contractInfo['HighestPrice'] = None
                    if (contractInfo['LowestPrice'] == ""):
                        contractInfo['LowestPrice'] = None

                    contractList.append(contractInfo)
                # print(contractList)

                result = self.allDateSave(contractList)
                if result == '-3':
                    self.record(self.recordFileName,'TradingDate:\t'+str(dateSearch)+'\terror!',1)
                elif result == '-2':
                    self.record(self.recordFileName,'TradingDate:\t'+str(dateSearch)+'\texists!',1)
                elif result == '-1':
                    self.record(self.recordFileName,'TradingDate:\t'+str(dateSearch)+'\tgot!',1)

                
            else:
                self.record(self.recordFileName,'   今日无行情数据！',2)
        except:
            self.recordError(self.errorRecordFileName,'数据获取失败！')
            




#获取配置文件数据
def getInfoData(recordFileName):
	f = open(recordFileName,'r')
	textInfo = f.read().splitlines()
	confInfo = {}
	f.close()
	while '' in textInfo:
		textInfo.remove('')
	if len(textInfo)>0:
		for ele in textInfo:
			try:
				confInfo[ele.split('=')[0].strip()] = ele.split('=')[1].strip()
			except Exception  as e:
				# print(recordFileName +'_Error:'+ele+'=>'+ str(e))
				continue
	return confInfo



def myJob():
    dateSearch =  datetime.date.today()                         #当天
    # dateSearch = datetime.date(2020,8,13)                       #选择日期
    getDataQH().websearch(dateSearch)
    os.system('taskkill /f /IM firefox.exe')




#####################################################################
if __name__ == '__main__':
    


    # 【手动运行】
    ####################################################
    myJob()
    ######################################################
    
    


    # 【定时运行】
    ######################################################
    # option = getInfoData('conf.txt')                            #配置文件 设置定时参数
    #
    #
    # WeekDays = option['weekdays']                               #每周星期  （0-4）=> 星期一到星期五
    # StartHour = option['hour']
    # StartMinute = option['minutes']
    # print(WeekDays)
    # print(StartHour)
    # print(StartMinute)
    # cron1 = BlockingScheduler()
    # trigger = CronTrigger(day_of_week = WeekDays,hour = StartHour,minute = StartMinute)
    # cron1.add_job(myJob,trigger)                                #myJob 定时任务内容
    # cron1.start()
    #########################################################

