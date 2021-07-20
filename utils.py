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


# 文本格式化
def re_text(text):
    # 替换多个空格：停用
    # pattern1 = re.compile(r'\s+')
    # text = re.sub(pattern=pattern1, repl=' ', string=text)

    # 匹配中文方案：停用，情况比较多
    # pattern2 = re.compile(r'([\u4e00-\u9fff]+)(\s*)(,)')  # 中文/空格/逗号
    # text = re.findall(pattern=pattern2, string=text)  # 正则匹配结果

    # 匹配英文方案：先将英文逗号全部替换成中文逗号，再还原英文中的逗号
    pattern3 = re.compile(r'(\s*)(,|，)(\s*)')  # 空格/逗号/空格
    text = re.sub(pattern=pattern3, repl='，', string=text)

    # 还原英文标点
    pattern4 = re.compile(r'([a-zA-Z]+)(，)([a-zA-Z]+)')
    text = re.sub(pattern=pattern4, repl=r'\1, \3', string=text)  # \1 代表正则匹配到的第一部分

    return text

