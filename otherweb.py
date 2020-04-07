# Time : 2020-04-06 23:03

# Author : zhongjr

# File : otherweb.py

# Purpose: 晋江部分章节被锁，从其他网站获取章节内容

import os
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


def get_url(url):
    location = os.getcwd() + '/fake_useragent.json'
    headers = {'user-agent': UserAgent(path=location).random}
    # soup = ''

    try:

        res = requests.get(url, headers=headers)
        res.encoding = 'gb18030'
        soup = bs(res.text, 'lxml')
        return soup

    except Exception as e:

        print('get url failed.')
        print('Exception:', e)
        return


def get_novel(url, novelname, author):

    chapters = get_url(url).select('td.ccss a')  # 所有章节的 a 标签
    article = []

    filepath = os.getcwd() + '/' + novelname + '.txt'

    for tr in chapters:

        href = url + tr.get('href')
        title = tr.text

        data = {
            'href': href,
            'title': title
        }

        article.append(data)

    with open(filepath, mode='w+', encoding='utf-8') as f:

        print('writing...')

        f.write('    ' + novelname + '\n\n')
        f.write('    ' + '作者：' + author + '\n\n')

        # text = ''
        # 循环获取章节文本
        for ar in article:

            text = '    ' + ar['title'] + '\n\n'

            chapter = get_url(ar['href'])
            lines = chapter.select('div#content')[0]
            for line in lines.strings:
                line = line.replace('　　', '\n\n    ').lstrip()  # 作话换行，还没替换干扰文本
                text = text + '    ' + line + '\n\n'

            f.write(text)

        print('write down.')


if __name__ == '__main__':
    url = 'http://www.k6uk.com/novel/59/59990/'
    novelname = '同桌那个坏同学'
    author = '福禄丸子'
    get_novel(url, novelname, author)
