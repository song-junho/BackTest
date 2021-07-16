import pandas as pd
from dateutil.relativedelta import relativedelta

'''
장부 관리
1. 자산 장부: df_balance_sheet
2. 거래 장부: df_trade_sheet
3. 포트폴리오 장부: df_port_sheet
'''

class sheet:
    df_balance_sheet = pd.DataFrame(columns=["일자", "investment_asset", "cash", "total_asset"])
    df_trade_sheet = pd.DataFrame(columns=["일자", "종목명", "종목코드", "buy_sell", "price", "volume"])
    df_port_sheet = pd.DataFrame(columns=["일자", "종목명", "종목코드", "price", "volume", "stock_asset"])

    def __init__(self, dict_df_stock, date_range, start_asset):

        self.dict_df_stock = dict_df_stock

        date_start = date_range[0] - relativedelta(days=1)
        self.df_balance_sheet.loc[0] = [date_start, 0, start_asset, start_asset]

    def append_df_balance_sheet(self, date_daily):
        '''
        자산장부 업데이트

        :param date_daily:
        :param investment_asset:
        :param cash:
        :param total_asset:
        :return:
        '''

        # 금일 트레이딩된 종목 추출
        df_today_trade = self.df_trade_sheet[self.df_trade_sheet["일자"] == date_daily]

        # 금일 트레이딩된 금액 정산
        df_today_trade["trade_asset"] = df_today_trade["price"] * df_today_trade["volume"]
        buy_asset = df_today_trade.loc[df_today_trade["buy_sell"] == "Buy", "trade_asset"].sum()
        sell_asset = df_today_trade.loc[df_today_trade["buy_sell"] == "Sell", "trade_asset"].sum()

        # 보유 현금(기 보유현금 - 매수금 + 매도금), 투자자산, 총 자산 업데이트
        cash = self.df_balance_sheet.iloc[-1]["cash"] - buy_asset + sell_asset
        investment_asset = self.df_port_sheet[self.df_port_sheet["일자"] == date_daily]["stock_asset"].sum()
        total_asset = cash + investment_asset

        # balance_sheet 업데이트
        self.df_balance_sheet = self.df_balance_sheet.append({"일자": date_daily,
                                                              "investment_asset": investment_asset,
                                                              "cash": cash,
                                                              "total_asset": total_asset,
                                                              }, ignore_index=True)

    def append_df_trade_sheet(self, df_trade_stocks, date_trade, buy_sell):
        '''
        거래장부 업데이트

        :param df_trade_stocks: 거래 종목군
        :param date_trade: 거래일자
        :param buy_sell: 매수/매도
        :param cash: 보유 현금
        :return:
        '''

        # 전일자 현금
        cash = self.df_balance_sheet.iloc[-1]["cash"]

        dict_df_stock = self.dict_df_stock

        if buy_sell == "Buy":

            stock_asset = cash / len(df_trade_stocks)  # 종목당 배정된 투자금액

            for num in range(0, len(df_trade_stocks)):
                stock_name = df_trade_stocks.loc[num, "종목명"]
                stock_code = df_trade_stocks.loc[num, "종목코드"]

                stock_price = dict_df_stock[stock_code].loc[date_trade, "Close"]
                stock_volume = int(stock_asset / stock_price)  # 매수가능 주식수

                self.df_trade_sheet = self.df_trade_sheet.append({"일자": date_trade,
                                                                  "종목명": stock_name,
                                                                  "종목코드": stock_code,
                                                                  "buy_sell": buy_sell,
                                                                  "price": stock_price,
                                                                  "volume": stock_volume,
                                                                  }, ignore_index=True)

        elif buy_sell == "Sell":

            for num in range(0, len(df_trade_stocks)):
                stock_name = df_trade_stocks.loc[num, "종목명"]
                stock_code = df_trade_stocks.loc[num, "종목코드"]

                stock_price = dict_df_stock[stock_code].loc[date_trade, "Close"]

                date_ex = self.df_port_sheet["일자"].unique()[-1]
                stock_volume = \
                self.df_port_sheet[(self.df_port_sheet["일자"] == date_ex) & (self.df_port_sheet["종목코드"] == stock_code)][
                    "volume"].values[0]

                self.df_trade_sheet = self.df_trade_sheet.append({"일자": date_trade,
                                                                  "종목명": stock_name,
                                                                  "종목코드": stock_code,
                                                                  "buy_sell": buy_sell,
                                                                  "price": stock_price,
                                                                  "volume": stock_volume,
                                                                  }, ignore_index=True)

    def append_df_port_sheet(self, date_daily, date_ex):
        '''
        프트폴리오 업데이트

        :param date_daily:
        :param investment_asset:
        :param cash:
        :param total_asset:
        :return:
        '''

        dict_df_stock = self.dict_df_stock

        # 금일 트레이딩된 종목 추출
        df_today_trade = self.df_trade_sheet[self.df_trade_sheet["일자"] == date_daily]

        # 전일자 df_port_sheet_ex(전일자 -> 금일자 이월)
        df_port_sheet_ex = self.df_port_sheet[self.df_port_sheet["일자"] == date_ex].copy().reset_index(drop=True)
        df_port_sheet_ex["일자"] = date_daily

        # 전일자 df_port_sheet_ex 업데이트 (현재 종목의 종가, 종목당 자산)
        for num in range(0, len(df_port_sheet_ex)):
            stock_code = df_port_sheet_ex.loc[num, "종목코드"]
            vol = df_port_sheet_ex.loc[num, "volume"]

            stock_price = dict_df_stock[stock_code].loc[date_daily, "Close"]

            df_port_sheet_ex.loc[num, "price"] = stock_price
            df_port_sheet_ex.loc[num, "stock_asset"] = vol * stock_price

        # 전일자 port_sheet(이월) 업데이트 (종목 보유량, Trade 적용)
        # 거래가 없는 경우
        if len(df_today_trade) == 0:
            None

        else:
            for num in range(0, len(df_today_trade)):

                stock_name = df_today_trade.iloc[num]["종목명"]
                stock_code = df_today_trade.iloc[num]["종목코드"]
                buy_sell = df_today_trade.iloc[num]["buy_sell"]
                stock_price = df_today_trade.iloc[num]["price"]
                trade_vol = df_today_trade.iloc[num]["volume"]

                if buy_sell == "Buy":

                    # 보유 종목 매수
                    if len(df_port_sheet_ex[df_port_sheet_ex["종목코드"] == stock_code]) > 0:

                        ex_vol = df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code, "volume"]

                        vol = ex_vol + trade_vol
                        stock_asset = stock_price * vol

                        df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code, "volume"] = vol
                        df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code, "stock_asset"] = stock_asset

                    # 신규 종목 매수
                    else:

                        stock_asset = stock_price * trade_vol

                        df_port_sheet_ex = df_port_sheet_ex.append({"일자": date_daily,
                                                                    "종목명": stock_name,
                                                                    "종목코드": stock_code,
                                                                    "price": stock_price,
                                                                    "volume": trade_vol,
                                                                    "stock_asset": stock_asset
                                                                    }, ignore_index=True)

                elif buy_sell == "Sell":

                    # 보유 종목 매도
                    if len(df_port_sheet_ex[df_port_sheet_ex["종목코드"] == stock_code]) > 0:

                        ex_vol = df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code, "volume"].values[0]

                        vol = ex_vol - trade_vol
                        stock_asset = stock_price * vol

                        # 보유 수량이 0인 경우, 해당 종목 port_sheet 내 제거
                        if vol == 0:
                            drop_index = df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code].index
                            df_port_sheet_ex = df_port_sheet_ex.drop(drop_index)
                        else:
                            df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code, "volume"] = vol
                            df_port_sheet_ex.loc[df_port_sheet_ex["종목코드"] == stock_code, "stock_asset"] = stock_asset

        # 전일자 port_sheet(이월)) -> port_sheet 업데이트
        self.df_port_sheet = self.df_port_sheet.append(df_port_sheet_ex, ignore_index=True)
