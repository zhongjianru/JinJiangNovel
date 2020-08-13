import re
import requests
from bs4 import BeautifulSoup as bs


# 构造请求头
def get_headers(cookies=''):
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    headers = {
        'Cookie': cookies,
        'Host': 'my.jjwxc.net',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': userAgent
    }
    return headers


# 发起请求
def get_url(url, headers=''):
    res = requests.get(url, headers=headers, allow_redirects=False)
    res.encoding = 'gb18030'
    soup = bs(res.text, 'lxml')
    return soup


# 循环获取两个标签中间的内容
def loop_tags(result, bgntag, endtag):
    if bgntag.next.strip() != '':
        result += '    '
        result += bgntag.next.strip()
        result += '\n\n'
    if bgntag.next.next == endtag:
        return result
    else:
        return loop_tags(result, bgntag.next.next, endtag)


# 循环获取标签内所有内容
def loop_tag(tartag):
    result = ''
    for tag in tartag.strings:
        tag = tag.replace('@无限好文，尽在晋江文学城', '')
        if len(tag.lstrip().rstrip()) != 0:
            result += '    ' + tag.lstrip().rstrip() + '\n\n'
    return result


# 替换干扰内容
def re_text(text, pattern):
    pattern = re.compile(pattern)
    result = re.sub(pattern=pattern, string=text, repl='')
    return result

