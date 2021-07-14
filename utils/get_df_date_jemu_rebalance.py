import datetime
import pandas  as pd

def get_df_date_jemu_rebalance(df_rebalance_master, date_range, df_krx):
    '''
    리밸런싱 설정
    Case 1: 매년 @월 @일 (1년 주기)
    Case 2: 매년 @월 @일, #월 #일 (반기 주기)
    Case 3: 매년 @월 @일, #월 #일, $월 $일, %월 %일 (분기 주기)

    초기 설정한 리밸런싱 일자가 영업일이 아닌 경우 가장 가까운 일자로 수정
    '''

    def get_date_jemu(date_rebalnce, jemu_Q):
        '''
        리밸런싱 일자에 적합한 재무일자 추출 함수

        1Q: 올해의 3월 1일
        2Q: 올해의 6월 1일
        3Q: 올해의 9월 1일
        4Q: 작년의 12월 1일
        '''

        year = date_rebalnce.year
        month = date_rebalnce.month

        if jemu_Q == "1Q":
            date_jemu = datetime.datetime(year, 3, 1)
        elif jemu_Q == "2Q":
            date_jemu = datetime.datetime(year, 6, 1)
        elif (jemu_Q == "3Q") & (month > 4):
            date_jemu = datetime.datetime(year, 9, 1)
        elif (jemu_Q == "3Q") & (month < 4):
            date_jemu = datetime.datetime(year - 1, 9, 1)
        elif jemu_Q == "4Q":
            date_jemu = datetime.datetime(year - 1, 12, 1)

        return date_jemu

    df_date_jemu_rebalance = pd.DataFrame(columns=["JemuDate", "RebalanceDate"])
    list_year = date_range.year.unique()

    for year in list_year:

        for num in range(0, len(df_rebalance_master)):
            mmdd = df_rebalance_master.loc[num, "RebalanceDate(MMDD)"]
            jemu_Q = df_rebalance_master.loc[num, "Quater"]

            year = year
            month = int(mmdd[:2])
            day = int(mmdd[2:4])

            # 리밸런싱 일자 생성
            date_rebalnce = datetime.datetime(year, month, day)

            ## 리밸런싱 일자가 미래인 경우 제외
            if date_rebalnce >= date_range[-1]:
                continue
            else:
                date_rebalnce = df_krx.loc[date_rebalnce:].index[0]

            # 적용 재무 일자 생성
            date_jemu = get_date_jemu(date_rebalnce, jemu_Q)

            df_date_jemu_rebalance = df_date_jemu_rebalance.append({"JemuDate": date_jemu,
                                                                    "RebalanceDate": date_rebalnce}, ignore_index=True)

    df_date_jemu_rebalance = df_date_jemu_rebalance.sort_values("RebalanceDate")
    df_date_jemu_rebalance = df_date_jemu_rebalance.reset_index(drop=True)

    return df_date_jemu_rebalance
