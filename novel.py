__author__ = 'zhongjr'

import os
import requests
from bs4 import BeautifulSoup as bs
import re # 正则表达式
import textwrap
import time
import random
import urllib


class Novel(object):
    def __init__(self, novelname, bgnchapter, endchapter, vipcookie):
        userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        # userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0'

        self.novelname = novelname
        self.bgnchapter = bgnchapter
        self.endchapter = endchapter
        self.vipcookie = vipcookie
        self.vipheader = {
            'Cookie': vipcookie,  # vip 章节的 cookie 和登录的 cookie 不一样
            'Host': 'my.jjwxc.net',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': userAgent,
        }

    # 发起请求
    def get_url(self, url, headers=''):
        res = requests.get(url, headers=headers) # 获取 response
        res.encoding = 'gb18030' # 解决中文乱码
        soup = bs(res.text, 'lxml')
        # soup = bs(res.text, 'html.parser') # lxml 解析器缓存不够造成内容丢失，换成 html.parser，但是又会造成作者有话说在前面的时候作话和正文解析不出来
        # print(res.text)
        return soup

    # 根据名称获取小说主页 url
    def get_novelurl(self):
        searchurl = 'http://www.jjwxc.net/search.php?kw=' + urllib.parse.quote(self.novelname, encoding='gb18030') + '&t=1' # 将中文转成 utf-8 编码， 以 % 开头，解码是 unquote
        soup = self.get_url(searchurl)
        novelurl = soup.select('div#search_result a')[0].get('href')

        if novelurl != '':
            print(self.novelname + ':', novelurl)
        else:
            print(self.novelname + ':', 'can\'t find this book.')
        return novelurl

    # 循环获取两个标签中间的内容
    def loop_tags(self, result, bgntag, endtag):
        if bgntag.next.strip() != '': # 这里必须是next，改成text不行，不懂为什么，但是可以正常拿到全部文本
            result += '    '
            result += bgntag.next.strip()
            result += '\n\n'
        # print('result:', result)
        # print(bgntag.next.strip()) # 这个 next 已经是标签里面的文本了，不是标签
        if bgntag.next.next == endtag: # 为什么要两个next？
            # print('1')
            return result
        else:
            # print('2')
            return self.loop_tags(result, bgntag.next.next, endtag)

    # 循环获取标签内所有内容
    def loop_tag(self, tartag):
        result = ''
        for tag in tartag.strings:
            tag = tag.replace('@无限好文，尽在晋江文学城', '') # 替换干扰文本
            if len(tag.lstrip().rstrip()) != 0: # 空行不保留
                result += '    ' + tag.lstrip().rstrip() + '\n\n'
            # print(tag)
            # 这个 tag 是 NavigableString 类型的，跟上面的 bgntag 类型不一样 ，所以要用 string，不能用 text
            # 可能是因为上面是兄弟标签，这里是内部标签？
            # 使用 div.string 需要这样的条件：div 标签里面有且仅有一个内容。如果 div 标签或者其子标签也有内容，则可以使用 div.strings，其返回 generator，需要 for 循环迭代出来
        return result

    # 章节内容格式化
    # 由于不用再循环替换章节文本，此方法可以作废
    def format_text(self, text):
        newtext = ''
        # 逐行删除空行
        # print("".join([s for s in mystr.splitlines(True) if s.strip()]))
        # 先用空行拆分字符再删除
        for line in text.splitlines():
            if len(line.lstrip()) != 0:
                newtext += '    ' + line.lstrip() + '\n\n' # 删除开头的空格

        return newtext

    # 获取每个章节文字内容
    def get_text(self, chapter):
        if chapter['isvip'] == False:
            soup = self.get_url(chapter['url'])
        else:
            soup = self.get_url(chapter['url'], headers=self.vipheader) # vip 章节请求的时候带上 header

        # novel = soup.select('div[class="noveltext"]')[0].text # 返回 noveltext 标签中的所有内容，这个内容太杂，需要再处理
        # return re_text(novel) # 返回正则匹配的结果，这个正则返回的结果不对

        # 方法一，可以实现，但是部分有作话的章节获取不到内容
        # bgntag = soup.select('div[class="noveltext"] div[style="clear:both;"]')[0]
        # endtag = soup.select('div[class="noveltext"] div#favoriteshow_3')[0]
        # novel = loop_tags('', bgntag, endtag)

        # 方法二，换一个 endtag 有作话的章节依然不行，两个 tag 都是 clear 的话全部内容都取不出来
        # bgntag = soup.select('div[class="noveltext"] div[style="clear:both;"]')[0]
        # endtag = soup.select('div[class="noveltext"] div[style="clear: both;"]')[0]
        # print(bgntag)
        # novel = loop_tags('', bgntag, endtag)

        # 方法三，循环单个标签，1、会有前面的一些不需要的字符 2、中间的内容没有用标签包起来，导致不能调整格式（可能方法二不行就是因为这个原因）
        # noveltext = bs(str(soup.select('div[class="noveltext"]')[0]).replace('<b>', ''), 'lxml')
        # print(bs(str(soup.select('div[class="noveltext"]')[0]).replace('<b>', ''), 'lxml').strings) # 输出在前面可以，后面不行，可能这个函数无法正常返回，直接取这个标签的文本算了，不要搞这么麻烦
        # novel = loop_tag('', noveltext)

        # 获取章节内容后面的作者有话说
        # 必须放在获取章节文本前面，extract() 方法会导致获取 readsmall 标签失败
        auwords_pre = ''
        auwords_lst = ''
        readsmall_1 = ''
        readsmall_2 = ''
        # 如果写了异常处理的代码，即使 try 这段报错，也会继续执行下去，不会中断
        try:
            # 章节前面的作者有话说
            readsmall_1 = soup.select('div[class="noveltext"] div#show')[0].find_next_sibling('div', attrs={'class': 'readsmall'})
            if readsmall_1:
                auwords_pre = self.loop_tag(readsmall_1)
                auwords_pre = auwords_pre + '    ----' + '\n\n'
                # print(readsmall_1)
        except Exception as e:
            print(e) # 如果这章没有前面的作话，会报错list index out of range，但是上面已经写了if了，不知道哪里出了问题，如果不想它报错可以把e去掉

        try:
            # 章节后面的作者有话说
            readsmall_2 = soup.select('div[class="noveltext"] div#favoriteshow_3')[0].find_next_sibling('div', attrs={'class': 'readsmall'}) # 应该是这句报错，如果不获取上面的正文，就不会报错，可能跟 soup 有关
            if readsmall_2:
                auwords_lst = self.loop_tag(readsmall_2)
                auwords_lst = '    ----' + '\n\n' + auwords_lst
                # print(readsmall_2)
        except Exception as e:
            print(e)

        # 如果两个作话取出来是一样的，说明只有后一个作话，将前一个置为空
        if readsmall_1 == readsmall_2:
            auwords_pre = ''

        # 方法四，直接取noveltext的文本
        noveltext = soup.select('div[class="noveltext"]')[0]
        [s.extract() for s in noveltext(['script', 'div'])]  # 将标签中的子标签移除（传入 list 移除多个标签）
        novel = self.loop_tag(noveltext)
        # novel = format_text(novel)

        novel = auwords_pre + novel + auwords_lst
        return novel

    # 获取小说简介
    def get_novelinfo(self, novelurl):
        soup = self.get_url(novelurl)
        title = soup.select('span[itemprop="articleSection"]')[0].text # select 返回结果是一个list，取返回的第一个元素
        author = soup.select('span[itemprop = "author"]')[0].text
        # novelintro = soup.select('div#novelintro')[0]
        # [s.extract() for s in novelintro('b')] # extract() 去除 b 标签，避免加粗换行，但是这样标签内的内容也去掉了
        # novelintro.b.name = 'nobr' # 修改 b 标签为 nobr，只能修改第一个
        novelintro = bs(str(soup.select('div#novelintro')[0]).replace('<b>', ''), 'lxml') # 先将标签树变成文本去掉 b 标签，再重新构造为标签树，避免该标签导致换行
        # print(novelintro)
        summary = self.loop_tag(novelintro)
        novelinfo = {
            'title': title,
            'author': author,
            'summary': summary
        }

        if novelinfo:
            print('get novelinfo successfully.')
        else:
            print('get novelinfo failed.')

        return novelinfo

    def get_article(self, novelurl):
        # 获取小说全部章节标题和链接，以字典形式存入列表
        soup = self.get_url(novelurl)
        chapters = soup.select('tr[itemprop*="chapter"]')
        article = []

        for tr in chapters:
            # 非 vip 章节
            if len(tr.select('a[itemprop="url"]')) > 0 and len(tr.select('a[style="cursor:pointer"]')) <= 0:
                title = tr.select('a[itemprop="url"]')[0].text # text 可以用 .text 获取，但是 href 只能用 get 方法获取（标签属性）
                url = tr.select('a[itemprop="url"]')[0].get('href')
                lastModify = tr.select('td')[5].find_next('span').text.lstrip().rstrip()
                isvip = False

            # vip 章节
            if len(tr.select('a[itemprop="url"]')) > 0 and len(tr.select('a[style="cursor:pointer"]')) > 0:
                title = tr.select('a[itemprop="url"]')[0].text # + tr.select('a')[1].text  # 加上 [VIP] 标志
                url = tr.select('a[itemprop="url"]')[0].get('rel')[0] # 不知道为什么返回的是个 list
                lastModify = tr.select('td')[4].find_next('span').text.lstrip().rstrip()
                isvip = True

            summary = tr.select('td')[2].text.strip()  # 章节简介，2表示第三个td标签
            num = tr.select('td')[0].text.strip()
            wordCount = tr.select('td[itemprop="wordCount"]')[0].text.strip()

            try:
                data = {
                    'title': title,
                    'url': url,
                    'summary': summary,
                    'num': num,
                    'wordCount': wordCount,
                    'lastModify': lastModify,
                    'isvip': isvip
                }
                article.append(data)
            except:
                pass

        if len(article) > 0:
            print('get chapters successfully,', len(article), 'chapters totally.')
        else:
            print('get chapters failed.')

        return article

    def write_file(self, novelinfo, article):
        desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
        filepath = desktop + '\\' + novelinfo['title'] + '.txt'
        print('filepath:', filepath)
        print('start writing in...')

        with open(filepath, mode='w+', encoding='gb18030') as f: # 先打开文件再进入循环，每次写入覆盖文件（如果文件不存在则先创建）
            f.write('    ' + novelinfo['title'] + '\n\n')
            f.write('    ' + '作者：' + novelinfo['author'] + '\n\n')
            f.write(novelinfo['summary'] + '\n')

            for chapter in article[(self.bgnchapter-1 if self.bgnchapter else None):self.endchapter]: # 写入本地 txt，列表可以切片选择部分章节
                try:
                    chaptertext = self.get_text(chapter) # 这个函数没有处理异常，vip 章节读取从这里开始出错，后面都不会执行
                    print(chapter['num'], chapter['title'], '[VIP]' if chapter['isvip'] == True else '', chapter['summary'], chapter['url'], '字数:', chapter['wordCount'], '最近修改时间:', chapter['lastModify'])
                    print('(章节内容为空)') if chaptertext == '' else ''
                    f.write('    第' + chapter['num'] + '章 ' + chapter['title'] + '\n\n') # 空格的转义字符是 \000 (Windows)
                    f.write(chaptertext + '\n')
                    time.sleep(random.uniform(2, 5)) # 暂时挂起
                except:
                    pass

        print('write done.')

    def get_novel(self):
        novelurl = self.get_novelurl()
        novelinfo = self.get_novelinfo(novelurl)
        article = self.get_article(novelurl)
        self.write_file(novelinfo, article)

    # 正则匹配小说内容
    def re_text(text):
        pattern = r'晋江原创网 @\u3000\u3000([\u4e00-\u9fa5][^0-9a-z\s]*)'
        return ''.join(re.findall(pattern, text))
