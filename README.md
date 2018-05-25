# 用 Python 做股票分析

在本次的課程中，我們會教大家使用 Python 做股票分析。內容會含括：

* Numpy, MatPlotLib, Pandas 的簡單使用技巧。
* 使用爬蟲抓取股價歷史資料、財報資料等。
* 實作選股法則。
* 實作投資策略。
* 利用回測來評估策略的好壞。
* 從無到有建構出自己的股票分析系統。

在課程中我們預計會使用到 Anaconda (Python 懶人包) 及 Visual Studio Code (編輯器)，可以的話請大家先下載及安裝。

### 下方連結為上課所使用的軟體 (請預先下載至筆電)：

* [Anaconda 下載網址](https://www.anaconda.com/download/)
  * [Anaconda 安裝教學](https://goo.gl/68rgcv)
* [Visual Studio Code 下載網址](https://code.visualstudio.com/)

如果不知道怎麼使用 Anaconda 來安裝 Python，可以操考這一個 [影片教學](https://bit.ly/2IJiW1b)。

如果之前沒有安裝過 Pyhton，請在安裝時將"Add Anaconda to my PATH environment variable" 選項打勾，這樣在命令列上才可以找到相關執行檔的路徑。

新版的 Anaconda 安裝檔在安裝時會提示您要不要安裝 "Visual Studio Code"，您可以選擇從 Anaconda 的安裝檔裡面直接安裝 Visual Studio Code，這樣就不用另外下載 Visual Studio Code 來安裝了。

### 在教學過程中，大家可能會遇到問題的套件

#### pandas-datareader 的安裝

理論上，我們已經不需要使用 pandas-datareader，因為 pandas-datareader 已經不再支援 yahoo finance，而且對於 google finance 也有可能隨時不支援。但是，因為 ffn 會使用到 pandas-datareader，所以還是要安裝一個可以使用的 pandas-datareader。

由於 pandas 改版的關係，有一些 API 的位置變了，所以如果要讓 pandas-datareader 可以跑，必須安裝 dev 版的 pandas-datareader，安裝方法如下：

```python
pip install git+https://github.com/pydata/pandas-datareader.git
```

請參閱：[pandas-datareader官網說明文件](https://pandas-datareader.readthedocs.io/en/latest/#install-latest-development-version)

#### talib 的安裝

欲在 windows 上安裝 talib，請直接至[Unofficial Windows Binaries for Python Extension Packages](Unofficial Windows Binaries for Python Extension Packages)下載對應的 .whl 檔回來安裝。
