from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from logger import SmoothValue

###################################################################################################
# Note set params with {'q' : 'author:' + authorname} to parse the articles form specify author   #
###################################################################################################

FORUM = 'Gossiping'

class PTT:

    def __init__(
        self,
        forum='Gossiping',
        num_pages=1,
        headers={},
        params={},
        txt_path = 'logger.txt',
    ):

        self.forum = forum
        self.headers = headers
        self.params = params
        self.num_pages = num_pages
        self.parse_info = []
        self.txt_path = txt_path
        SmoothValue.setting(file_path=self.txt_path)

    def fetch(self):

        if bool(self.params):
            self.params['page'] = 1
            idx = list(range(1, self.num_pages + 1))
            list(map(self._fetch_kw, idx))
        else:
            self.params['page'] = 0
            self.params['q'] = ''
            idx = self.parse_newest_index()
            idx = list(range(idx - self.num_pages + 1, idx + 1))
            idx.reverse()
            list(map(self._fetch_forum, idx))
        
        SmoothValue.durationTime()
        SmoothValue.info(
            forum=self.forum, 
            keyword=self.params['q'],
            pages=self.num_pages,
            save_path=self.txt_path,
            )
        SmoothValue.writeInfo()
        
    def _fetch_forum(self, idx):

        url = f'https://www.ptt.cc/bbs/{self.forum}/index{idx}.html'
        ent = self.get_article_info(
            url=url,
            headers=self.headers,
            params=self.params,
            )
        self.params['page'] = self.params['page'] + 1
        for e in ent:
            try:
                ent_info = self.ent2info(e, self.forum)
                info = self.parse_ent_content(ent_info, self.headers, self.params)
                self.parse_info.append(info)
                SmoothValue.addCallback('success', self.params['page'])
            except:
                SmoothValue.addCallback('fail', self.params['page'])

    def _fetch_kw(self, page):

        url = f'https://www.ptt.cc/bbs/{self.forum}/search?'
        self.params['page'] = page
        ent = self.get_article_info(url=url, headers=self.headers, params=self.params)
        for e in ent:
            try:
                ent_info = self.ent2info(e, self.forum)
                info = self.parse_ent_content(ent_info, self.headers, self.params)
                self.parse_info.append(info)
                SmoothValue.addCallback('success', page)
            except:
                SmoothValue.addCallback('fail', page)

    def parse_newest_index(self):

        url = f'https://www.ptt.cc/bbs/{self.forum}/index.html'

        r = requests.get(
            url=url,
            headers=self.headers,
            params=self.params,
            cookies={'over18': '1'}
        )
        doc = BeautifulSoup(r.text, features="lxml")
        newest_anchor = doc.find_all("a", {"class": "btn"})[-3].get('href')
        index = re.findall(r"\d+", newest_anchor)[0]

        return int(index) + 1

    def to_csv(self, save_path=None):
        import pandas as pd
        df_list = []
        try:
            for dct in self.parse_info:
                df = pd.DataFrame(dct, index=[0])
                df_list.append(df)
            df = pd.concat(df_list)
        except:
            SmoothValue.error()
        if save_path is not None:
            df.to_csv(save_path)
            SmoothValue.info(save_path=save_path)
        else:
            df.to_csv(f'ptt_{self.forum}.csv')
            SmoothValue.info(save_path=f'ptt_{self.forum}.csv')

    def to_xlsx(self, save_path=None):
        import openpyxl
        wb = openpyxl.Workbook()
        titles = ['title', 'url', 'author', 'date', 'recommand', 'content']
        ws = wb.active
        ws.append(titles)
        try:
            for dct in self.parse_info:
                l = []
                for title in titles:
                    l.append(dct[title])
                ws.append(l)
        except:
            SmoothValue.error()
        if save_path is not None:
            wb.save(save_path)
            SmoothValue.info(save_path=save_path)
        else:
            wb.save(f'ptt_{self.forum}.xlsx')
            SmoothValue.info(save_path=f'ptt_{self.forum}.xlsx')

    @staticmethod
    def content_cleaner(content):
        
        text = content.split('--')[0]
        text = text.split('\n')[2:]
        text = '\n'.join(text)
        text = re.sub('[^\w\s]','', text)

        return text \
            .replace('\n', '').replace('\t', '') \
            .replace('[', '').replace(']', '')  \
            .replace('>>', '').replace('<<', '')

    @staticmethod
    def ent2info(ent, forum=None):

        info_dict = {
            'title': ent.find('a', href=re.compile(f"^/bbs/{forum}/M")).text,
            'url': 'https://www.ptt.cc' + ent.find('a', href=re.compile(f"^/bbs/{forum}/M")).get('href'),
            'author': ent.find('div', {'class': 'author'}).text,
            'date': ent.find('div', {'class': 'date'}).text,
            'recommand': ent.find('div', {'class': 'nrec'}).text,
        }

        return info_dict

    def parse_ent_content(self, ent_dict, headers=None, params=None):

        url = ent_dict['url']
        r = requests.get(
            url=url,
            headers=headers,
            params=params,
            cookies={'over18': '1'}
        )
        doc = BeautifulSoup(r.text, 'html.parser')
        ent = doc.find(id='main-container')
        ent_dict['content'] = self.content_cleaner(ent.text)

        return ent_dict

    @staticmethod    
    def get_article_info(url, headers, params):

        r = requests.get(
            url=url,
            headers=headers,
            params=params,
            cookies={'over18': '1'}
        )
        doc = BeautifulSoup(r.text, 'html.parser')
        ent = doc.find_all('div', class_='r-ent')

        return ent