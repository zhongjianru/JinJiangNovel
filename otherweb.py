# Time : 2020-04-06 23:03

# Author : zhongjr

# File : otherweb.py

# Purpose: 晋江部分章节被锁，从其他网站获取章节内容

import os
import re
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


# 递归调用
def rec_text(text):

    # author = 'Christian Böhm (Ludwig-Maximilians-Universität München)'  # 处理后只留下前面的作者名，括号内容去掉
    # pattern = re.compile('.*(\(.*\))')  # 对括号进行转义，避免 Python 认为是在添加子块
    pattern = re.compile('.*(\(((w|W|ｗ).*(c|o|m|C|O|M|ｍ)|(看啦又看).*)\))')  # 指定 w 开头 m 结尾的字符串
    match = re.match(pattern=pattern, string=text)

    if match:

        temp = match.group(0)  # 原字符串
        result = re.sub(pattern='\(' + match.group(1) + '\)', repl='', string=text)  # 将匹配到的字符串替换掉
        return rec_text(result)  # 递归调用，每次去除一处干扰字符，要写 return

    else:

        return text  # 如果不需要再继续处理，返回原字符串


def re_text(text):
    pattern = re.compile('\(((w|W|ｗ).*(c|o|m|C|O|M|ｍ)|(看啦又看).*)\)')  # 跟上面的pattern不一样
    result = re.sub(pattern=pattern, string=text, repl='')
    return result


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
                line = line.replace('　　', '\n\n    ').lstrip()  # 作话换行
                line = re_text(line)  # 替换干扰文本
                text = text + '    ' + line + '\n\n'

            f.write(text)

        print('write down.')


if __name__ == '__main__':
    url = 'http://www.k6uk.com/novel/59/59990/'
    novelname = '同桌那个坏同学'
    author = '福禄丸子'
    get_novel(url, novelname, author)
