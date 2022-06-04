import openpyxl
from pandas import NA
import requests
import json
import os
import time
import cloudscraper
import random
import re
from logger import SmoothValue

FORUM = 'stock'

class Dcard:

    def __init__(
        self,
        forum='stock',
        num_article=2,
        headers={},
        params={},
        kw='遠距',
        txt_path = 'logger.txt',
        parse_content = False,
        titles = ['title', 'forumName','school', 'gender', 'commentCount', 'likeCount', 'totalCommentCount', 'topics', 'content']
    ):

        self.forum = forum
        self.kw = kw
        self.headers = headers
        self.params = params
        self.num_article = num_article
        self.count = 0
        self.parse_info = []
        self.txt_path = txt_path
        self.titles = titles
        self.parse_content = parse_content
        self.early_stop_rounds = 0
        SmoothValue.setting(file_path=self.txt_path)

        if self.kw is not None:
            self.parse_content = True

    def fetch(self):

        if self.parse_content:
            if self.kw is not None:
                while self.count < self.num_article:
                    root = self._fetch_kw()
                    self._fetch_content(root)
            else:
                while self.count < self.num_article:
                    root = self._fetch_forum()
                    self._fetch_content(root)
        else:
            self.titles = list(filter(lambda x: x not in ['content', 'excerpt'], self.titles))
            self.titles = self.titles + ['excerpt']
            while self.count < self.num_article:
                if self.early_stop_rounds >= 10:
                    print('Early Stopping!!')
                    break
                try:
                    root = self._fetch_forum()
                    self._fetch_excerpt(root)
                except:
                    self.early_stop_rounds = self.early_stop_rounds + 1
                    SmoothValue.addCallback('fail', self.count)
                    time.sleep(random.randint(2, 6))
  
        SmoothValue.durationTime()
        SmoothValue.info(
            forum=self.forum, 
            keyword=self.kw,
            titles=self.titles,
            num_article=self.num_article,
            save_path=self.txt_path,
        )
        SmoothValue.writeInfo()
        
    def _fetch_forum(self):

        url = f"https://www.dcard.tw/service/api/v2/forums/{self.forum}/posts"
        scraper = cloudscraper.create_scraper()
        try:
            r = scraper.get(url, headers=self.headers, params=self.params)
            root = json.loads(r.text)
            time.sleep(random.randint(2,6))
        except:
            return None

        return root

    def _fetch_kw(self):

        url = f'https://www.dcard.tw/service/api/v2/search/posts?query={self.kw}'
        scraper = cloudscraper.create_scraper()
        try:
            r = scraper.get(url, headers=self.headers, params=self.params)
            root = json.loads(r.text)
            time.sleep(random.randint(2,6))
        except:
            return None

        return root

    def _fetch_content(self, root):

        idx = self.parse_ent_id(root)
        self.params['before'] = idx[-1]
        list(map(self._fetch,idx))

    def _fetch_excerpt(self, root):

        idx = self.parse_ent_id(root)
        self.params['before'] = idx[-1]
        self.parse_info = self.parse_info + root
        self.count = self.count + len(root)
        SmoothValue.addCallback('success', self.count, num_articles=self.params['limit']  if self.params['limit'] <= 100 else 100)

    def _fetch(self, idx):
        url = 'https://www.dcard.tw/_api/posts/' + str(idx)
        scraper = cloudscraper.create_scraper()

        self.count = self.count + 1
        try:
            post = scraper.get(url, headers=self.headers)
            time.sleep(random.randint(2,6))

            postInfo = json.loads(post.text)
            postInfo = dict(filter(lambda x:x[0] in self.titles, postInfo.items()))
            self.parse_info.append(postInfo)

            SmoothValue.addCallback('success', self.count)
        except:
            SmoothValue.addCallback('fail', self.count)

    def parse_ent_id(self, root):
        return [str(post['id']) for post in root]

    def to_csv(self, save_path=None):
        import pandas as pd
        df_list = []
        try:
            for dct in self.parse_info:
                dct = dict(filter(lambda x:x[0] in self.titles, dct.items()))
                for key in dct:
                    dct[key] = str(dct[key])
                df = pd.DataFrame(dct, index=[0])
                df_list.append(df)
            df = pd.concat(df_list)
        except:
            SmoothValue.error()
        if self.parse_content:
            df['content'] = df.apply(lambda x: self.content_cleaner(x['content']), axis=1)
        else:
            df['excerpt'] = df.apply(lambda x: self.content_cleaner(x['excerpt']), axis=1)
        if save_path is not None:
            df.to_csv(save_path)
            SmoothValue.info(save_path=save_path)
        else:
            df.to_csv(f'ptt_{self.forum}.csv')
            SmoothValue.info(save_path=f'ptt_{self.forum}.csv')

    def to_xlsx(self, save_path=None):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(self.titles)
        try:
            for dct in self.parse_info:
                l = []
                for title in self.titles:
                    if title == 'content' or title == 'excerpt':
                        content = self.content_cleaner(str(dct[title]))
                        l.append(content)
                    else:
                        try:
                            l.append(str(dct[title]))
                        except:
                            dct[title] = None
                            l.append(str(dct[title]))
                ws.append(l)
        except:
            SmoothValue.error()
        if save_path is not None:
            wb.save(save_path)
            SmoothValue.info(save_path=save_path)
        else:
            wb.save(f'ptt_{self.forum}.xlsx')
            SmoothValue.info(save_path=f'ptt_{self.forum}.xlsx')

    def content_cleaner(self, text):
        text = re.sub('[^\w\s]','', text)
        return text \
            .replace('\n', '').replace('\t', '') \
            .replace('[', '').replace(']', '')  \
            .replace('>>', '').replace('<<', '')

# params = {
#     'popular' : 'false',
#     'limit' : 100,
# }
# headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

# a = Dcard(params=params, headers=headers, kw=None, num_article=250)

# a.fetch()
# a.to_xlsx()
# a.to_csv()
