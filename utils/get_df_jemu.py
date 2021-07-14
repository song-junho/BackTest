import JunhoFinance
import pandas as pd
from tqdm import tqdm

def get_df_jemu(jemu_type="3", data_type="qy"):
    '''
    jemu_type: 연결: "1", 개별: "2", 연결 + 개별: "3"
    data_type: 분기: "q", 연간: "y", TTM: "qy"

    return: df_jemu
    '''

    jh_db    = JunhoFinance.DataBase()
    jh_query = JunhoFinance.SqlQuery()
    con = jh_db.db_connect()

    file_name_rate   = f"finance_rate_{jemu_type}_{data_type}_table"
    file_name_is     = f"finance_is_{jemu_type}_{data_type}_table"
    file_name_status = f"finance_status_{jemu_type}_{data_type}_table"

    df_rate   = jh_query.sql_table(con, file_name_rate)
    df_is     = jh_query.sql_table(con, file_name_is)
    df_status = jh_query.sql_table(con, file_name_status)

    df_is     = df_is.reset_index()
    df_rate   = df_rate.reset_index()
    df_status = df_status.reset_index()




    df_jemu = pd.merge(left=df_is, right=df_rate, how="left", on=["일자", "종목코드", "종목명"])
    df_jemu = pd.merge(left=df_jemu, right=df_status, how="left", on=["일자", "종목코드", "종목명"])
    #
    # for stock_code in tqdm(df_jemu["종목코드"].unique()):
    #
    #     df_jemu.loc[df_jemu["종목코드"] == stock_code, "자산총계"]   = df_jemu.loc[df_jemu["종목코드"] == stock_code, "자산총계"] .fillna(method="ffill")
    #     df_jemu.loc[df_jemu["종목코드"] == stock_code, "자본총계"]   = df_jemu.loc[df_jemu["종목코드"] == stock_code, "자본총계"] .fillna(method="ffill")
    #     df_jemu.loc[df_jemu["종목코드"] == stock_code, "부채총계"]   = df_jemu.loc[df_jemu["종목코드"] == stock_code, "부채총계"] .fillna(method="ffill")
    #     df_jemu.loc[df_jemu["종목코드"] == stock_code, "이익잉여금"] = df_jemu.loc[df_jemu["종목코드"] == stock_code, "이익잉여금"].fillna(method="ffill")


    return df_jemu