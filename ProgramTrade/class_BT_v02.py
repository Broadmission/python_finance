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
        self.P_buy=np.zeros(self.r)        #買進價格
        self.P_sal=np.zeros(self.r)        #賣出價格

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
        Bcnt=0                 #買進次數
        Scnt=0                 #賣出次數
        self.P_buy=np.zeros(self.r) 
        self.P_sal=np.zeros(self.r)
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
            
            if self.Psy[i-1] == 1 and  self.Pos[i] != self.Pos[i-1]:
                Bcnt += 1
                self.P_buy[Bcnt] = self.Open[i]
                
            if self.Psy[i-1] == -1 and  self.Pos[i] != self.Pos[i-1]:
                Scnt += 1
                self.P_sal[Scnt] = self.Open[i]                   

       # print(Bcnt, Scnt)
        Bh = self.Close[TK-1] - self.Open[RK] 
        profit=np.zeros(9)
        '''
        profit[0]:總盈虧      profit[1]:總獲利    profit[2]:總虧損
        profit[3]:交易次數    profit[4]:盈餘次數  profit[5]:虧損次數  
        profit[6]:獲利因子=總獲利/總虧損  profit[7]:勝率 100*獲利次數/總交易次數
        profit[8]:報酬率
        '''
        i=1
        cost=0
        while True:
            if self.P_buy[i] == 0 and self.P_sal[i] ==0:
               # print(i)
                break
            if self.P_buy[i]==0:
                self.P_buy[i]=self.Close[TK-1]
            if self.P_sal[i]==0:
                self.P_sal[i]=self.Close[TK-1]
                
            cost += self.P_buy[i]    
            pt = self.P_sal[i] - self.P_buy[i]
            if pt >= 0:
                profit[1] += pt
                profit[4] += 1
            else:
                profit[2] -= pt
                profit[5] += 1
            profit[0] += pt
            profit[3] += 1
            i += 1    
        #print(profit)   
        if profit[2] != 0:
            profit[6] = profit[1] / profit[2]
        else:
            profit[6] = profit[1]
        profit[7]= 100*profit[4]/profit[3]
        profit[8]=100*profit[0]/cost
        return (profit, Bh)      #傳回報酬
    # 均線指標回測.           
    def MA(self,RK=0, TK=0, MaL=0, MaS=0, MaxLong=0, MaxShort=0):
        """A docstring of a method.""" 
        if TK == 0:
            TK = self.r
        Bcnt=0                 #買進次數
        Scnt=0                 #賣出次數
        self.P_buy=np.zeros(self.r) 
        self.P_sal=np.zeros(self.r)
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

            if self.MAI[i-1] == 1 and  self.Pos[i] != self.Pos[i-1]:
                Bcnt += 1
                self.P_buy[Bcnt] = self.Open[i]
                
            if self.MAI[i-1] == -1 and  self.Pos[i] != self.Pos[i-1]:
                Scnt += 1
                self.P_sal[Scnt] = self.Open[i] 
                
        Bh = self.Close[TK-1] - self.Open[RK] 
        profit=np.zeros(9)
        '''
        profit[0]:總盈虧      profit[1]:總獲利    profit[2]:總虧損
        profit[3]:交易次數    profit[4]:盈餘次數  profit[5]:虧損次數  
        profit[6]:獲利因子=總獲利/總虧損  profit[7]:勝率 100*獲利次數/總交易次數
        profit[8]:報酬率
        '''
        i=1        
        cost=0        
        while True:
            if self.P_buy[i] == 0 and self.P_sal[i] ==0:
               # print(i)
                break
            if self.P_buy[i]==0:
                self.P_buy[i]=self.Close[TK-1]
            if self.P_sal[i]==0:
                self.P_sal[i]=self.Close[TK-1]
                
            cost += self.P_buy[i]
            pt = self.P_sal[i] - self.P_buy[i]
            if pt >= 0:
                profit[1] += pt
                profit[4] += 1
            else:
                profit[2] -= pt
                profit[5] += 1
            profit[0] += pt
            profit[3] += 1
            i += 1    
        #print(profit)   
        if profit[2] != 0:
            profit[6] = profit[1] / profit[2]
        else:
            profit[6] = profit[1]
        profit[7]= 100*profit[4]/profit[3]
        profit[8]=100*profit[0]/cost
        return (profit, Bh)      #傳回報酬
    # 複合指標回測.           
    def COMBO(self,RK=0, TK=0,n=0, Ub=0, Lb=0, MaL=0, MaS=0, MaxLong=0, MaxShort=0):
        """A docstring of a method.""" 
        if TK == 0:
            TK = self.r
        Bcnt=0                 #買進次數
        Scnt=0                 #賣出次數
        self.P_buy=np.zeros(self.r) 
        self.P_sal=np.zeros(self.r)
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

            if self.BS[i-1] == 1 and  self.Pos[i] != self.Pos[i-1]:
                Bcnt += 1
                self.P_buy[Bcnt] = self.Open[i]
                
            if self.BS[i-1] == -1 and  self.Pos[i] != self.Pos[i-1]:
                Scnt += 1
                self.P_sal[Scnt] = self.Open[i]       
        Bh = self.Close[TK-1] - self.Open[RK]   
        profit=np.zeros(9)
        '''
        profit[0]:總盈虧      profit[1]:總獲利    profit[2]:總虧損
        profit[3]:交易次數    profit[4]:盈餘次數  profit[5]:虧損次數  
        profit[6]:獲利因子=總獲利/總虧損  profit[7]:勝率 100*獲利次數/總交易次數  
        profit[8]:報酬率
        '''
        i=1 
        cost=0               
        while True:
            if self.P_buy[i] == 0 and self.P_sal[i] ==0:
               # print(i)
                break
            if self.P_buy[i]==0:
                self.P_buy[i]=self.Close[TK-1]
            if self.P_sal[i]==0:
                self.P_sal[i]=self.Close[TK-1]
                
            cost += self.P_buy[i]
            pt = self.P_sal[i] - self.P_buy[i]
            if pt >= 0:
                profit[1] += pt
                profit[4] += 1
            else:
                profit[2] -= pt
                profit[5] += 1
            profit[0] += pt
            profit[3] += 1
            i += 1    
        #print(profit)   
        if profit[2] != 0:
            profit[6] = profit[1] / profit[2]
        else:
            profit[6] = profit[1]
        profit[7]= 100*profit[4]/profit[3]
        profit[8]=100*profit[0]/cost         
        return (profit, Bh)      #傳回報酬     
                                   
if __name__ == "__main__":
     fn = '../file/台指期.xlsx'
     tb= BackTest(fn)
     profit=np.zeros(6)
     (profit, bh) = tb.PSY(50,0,20, 0.75, 0.25, 2, -2)
     print('心理線報酬點數    = {:-10.0f}, BH報酬 = {:d}'.format(profit[0],bh))
     print('總獲利 = {:-10.0f}, 總損失 = {:-10.0f}'.format(profit[1],profit[2]))
     print('總獲利次數 = {:-4.0f}, 總損失次數 = {:-4.0f}'.format(profit[4],profit[5]))
     print('獲利因子 = {:6.2f}, 勝率= {:6.2f} %'.format(profit[6],profit[7]))
     print('報酬率= {:6.2f} %\n'.format(profit[8]))
     
     (profit, bh) = tb.MA(50,0,20, 10, 2, -2)
     print('均線報酬點數      = {:-10.0f}, BH報酬 = {:d}'.format(profit[0],bh))
     print('總獲利 = {:-10.0f}, 總損失 = {:-10.0f}'.format(profit[1],profit[2]))
     print('總獲利次數 = {:-4.0f}, 總損失次數 = {:-4.0f}'.format(profit[4],profit[5]))
     print('獲利因子 = {:6.2f}, 勝率= {:6.2f} %'.format(profit[6],profit[7]))
     print('報酬率= {:6.2f} %\n'.format(profit[8]))
     
     (profit, bh) = tb.COMBO(50,0,15, 0.75, 0.25, 20, 10, 2, -2)
     print('複合指標報酬點數  = {:-10.0f}, BH報酬 = {:d}'.format(profit[0],bh))
     print('總獲利 = {:-10.0f}, 總損失 = {:-10.0f}'.format(profit[1],profit[2]))
     print('總獲利次數 = {:-4.0f}, 總損失次數 = {:-4.0f}'.format(profit[4],profit[5]))
     print('獲利因子 = {:6.2f}, 勝率= {:6.2f} %'.format(profit[6],profit[7]))
     print('報酬率= {:6.2f} %\n'.format(profit[8]))
     