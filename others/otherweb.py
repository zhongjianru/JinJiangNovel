# Time : 2020-04-06 23:03

# Author : zhongjr

# File : otherweb.py

# Purpose: 晋江部分章节被锁，从其他网站获取章节内容

from main import utils
import os
import re
import requests
from bs4 import BeautifulSoup as bs
import time


def get_url(url, encording):

    # location = os.getcwd() + '/fake_useragent.json'
    # headers = {'User-Agent': UserAgent(path=location).random, 'Accept-Language': 'zh-CN,zh;q=0.9'}
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Connection': 'keep-alive',
        # 'Host': 'api.share.baidu.com',
        # 'Referer': 'http://www.biquge.tv/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }

    try:
        print('getting url:', url)
        res = requests.get(url, headers=headers)
        res.encoding = encording
        soup = bs(res.text, 'lxml')
        return soup

    except:
        pass


def get_novel(url, encording, novelname, author):
    chapters = get_url(url, encording).select('div.mb20 div.info-chapters a')  # 所有章节的 a 标签
    article = []
    filepath = 'novel/' + novelname + '.txt'

    for tr in chapters[:]:
        href = tr.get('href')
        title = tr.text
        data = {
            'href': href,
            'title': title
        }
        article.append(data)

    with open(filepath, mode='w+', encoding=encording) as f:
        print('start writing...')
        f.write('    ' + novelname + '\n\n')
        f.write('    ' + '作者：' + author + '\n\n')

        # text = ''
        # 循环获取章节文本
        for pt in article:
            print('writing:', pt)
            text = '    ' + pt['title'] + '\n\n'
            content = ''
            chapter_url = pt['href']
            try:
                chapter = get_url(chapter_url, encording)
                content = chapter.select('article.content')[0]
                content = utils.loop_tag(content)
            except:
                pass

            text = text + content\
                .replace(' ', '')\
                .replace(', ', '，')\
                .replace(',', '，')\
                .replace('    内容未完，下一页继续阅读\n\n', '')\
                .replace('    【本章阅读完毕，更多请搜索笔趣阁;https://www.xp7000.com 阅读更多精彩小说】\n\n', '')

            f.write(text)
            time.sleep(2)  # 暂时挂起

        print('write down.')


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


if __name__ == '__main__':
    url = 'http://www.5izhenjiang.com/155_155109/'
    encording = 'utf-8'
    novelname = '野狗骨头'
    author = '休屠城'
    get_novel(url, encording, novelname, author)
