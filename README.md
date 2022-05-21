# webParser

這個專案會不定時更新各個網頁的 python 爬取代碼

## PTT

PTT 的網頁沒有什麼反爬機制，所以可以輕鬆的用 requests 模組就爬取到文章
PTT 不支援 API，所以需要用 bs4 去解析 html 

### Usage

```python
git clone https://github.com/DongDong-Zoez/webParser.git
python demo.py
```

### argument

- ```k```: 字串，輸入你要搜尋的關鍵字
- ```f```: 字串，輸入你要搜尋的看板
- ```p```: 字串，logger file 的輸出位置
- ```n```: 整數，輸入你要爬取的頁面數量
- ```a```: 字串，輸入要搜尋的指定作者
- ```l```: 字典，輸入 requests 的 headers
- ```c```: 布林，是否要輸出 csv file
- ```x```: 布林，是否要輸出 xlsx file 
- ```cp```: 字串，輸出 csv file 的位置
- ```xp```: 字串，輸出 xlsx file 的位置

## Dcard

Dcard 使用的是高級的 Cloudflare，我們使用一般的 cloudscraper 沒辦法繞過 dcard 的 Captcha，
所以有時候會有錯誤產生 --> 盡量不要向 dcard 網站發太過頻繁的請求

如果設置 ```-c False``` 則會平均每 4 秒抓 100 篇文章 (僅包含內文簡介)

如果設置 ```-c True``` 則會平均每 4 秒抓 1 篇文章 (包含內文)

### Usage

```python
git clone https://github.com/DongDong-Zoez/webParser.git
python demo.py -c False
```

### argument

- ```f```: 字串，輸入你要搜尋的看板
- ```n```: 整數，輸入你要爬取的文章數量
- ```i```: 字典，輸入 requests 的 headers
- ```p```: 字典，輸入 requests 的 params
- ```w```: 字串，輸入你要搜尋的關鍵字
- ```l```: 字串，logger file 的輸出位置
- ```c```: 布林，是否要爬取整個內文
- ```t```: 列表，輸入你要爬取的 columns
- ```cp```: 字串，輸出 csv file 的位置
- ```xp```: 字串，輸出 xlsx file 的位置
