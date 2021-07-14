import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import FinanceDataReader as fdr
import JunhoFinance
from tqdm import tqdm_notebook
import pickle
import numpy as np
import math

import utils
import universe


import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 코스피 영업일자를 위한 df_krx 생성
df_kospi   = fdr.DataReader("KS11")
df_kosdaq  = fdr.DataReader("KQ11")
df_krx_info = fdr.StockListing("KRX")

## 1. 재무제표 생성
df_jemu_3_qy = utils.get_df_jemu("3", "qy")
df_jemu_3_q  = utils.get_df_jemu("3", "q")
df_jemu_3_y  = utils.get_df_jemu("3", "y")


## 2. 날짜 범위 설정
date_range = pd.date_range(start = '20100120', end = '20210611')

## 3. 리밸런싱 일자 정의
df_rebalance_master = pd.DataFrame(columns = ["Quater", "RebalanceDate(MMDD)", ""])

df_rebalance_master.loc[0]  = ["1Q", "0520", ""]
df_rebalance_master.loc[1]  = ["1Q", "0620", ""]
df_rebalance_master.loc[2]  = ["1Q", "0720", ""]
df_rebalance_master.loc[3]  = ["2Q", "0820", ""]
df_rebalance_master.loc[4]  = ["2Q", "0920", ""]
df_rebalance_master.loc[5]  = ["2Q", "1020", ""]
df_rebalance_master.loc[6]  = ["3Q", "1120", ""]
df_rebalance_master.loc[7]  = ["3Q", "1220", ""]
df_rebalance_master.loc[8]  = ["3Q", "0120", ""]
df_rebalance_master.loc[9]  = ["4Q", "0220", ""]
df_rebalance_master.loc[10] = ["4Q", "0320", ""]
df_rebalance_master.loc[11] = ["4Q", "0420", ""]

### 리밸런싱 일자 및 재무적용 일자 테이블 생성
df_date_jemu_rebalance = utils.get_df_date_jemu_rebalance(df_rebalance_master, date_range, df_kospi)

## 4. 가격 Dictionary 생성
with open(r"D:\MyProject\StockPrice\DictDfStock.pickle", 'rb') as fr:
    dict_df_stock = pickle.load(fr)

# 6. 업종사전 생성
df_sector_map = pd.read_excel(r"C:\Users\송준호\Desktop\업종지도_사전.xlsx")
df_sector_map = pd.merge(left = df_sector_map, right = df_krx_info[["Symbol", "Name"]],\
                          how = "inner", left_on = "종목명", right_on = "Name")[["업종", "Category_0", "Category_1", "Category_2","Category_3","Category_4","종목명", "Symbol"]]


date_jemu  = df_date_jemu_rebalance["JemuDate"].iloc[-1]
date_trade = df_date_jemu_rebalance["RebalanceDate"].iloc[-1]

my_universe = universe(date_jemu, date_trade, df_jemu_3_qy, df_jemu_3_y, df_jemu_3_q)


print(df_jemu_3_q)