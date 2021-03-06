import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


class universe:

    def __init__(self, date_jemu, date_trade, df_jemu_3_qy, df_jemu_3_y, df_jemu_3_q):

        self.date_jemu = date_jemu
        self.date_trade = date_trade
        self.df_jemu_3_qy = df_jemu_3_qy
        self.df_jemu_3_y = df_jemu_3_y
        self.df_jemu_3_q = df_jemu_3_q

    def get_df_set(self, dict_df_condition):

        df_set = pd.DataFrame()
        list_df_set_sub = []

        for factor in dict_df_condition.keys():
            df_condition = dict_df_condition[factor]
            for num in range(0, len(df_condition)):
                condition = df_condition.loc[num]
                df_set_sub = self.get_df_set_sub(factor, condition)
                list_df_set_sub.append(df_set_sub)

        # df_set_sub들의 교집합 => df_set
        for num in range(0, len(list_df_set_sub)):
            df_set_sub = list_df_set_sub[num]

            if len(df_set) == 0:
                df_set = df_set_sub
            else:
                df_set = pd.merge(left=df_set, right=df_set_sub[["종목코드"]], how="inner", on="종목코드")

        return df_set

    def get_df_set_sub(self, factor, condition):

        date_jemu = self.date_jemu
        date_trade = self.date_trade
        df_jemu_3_qy = self.df_jemu_3_qy
        df_jemu_3_y = self.df_jemu_3_y
        df_jemu_3_q = self.df_jemu_3_q

        if factor == "Size":
            df_jemu_std_date = df_jemu_3_qy[df_jemu_3_qy["일자"] == date_jemu].copy()
            df_value = df_jemu_std_date[["종목명", "종목코드", condition["sub_factor"]]]

        elif factor == "Growth":

            v_type = condition["type"]
            sub_factor = condition["sub_factor"]
            Q_Y_TTM = condition["Q_Y"]
            QoQ_YoY = condition["QoQ_YoY"]
            period = condition["period"]
            rank_value = condition["rank_value"]
            v_range = condition["range"]
            inequality = condition["inequality"]
            value = condition["value"]

            # 적용 재무제표
            ## 연간 재무제표의 경우 연간데이터가 채워지지 않은 경우에는 작년데이터 사용
            if Q_Y_TTM == "Q":
                df_jemu_std = df_jemu_3_q

            elif Q_Y_TTM == "Y":
                df_jemu_std = df_jemu_3_y
                if date_jemu.month != 12:
                    date_jemu = date_jemu - relativedelta(months=date_jemu.month)

            elif Q_Y_TTM == "TTM":
                df_jemu_std = df_jemu_3_qy

            df_jemu_std_date = df_jemu_std[df_jemu_std["일자"] == date_jemu].copy()

            if v_type == "raw":
                df_value = df_jemu_std_date[["종목명", "종목코드", sub_factor]]

            elif v_type == "pct":

                if QoQ_YoY == "QoQ":
                    relative_month = 3

                elif QoQ_YoY == "YoY":
                    relative_month = 12

                df_jemu_ex_date = df_jemu_std[
                    df_jemu_std["일자"] == date_jemu - relativedelta(months=relative_month)].copy()

                df_merge = pd.merge(left=df_jemu_std_date[["종목코드", sub_factor]],
                                    right=df_jemu_ex_date[["종목코드", sub_factor]], how="left", on="종목코드")
                df_merge.columns = ["종목코드", sub_factor + "_ex0", sub_factor + "_ex1"]
                df_merge[sub_factor + "_성장률(%)"] = ((df_merge[sub_factor + "_ex0"] - df_merge[
                    sub_factor + "_ex1"]) / df_merge[sub_factor + "_ex1"]) * 100

                df_value = df_merge
                df_value = pd.merge(left=df_value, right=df_jemu_std_date[["종목명", "종목코드"]], how="left", on="종목코드")[
                    ["종목명", "종목코드", sub_factor + "_성장률(%)"]]
                condition["sub_factor"] = sub_factor + "_성장률(%)"

            elif v_type == "continuity":

                if QoQ_YoY == "QoQ":
                    relative_month = 3

                elif QoQ_YoY == "YoY":
                    relative_month = 12

                df_merge = pd.DataFrame()
                df_pct = pd.DataFrame()
                for num in range(0, period):

                    df_merge = \
                        df_jemu_std[
                            df_jemu_std["일자"] == date_jemu - relativedelta(months=relative_month * (num))][
                            ["일자", "종목코드", sub_factor]].copy()

                    df_jemu_ex_date = df_jemu_std[df_jemu_std["일자"] == date_jemu - relativedelta(
                        months=relative_month * (num + 1))].copy()
                    df_merge = pd.merge(left=df_merge, right=df_jemu_ex_date[["일자", "종목코드", sub_factor]],
                                        how="left", on="종목코드")
                    df_merge.columns = ["일자", "종목코드", sub_factor + "_" + str(num), "일자",
                                        sub_factor + "_" + str(num + 1)]
                    df_merge[sub_factor + "_성장률(%)"] = ((df_merge[sub_factor + "_" + str(num)] - df_merge[
                        sub_factor + "_" + str(num + 1)]) / df_merge[sub_factor + "_" + str(num)].abs()) * 100

                    if len(df_pct) == 0:
                        df_pct = df_merge[["종목코드", sub_factor + "_성장률(%)"]]
                    else:
                        df_pct = pd.merge(left=df_pct, right=df_merge[["종목코드", sub_factor + "_성장률(%)"]],
                                          how="left", on="종목코드")

                df_pct["count"] = 0
                for num in range(0, len(df_pct)):

                    count = 0
                    for col_num in range(1, len(df_pct.columns) - 1):

                        if df_pct.loc[num, df_pct.columns[col_num]] > 0:
                            count += 1
                        df_pct.loc[num, "count"] = count
                df_pct = pd.merge(left=df_pct, right=df_jemu_std_date[["종목명", "종목코드"]], how="left", on="종목코드")[
                    ["종목명", "종목코드", "count"]]
                df_value = df_pct
                condition["sub_factor"] = "count"

        df_set_sub = self.set_rank_value(df_value, condition)

        return df_set_sub

    def set_rank_value(self, df_value, condition):

        sub_factor = condition["sub_factor"]
        rank_value = condition["rank_value"]
        v_range = condition["range"]
        inequality = condition["inequality"]
        value = condition["value"]

        if rank_value == "Value":

            if inequality == "<":
                df_value = df_value[df_value[sub_factor] < value]
            elif inequality == "<=":
                df_value = df_value[df_value[sub_factor] <= value]
            elif inequality == ">":
                df_value = df_value[df_value[sub_factor] > value]
            elif inequality == ">=":
                df_value = df_value[df_value[sub_factor] >= value]

        else:
            # Rank 조건
            abs_pct = rank_value.split("_")[1]
            asc_dsc = rank_value.split("_")[2]

            if asc_dsc == "asc":
                is_asc = True
            elif asc_dsc == "dsc":
                asc_dsc = False

            if abs_pct == "%":
                if v_range == "All":
                    if inequality == "<":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[
                                   :int(len(df_value) * (value / 100)) - 1]
                    elif inequality == "<=":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[
                                   :int(len(df_value) * (value / 100))]
                    elif inequality == ">":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[
                                   int(len(df_value) * (value / 100)):]
                    elif inequality == ">=":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[
                                   int(len(df_value) * (value / 100)) - 1:]

                elif v_range == "Sector":
                    print("개발예정")
                else:
                    print("개발예정")
            elif abs_pct == "abs":

                if v_range == "All":
                    if inequality == "<":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[:value - 1]
                    elif inequality == "<=":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[:value]
                    elif inequality == ">":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[value:]
                    elif inequality == ">=":
                        df_value = df_value.sort_values(sub_factor, ascending=is_asc).iloc[value - 1:]
                elif v_range == "Sector":
                    print("개발예정")
                else:
                    print("개발예정")

        df_set_sub = df_value[["종목명", "종목코드"]]

        return df_set_sub

