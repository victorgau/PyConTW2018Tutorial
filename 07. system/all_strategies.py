
import numpy as np
import pandas as pd
import talib
from talib import MA_Type

# 這是我們的策略的部分
# 主要只是要算出進出的訊號 signals 跟何時持有部位 positions
# 底下是一個突破系統的範例

def Breakout_strategy(df):
    """
    進場點：突破前一日的 20 日高點
    出場點：突破前一日的 10 日低點
    """
    # Donchian Channel
    df['20d_high'] = np.round(pd.Series.rolling(df['Close'], window=20).max(), 2)
    df['10d_low'] = np.round(pd.Series.rolling(df['Close'], window=10).min(), 2)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['Close'][t] > df['20d_high'][t-1]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['Close'][t] < df['10d_low'][t-1]:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def RSI_7030_strategy(df):
    """
    進場點：RSI < 30
    出場點：RSI > 70
    """
    df['RSI'] = talib.RSI(df['Close'].values)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['RSI'][t-1] < 30:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['RSI'][t-1] > 70:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def RSI_8020_strategy(df):
    """
    進場點：RSI < 20
    出場點：RSI > 80
    """
    df['RSI'] = talib.RSI(df['Close'].values)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['RSI'][t-1] < 20:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['RSI'][t-1] > 80:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def BBands_strategy(df):
    
    df['UBB'], df['MBB'], df['LBB'] = talib.BBANDS(df['Close'].values, matype=MA_Type.T3)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['Close'][t] < df['LBB'][t-1]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['Close'][t] > df['UBB'][t-1]:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def 第一組_strategy(df):
    close=pd.DataFrame(df["Close"])
    short_win = 12    # 短期EMA平滑天数
    long_win  = 26    # 長期EMA平滑天数
    macd_win  = 20    # DEA線平滑天数
    macd_tmp  =  talib.MACD( df['Close'].values,fastperiod = short_win ,slowperiod = long_win ,signalperiod = macd_win )
    df['DIF'] =macd_tmp [ 0 ]
    df['DEA'] =macd_tmp [ 1 ]
    df['MACD']=macd_tmp [ 2 ]
    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['DIF'][t] > 0 and df['DEA'][t] >0 and df['DIF'][t] > df['DEA'][t] and df['DIF'][t-1]<df['DEA'][t-1]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['DIF'][t] < 0 and df['DEA'][t] < 0 and df['DIF'][t] < df['DEA'][t] and df['DIF'][t-1]>df['DEA'][t-1]:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def Team3_strategy(df):
    """
    主要使用BBand + 5MA策略，
    中軌為20ma，上下軌為正負1.5sd
    # 若5MA開始向上突破下軌，低檔買進
    # 若收盤價向下跌破中軌，獲利了結趕快落跑
    """

    df['5ma'] = pd.Series.rolling(df['Close'], window=5).mean()
    # bbands策略,N=20
    df['20ma'] = pd.Series.rolling(df['Close'], window=20).mean()
    df['SD'] = pd.Series.rolling(df['Close'], window=20).std()
    # 上軌=20ma+1.5sd ,中軌=20ma, 下軌=20ma-1.5sd
    df['upbbands'] = df['20ma']+1.5*df['SD']
    df['midbbands']=df['20ma']
    df['lowbbands'] = df['20ma']-1.5*df['SD']

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if  (df['5ma'][t] > df['lowbbands'][t-1]):
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif  (df['Close'][t] < df['midbbands'][t-1]):
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def 中山南拳寶寶_strategy(df):
    """
    WMSR < 80時進場
    WMSR > 20時出場
    """
    df['low9'] = df['Low'].rolling(window=9).min()
    df['high9'] = df['High'].rolling(window=9).max()
    df['WMSR'] = 100*((df['high9'] - df['Close']) / (df['high9'] - df['low9']) )

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['WMSR'][t] < 80:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['WMSR'][t] > 20:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def JuianJuian4715_strategy(df):
    """
    ##strategy:以20MA為中心，上下各2個標準差為範圍的一個軌道操作方式。
    ##買進訊號:
    #1.價格由下向上 穿越下軌線時，是買進訊號
    #2.價格由下向上 穿越中間線時，股價可能加速向上，是加碼買進訊號
    #3.價格在中間線與上軌線之間波動時，為多頭市場，可作多
    """
    has_position = False
    df['signals'] = 0

    ave = pd.Series.rolling(df['Close'], window=20).mean()
    std = pd.Series.rolling(df['Close'], window=20).std()
    df['ave']= pd.Series.rolling(df['Close'], window=20).mean()
    df['upper'] = ave + 2*std
    df['lower'] = ave -2*std

    for t in range(2, df['signals'].size):
        if df['upper'][t] > df['ave'][t-1]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['lower'][t] < df['ave'][t-1]:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def 大盜韓不住_strategy(df):
    """
    乖離率,乖離率代表的就是投資者的平均報酬率，當股價漲離平均成本很多的時候，
    就可能會有大的獲利賣壓出現，讓股價往均線跌回,當股價跌出平均成本太多的時候，攤平或逢低的買盤可能會進入
    乖離率<-3% 進場 , >3.5% 出場
    """
    has_position = False
    df['6d'] = pd.Series.rolling(df['Close'], window=6).mean()
    df['BIAS'] = (df['Close'] - df['6d'] )/df['6d']
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['BIAS'][t] < -0.02:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['BIAS'][t] > 0.025:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def 財運滾滾來_strategy(df):
    """
    進場訊號:黃金交叉(20MA>60MA)、今日收盤價跌破前日BBANDS下限、乖離率(BIAS)小於-0.05[三項條件同時符合即進場]
    出場訊號:死亡交叉(20MA<60MA)、今日收盤價漲破前日BBANDS上限、乖離率(BIAS)大於 0.1[三項條件同時符合即出場]
    """
    df['20MA'] = pd.Series.rolling(df['Close'], window=20).mean()
    df['60MA'] = pd.Series.rolling(df['Close'], window=60).mean()
    df['UBB'], df['MBB'], df['LBB'] = talib.BBANDS(df['Close'].values, matype=MA_Type.T3)
    df['BIAS']= (df['Close']-df['20MA'])/df['20MA']

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['20MA'][t] > df['60MA'][t] and df['Close'][t] < df['LBB'][t-1] and df['BIAS'][t] < -0.05:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['20MA'][t] < df['60MA'][t] and df['Close'][t] > df['UBB'][t-1] and df['BIAS'][t] > 0.1:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def team2_strategy(df):
    has_position = False
    df['signals'] = 0

    """
    原先布林逆勢策略是股價上到下突破UBB買進、下到上突破賣出
    想透過收盤價下到上突破ubb、上到下突破UBB放慢進出場，搭配乖離率做調整
    """
    #
    # 進場訊號：1.六日乖離率 < -0.06
    #           2.收盤價下到上突破LBB

    # 賣出訊號：1.六日乖離率 > 0.06
    #           2.價格上到下突破UBB
    df['UBB'], df['MBB'], df['LBB'] = talib.BBANDS(df['Close'].values, matype=MA_Type.T3)
    df['MA6'] = pd.Series.rolling(df['Close'], window=6).mean()
    df['BIAS6']= (df['Close']-df['MA6'])/df['MA6']

    for t in range(2, df['signals'].size):
        if df['BIAS6'][t] < -0.06 or ( df['Close'][t] > df['LBB'][t] and df['Close'][t-1] < df['LBB'][t-1]) :
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['BIAS6'][t] > 0.06 or ( df['Close'][t-1] > df['UBB'][t-1] and df['Close'][t] > df['UBB'][t] ):
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df


def LG_minus3_CL(df):
    """
    KDJ 策略
    進場訊號: 當K>D 值 且J值小於10時進場
    出場訊號: 當K<D 值 且J值大於90時出場

    KDJ策略為 J<0 進場 J>100出場，但此設定回測結果大部分股票皆無交易訊號，故設定區間為(10,90)

    """
    df['Talib_K_index']=talib.STOCH(df["High"].values,df['Low'].values,df['Close'].values )[0]
    df['Talib_D_index']=talib.STOCH(df["High"].values,df['Low'].values,df['Close'].values )[1]
    df['Talib_J_index']=3*df['Talib_K_index']-2*df['Talib_D_index']
    has_position = False
    df['signals'] = 0
    for t in range(2,df['signals'].size):
        if df['Talib_K_index'][t] > df["Talib_D_index"][t] and df['Talib_J_index'][t]<10 :
            if not has_position:
                df.loc[df.index[t] ,"signals"]=1
                has_position =True
        elif df['Talib_K_index'][t] <df['Talib_D_index'][t] and df['Talib_J_index'][t]>90:
            if has_position:
                df.loc[df.index[t],'signals']= -1
                has_position = False


    df['positions'] = df['signals'].cumsum().shift()
    return df

def Best_strategy(df):
    """
     MACD：對長期與短期的移動平均線 收斂或發散的徵兆，加以雙重平滑處理，用來判斷買賣股票的時機與訊號(確定波段漲幅 找到買賣點)
     MACD策略：快線 (DIF) 向上突破 慢線 (MACD)。 → 買進訊號
               快線 (DIF) 向下跌破 慢線 (MACD)。→ 賣出訊號
    """
    df['EMAfast'] = pd.Series.ewm(df['Close'], span = 12).mean()
    df['EMAslow'] = pd.Series.ewm(df['Close'], span = 26).mean()
    df['DIF'] = (df['EMAfast'] - df['EMAslow'])
    df['MACD'] = pd.Series.ewm(df['DIF'], span = 9).mean()

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['DIF'][t-1]<df['MACD'][t] and df['DIF'][t]>df['MACD'][t]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['DIF'][t-1]>df['MACD'][t] and df['DIF'][t]<df['MACD'][t]:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df

def 第六組_strategy(df):
    df['MA20'] = np.round(pd.Series.rolling(df['Close'], window=20).max(), 2)
    df['MA60'] = np.round(pd.Series.rolling(df['Close'], window=60).min(), 2)

    has_position = False
    df['signals'] = 0

    """
    # 當短周期均線(MA20)由下方突破長周期均線(MA60),即為[黃金交叉],買進
    # 反之;當短周期均線(MA20)由下方跌破長周期均線(MA60),即為[死亡交叉],賣出
    """
    
    for t in range(3, df['signals'].size):
        if df['MA20'][t-2] < df['MA60'][t-2] and df['MA20'][t-1] > df['MA60'][t-1]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1  #買進的訊號
                has_position = True
        elif df['MA20'][t-2] > df['MA60'][t-2] and df['MA20'][t-1] < df['MA60'][t-1]:
            if has_position:
                df.loc[df.index[t], 'signals'] = -1 #賣出的訊號
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df
