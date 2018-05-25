#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import numpy as np

# MatPlotLib 的主要模組
import matplotlib.pyplot as plt

# 畫圖形週邊東西的套件
from matplotlib import gridspec
from matplotlib.ticker import  FuncFormatter

import bisect

# 畫圖用的套件
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import colorConverter
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib import colors as mcolors

from dateutil.parser import parse

# 讀股價歷史資料
from twsr import get_historical_data, get_data_months

import pandas as pd

has_chinese_font = False
chinese_font_path = r"c:\windows\fonts\simsun.ttc"
#chinese_font_path = r"simhei.ttf"
if os.path.exists(chinese_font_path):
    from matplotlib.font_manager import FontProperties
    font = FontProperties(fname=chinese_font_path, size=24)
    has_chinese_font = True

def candlestick(ax, opens, highs, lows, closes, width=4, colorup='g', colordown='r', alpha=0.75, ):
    "畫 K 線圖"

    delta = width / 2.

    # 中間的 Box
    barVerts = [((i - delta, open),
                 (i - delta, close),
                 (i + delta, close),
                 (i + delta, open))
                for i, open, close in zip(range(len(opens)), opens, closes)]

    # 下影線
    downSegments = [((i, low), (i, min(open, close)))
                     for i, low, high, open, close in zip(range(len(lows)), lows, highs, opens, closes)]

    # 上影線
    upSegments = [((i, max(open, close)), (i, high))
                     for i, low, high, open, close in zip(range(len(lows)), lows, highs, opens, closes)]

    rangeSegments = upSegments + downSegments

    r, g, b = colorConverter.to_rgb(colorup)
    colorup = r, g, b, alpha
    r, g, b = colorConverter.to_rgb(colordown)
    colordown = r, g, b, alpha
    colord = {True: colorup,
              False: colordown,
              }
    colors = [colord[open < close] for open, close in zip(opens, closes)]

    useAA = 0,  # use tuple here
    lw = 0.5,   # and here
    rangeCollection = LineCollection(rangeSegments,
                                     colors=((0, 0, 0, 1), ),
                                     linewidths=lw,
                                     antialiaseds=useAA,
                                     )

    barCollection = PolyCollection(barVerts,
                                   facecolors=colors,
                                   edgecolors=((0, 0, 0, 1), ),
                                   antialiaseds=useAA,
                                   linewidths=lw,
                                   )

    minx, maxx = 0, len(rangeSegments) / 2
    miny = min([low for low in lows])
    maxy = max([high for high in highs])

    corners = (minx, miny), (maxx, maxy)
    ax.update_datalim(corners)
    ax.autoscale_view()

    # add these last
    ax.add_collection(rangeCollection)
    ax.add_collection(barCollection)

    return rangeCollection, barCollection


def volume_overlay(ax, opens, closes, volumes, colorup='g', colordown='r', width=4, alpha=1.0):
    """Add a volume overlay to the current axes.  The opens and closes
    are used to determine the color of the bar.  -1 is missing.  If a
    value is missing on one it must be missing on all

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    opens : sequence
        a sequence of opens
    closes : sequence
        a sequence of closes
    volumes : sequence
        a sequence of volumes
    width : int
        the bar width in points
    colorup : color
        the color of the lines where close >= open
    colordown : color
        the color of the lines where close <  open
    alpha : float
        bar transparency

    Returns
    -------
    ret : `barCollection`
        The `barrCollection` added to the axes

    """

    colorup = mcolors.to_rgba(colorup, alpha)
    colordown = mcolors.to_rgba(colordown, alpha)
    colord = {True: colorup, False: colordown}
    colors = [colord[open < close]
              for open, close in zip(opens, closes)
              if open != -1 and close != -1]

    delta = width / 2.
    bars = [((i - delta, 0), (i - delta, v), (i + delta, v), (i + delta, 0))
            for i, v in enumerate(volumes)
            if v != -1]

    barCollection = PolyCollection(bars,
                                   facecolors=colors,
                                   edgecolors=((0, 0, 0, 1), ),
                                   antialiaseds=(0,),
                                   linewidths=(0.5,),
                                   )

    ax.add_collection(barCollection)
    corners = (0, 0), (len(bars), max(volumes))
    ax.update_datalim(corners)
    ax.autoscale_view()

    # add these last
    return barCollection


def millions(x, pos):
    'The two args are the value and tick position'
    return '%1.1fM' % (x*1e-6)


def thousands(x, pos):
    'The two args are the value and tick position'
    return '%1.1fK' % (x*1e-3)


def getListOfDates(startdate, enddate):
    "取得資料裡面的月份的第一天"
    dates = [datetime.date(m//12, m%12+1, 1) for m in range(startdate.year*12+startdate.month-1, enddate.year*12+enddate.month)]
    return np.array(dates)


def getDateIndex(dates, tickdates):
    "找出最接近 tickdate 的日期的 index"
    index = [bisect.bisect_left(dates, tickdate) for tickdate in tickdates]
    return np.array(index)


def getMonthNames(dates, index):
    "取得 X 軸上面日期的表示方式"
    names = []
    for i in index:
        if i==0:
            if dates[i].day > 15:
                names.append("")
            else:
                names.append(dates[i].strftime("%b'%y"))
        else:
            names.append(dates[i].strftime("%b'%y"))

    return np.array(names)


class Cursor(object):
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='lightgray')  # the horiz line
        self.ly = ax.axvline(color='lightgray')  # the vert line

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        plt.draw()


def draw_price_ta(ax0, df):
    df['ma05'] = pd.Series.rolling(df['Close'], window=5).mean()
    df['ma20'] = pd.Series.rolling(df['Close'], window=20).mean()
    ax0.plot(df['ma05'].values, color='m', lw=2, label='MA (5)')
    ax0.plot(df['ma20'].values, color='blue', lw=2, label='MA (20)')


def draw_volume_ta(ax1, df):
    pass


def draw(df, title="", colorup='g', colordown='r', save=False):
    # 畫出價量曲線

    # 檢查實際讀到的日期
    if not 'Date' in df.columns:
        df['Date'] = df.index.date

    startdate = df.index.date[0]
    enddate = df.index.date[-1]

    def format_coord1(x, y):
        "用來顯示股價相關資訊"
        try:
            index = int(x+0.5)
            if index < 0 or index >= len(df.Date):
                return ""
            else:
                return 'x=%s, y=%1.1f, price=%1.1f' % (df.Date[int(x+0.5)], y, df.Close[int(x+0.5)])
        except Exception as e:
            print(e.args)
            return ''


    def format_coord2(x, y):
        "用來顯示 Volume 的相關資訊"
        try:
            index = int(x+0.5)
            if index < 0 or index >= len(df.Date):
                return ""
            else:
                return 'x=%s, y=%1.1fM, volume=%1.1fM' % (df.Date[int(x+0.5)], y*1e-6, df.Volume[int(x+0.5)]*1e-6)
        except Exception as e:
            print(e.args)
            return ''

    # 如果沒有讀到任何股價，就跳出程式
    if df.empty:
        raise SystemExit

    tickdates = getListOfDates(startdate, enddate)
    tickindex = getDateIndex(df.Date, tickdates)
    ticknames = getMonthNames(df.Date, tickindex)

    millionformatter = FuncFormatter(millions)
    thousandformatter = FuncFormatter(thousands)

    fig = plt.figure(figsize=(10, 8))
    fig.subplots_adjust(bottom=0.1)
    fig.subplots_adjust(hspace=0)
    if has_chinese_font:
        fig.suptitle(title, fontsize=24, fontweight='bold', fontproperties=font)
    else:
        fig.suptitle(title, fontsize=24, fontweight='bold')

    gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])

    ax0 = plt.subplot(gs[0])
    candles = candlestick(ax0, df.Open, df.High, df.Low, df.Close, width=1, colorup=colorup, colordown=colordown)

    last_price = "Date:{}, Open:{}, High:{}, Low:{}, Close:{}, Volume:{}".format(df.Date[-1], df.Open[-1], df.High[-1], df.Low[-1], df.Close[-1], df.Volume[-1])
    #ax0.text(0.99, 0.97, last_price, horizontalalignment='right', verticalalignment='bottom', transform=ax0.transAxes)

    draw_price_ta(ax0, df)

    ax0.set_xticks(tickindex)
    ax0.set_xticklabels(ticknames)
    ax0.format_coord=format_coord1
    ax0.legend(loc='upper left', shadow=True, fancybox=True)
    ax0.set_ylabel('Price($)', fontsize=16)
    ax0.set_title(last_price, fontsize=10, loc='right')
    ax0.grid(True)

    ax1 = plt.subplot(gs[1], sharex=ax0)
    vc = volume_overlay(ax1, df.Open, df.Close, df.Volume, colorup=colorup, colordown=colordown, width=1)

    ax1.set_xticks(tickindex)
    ax1.set_xticklabels(ticknames)
    ax1.format_coord=format_coord2

    ax1.tick_params(axis='x',direction='out',length=5)
    ax1.yaxis.set_major_formatter(millionformatter)
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position("right")
    ax1.set_ylabel('Volume', fontsize=16)
    ax1.grid(True)

    plt.setp(ax0.get_xticklabels(), visible=False)

    cursor0 = Cursor(ax0)
    cursor1 = Cursor(ax1)
    plt.connect('motion_notify_event', cursor0.mouse_move)
    plt.connect('motion_notify_event', cursor1.mouse_move)

    # 使用 cursor 的時候，如果沒有設定上下限，圖形的上下限會跑掉
    yh = df.High.max()
    yl = df.Low.min()
    ax0.set_ylim(yl - (yh-yl)/20.0, yh + (yh-yl)/20.0)
    ax0.set_xlim(0, len(df.Date)-1)

    if save:
        plt.savefig("{}.png".format(title))
        plt.close()
    else:
        plt.show()


def main():

    symbol = "2330"
    df = get_data_months(symbol, months=3)
    df = df.rename(columns={'成交股數':'Volume', '成交金額':'Volume1', '成交筆數':'Volume2',
        '開盤價':'Open', '收盤價':'Close', '最高價':'High', '最低價':'Low'})
    draw(df, title="台積電", save=True)


if __name__=="__main__":
    main()
