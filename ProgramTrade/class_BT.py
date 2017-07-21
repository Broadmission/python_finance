# -*- coding: utf-8 -*-
"""Back Test class.
    心理線、長短均線指標回溯測試

"""
import pandas as pd
import numpy as np

# This is a comment of a class.
class BackTest:
    """A docstring of the class."""
    # This is a comment of the method.
    def __init__(self,fn):
        """A docstring of the __init__."""
   #     self.RK = RK                                 #保留K線數
   #     self.TK = TK                                 #測試K線數
        
        self.table= pd.read_excel(fn)
        (self.r,self.c)=self.table.shape
        self.Open=self.table['開盤價']
        self.Close=self.table['收盤價']
        self.Psy=np.zeros(self.r)          #心理線買賣
        self.Updown=np.zeros(self.r)       #上漲、下跌
        self.MAI=np.zeros(self.r)          #均線買賣
        self.MAIsub=np.zeros(self.r)       #長短均線差
        self.BS=np.zeros(self.r)           #綜合判斷買賣
        self.Pos = np.zeros(self.r)        #部位
        self.Acct=np.zeros(self.r)          #帳戶餘額
        self.Market=np.zeros(self.r)       #對準市場

#判斷漲跌
        for i in range(1,self.r):
            if self.Close[i] > self.Close[i-1]:
                self.Updown[i] = 1
            else:
                self.Updown[i] = 0
    # 心理線回測.           
    def PSY(self,RK=0, TK=0, n=0, Ub=0, Lb=0, MaxLong=0, MaxShort=0):
        """A docstring of a method."""
        if TK == 0:
            TK = self.r
        self.Market=np.zeros(self.r) 
#心理線買賣點
        for i in range(RK-1,TK):
               # 計算心理線指標
            wk = self.Updown[i-n+1:i+1].mean()
            if  wk <= Lb:
               self. Psy[i] = 1
            elif wk >= Ub:
                self.Psy[i] = -1
            else:
                self.Psy[i] = 0        

#部位計算
        for i in range(RK-1,TK):
            if self.Pos[i-1] + self.Psy[i-1]  >= MaxLong :
                self.Pos[i] = MaxLong
            elif self.Pos[i-1] + self.Psy[i-1]  <= MaxShort :
                self.Pos[i] = MaxShort
            else:
                self.Pos[i] = self.Pos[i-1] + self.Psy[i-1]  
            self.Acct[i] = self.Acct[i-1] - (self.Pos[i] - self.Pos[i-1]) * self.Open[i]     #帳戶餘額
            self.Market[i]=self.Acct[i] + self.Pos[i] * self.Close[i]                   #對準市場
        Bh = self.Close[TK-1] - self.Open[RK]   
        return (self.Market[TK-1], Bh,self.Market)      #傳回報酬
    # 均線指標回測.           
    def MA(self,RK=0, TK=0, MaL=0, MaS=0, MaxLong=0, MaxShort=0):
        """A docstring of a method.""" 
        if TK == 0:
            TK = self.r
        self.Market=np.zeros(self.r) 
        #長短均線差
        for i in range(RK-2,TK):
               # 計算均線短指標
            ms = self.Close[i-MaS+1:i+1].mean()
            ml = self.Close[i-MaL+1:i+1].mean()
            self.MAIsub[i] = ms - ml
        #均線買賣點
        for i in range(RK-1,TK):
            if  self.MAIsub[i-1]  <= 0 and self.MAIsub[i] > 0 :
                self.MAI[i] = 1
            elif self.MAIsub[i-1]  > 0 and self.MAIsub[i] <= 0 :
                self.MAI[i] = -1
            else:
                self.MAI[i] = 0                            
        #部位計算
        for i in range(RK-1,TK):
            if self.Pos[i-1] + self.MAI[i-1]  >= MaxLong :
                self.Pos[i] = MaxLong
            elif self.Pos[i-1] + self.MAI[i-1]  <= MaxShort :
                self.Pos[i] = MaxShort
            else:
                self.Pos[i] = self.Pos[i-1] + self.MAI[i-1]  
            self.Acct[i] = self.Acct[i-1] - (self.Pos[i] - self.Pos[i-1]) * self.Open[i]     #帳戶餘額
            self.Market[i]=self.Acct[i] + self.Pos[i] * self.Close[i]       
        Bh = self.Close[TK-1] - self.Open[RK]   
        return (self.Market[TK-1], Bh,self.Market)      #傳回報酬
    # 複合指標回測.           
    def COMBO(self,RK=0, TK=0,n=0, Ub=0, Lb=0, MaL=0, MaS=0, MaxLong=0, MaxShort=0):
        """A docstring of a method.""" 
        if TK == 0:
            TK = self.r
        self.Market=np.zeros(self.r) 
#心理線買賣點
        for i in range(RK-1,TK):
               # 計算心理線指標
            wk = self.Updown[i-n+1:i+1].mean()
            if  wk <= Lb:
               self. Psy[i] = 1
            elif wk >= Ub:
                self.Psy[i] = -1
            else:
                self.Psy[i] = 0        
        #長短均線差
        for i in range(RK-2,TK):
               # 計算均線短指標
            ms = self.Close[i-MaS+1:i+1].mean()
            ml = self.Close[i-MaL+1:i+1].mean()
            self.MAIsub[i] = ms - ml
        #均線買賣點
        for i in range(RK-1,TK):
            if  self.MAIsub[i-1]  <= 0 and self.MAIsub[i] > 0 :
                self.MAI[i] = 1
            elif self.MAIsub[i-1]  > 0 and self.MAIsub[i] <= 0 :
                self.MAI[i] = -1
            else:
                self.MAI[i] = 0                            
        #綜合判斷買賣點           
        for i in range(RK-1,TK):
            if  self.MAI[i]  == 1 or self.Psy[i] == 1 :
                self.BS[i] = 1
            elif self.MAI[i]  == -1 or self.Psy[i] == -1 :
                self.BS[i] = -1
            else:
                self.BS[i] = 0    
        #部位計算
        for i in range(RK-1,TK):
            if self.Pos[i-1] + self.BS[i-1]  >= MaxLong :
                self.Pos[i] = MaxLong
            elif self.Pos[i-1] + self.BS[i-1]  <= MaxShort :
                self.Pos[i] = MaxShort
            else:
                self.Pos[i] = self.Pos[i-1] + self.BS[i-1]  
            self.Acct[i] = self.Acct[i-1] - (self.Pos[i] - self.Pos[i-1]) * self.Open[i]     #帳戶餘額
            self.Market[i]=self.Acct[i] + self.Pos[i] * self.Close[i]       
        Bh = self.Close[TK-1] - self.Open[RK]   
        return (self.Market[TK-1], Bh,self.Market)      #傳回報酬     
                                   
if __name__ == "__main__":
     fn = '../file/台指期.xlsx'
     tb= BackTest(fn)
     (rtn, bh,market) = tb.PSY(50,0,15, 0.75, 0.25, 2, -2)
     print('心理線報酬點數    = {:-10.0f}, BH報酬 = {:d}'.format(rtn,bh))
     (rtn, bh,market) = tb.MA(50,0,20, 10, 2, -2)
     print('均線報酬點數      = {:-10.0f}, BH報酬 = {:d}'.format(rtn,bh))
     (rtn, bh,market) = tb.COMBO(50,0,15, 0.75, 0.25, 20, 10, 2, -2)
     print('複合指標報酬點數  = {:-10.0f}, BH報酬 = {:d}'.format(rtn,bh))

