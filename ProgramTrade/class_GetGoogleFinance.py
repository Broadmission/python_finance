# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 09:11:04 2017
1.自Google finance抓取台股日資料(任意期間)
2.繪製OHLC股票圖(K線)
3.存入EXCEL檔案
@author: User
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator, DayLocator
from matplotlib.finance import candlestick_ohlc
import datetime
import matplotlib.dates as dt
import requests
import simplejson as json

class GetGoogleFinance():
    def __init__(self,stkno,startdate,enddate):
        self.sdate=startdate
        self.edate=enddate
        S_date=datetime.datetime.strftime(startdate,'%Y%m%d')
        E_date=datetime.datetime.strftime(enddate,'%Y%m%d')
        self.fn=str(stkno)+'_'+S_date+'_'+E_date+'.xlsx'
        self.stkno=stkno
        self.stkid=''
        self.writer=pd.ExcelWriter(self.fn)
        
    def savetoexcel(self,data,sheetname):
        data.to_excel(self.writer,sheetname,index=False)
        self.writer.save()
    
    def getid(self):
        try:
            r = requests.get("https://finance.google.com/finance/info", \
                             params = {"client":"ig", "q":self.stkno})
        except Exception as err:
            print(err)
            r = []
        else:
            s=r.text[4:]
            o=json.loads(s)
            self.stkid=str(o[0]['id'])
            #print(stkid)
        return 

    def getstock(self,asc=False):
        s_yy=self.sdate.year
        s_mm='{:%b}'.format(self.sdate)
        s_dd=self.sdate.day
        e_yy=self.edate.year
        e_mm='{:%b}'.format(self.edate)
        e_dd=self.edate.day 
        Data=pd.DataFrame()
        for startrow in range(1,10200,200):
            try:
                url='https://www.google.com/finance/historical?cid={}&startdate={}+{}%2C+{}&enddate={}+{}%2C+{}&num=200&ei=91FUWbDaMIuk0AS8mKzQDg&start={}'\
                .format(self.stkid,s_mm,s_dd,s_yy,e_mm,e_dd,e_yy,startrow)
                data=pd.read_html(url)[2]
                data=data.drop(data.columns[[0]],axis=0)
                Data=Data.append(data,ignore_index=True)
            except Exception as err:
                print(err)
                break
        Data.columns=['dates','open','high','low','close','volume']
        Data=Data.replace('-','0')
        Data[['open','high','low','close','volume']]=\
        Data[['open','high','low','close','volume']].astype(float)
        for i in range(len(Data)):
                Data['dates'].loc[i]=datetime.datetime.strptime\
                (Data['dates'].loc[i], "%b %d, %Y").date()
        if asc==True:
            Data=Data.sort_index(by=['dates'],ascending=[True])
            
        return Data
    
if __name__ == "__main__":
    mondays = MonthLocator(bymonthday=1)        # major ticks on the mondays
    alldays = DayLocator()              # minor ticks on the days
    MonthFormatter = DateFormatter('%b %d %Y')  # e.g., Jan 12
    dayFormatter = DateFormatter('%d')      # e.g., 12
    '''
    Get data from google finance
    '''    
    stkno='2330'
    start = datetime.datetime(2016,6,1)
    end = datetime.datetime(2017,6,1)
    Gdata=GetGoogleFinance(stkno,start,end)
    Gdata.getid()

    Data =Gdata.getstock(True)
    '''
    Save data to excel
    '''

    Gdata.savetoexcel(Data,stkno)  
    
    Data['dates']=dt.date2num(Data['dates'])
    quotes=zip(Data.dates,Data.open,Data.high,Data.low,Data.close,Data.volume)    
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    
    ax.xaxis.set_minor_locator(mondays)
    ax.xaxis.set_major_formatter(MonthFormatter)
    
    candlestick_ohlc(ax, quotes, width=0.6)
    
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.title(stkno)
    
    plt.show()