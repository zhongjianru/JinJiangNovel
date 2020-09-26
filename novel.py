__author__ = 'zhongjr'

# 调用层次不是很清晰，建议分为三层，按顺序排列：
# 1、工具函数（utils.py）：包括 get_url、loop_tags、user_login 和 test_cookie，还有去除干扰文字的函数
# 2、中间函数（novel.py）：包括 get_cookie、get_novel_url、get_novelinfo、get_article 和 get_text
# 3、目标函数（main.py） ：get_novel
# 4、函数和变量命名规范（下划线分割，字母小写）

import utils
import time
import random
import urllib
from bs4 import BeautifulSoup as bs


class Novel(object):
    def __init__(self, novel_name, chapter_bgn, chapter_end, cookies):
        userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        # userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0'

        self.novel_name = novel_name
        self.chapter_bgn = chapter_bgn
        self.chapter_end = chapter_end
        self.cookies = cookies
        self.headers = {
            'Cookie': cookies,  # vip 章节的 cookie 和登录的 cookie 不一样
            'Host': 'my.jjwxc.net',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': userAgent,
        }

    # 根据名称获取小说主页 url
    def get_novelurl(self):
        search_url = 'http://www.jjwxc.net/search.php?kw=' + urllib.parse.quote(self.novel_name, encoding='gb18030') + '&t=1' # 将中文转成 utf-8 编码， 以 % 开头，解码是 unquote
        soup = utils.get_url(search_url)
        novel_url = soup.select('div#search_result a')[0].get('href')

        if novel_url != '':
            print(self.novel_name + ':', novel_url)
        else:
            print(self.novel_name + ':', 'can\'t find this book.')
        return novel_url

    # 获取小说简介
    def get_novelinfo(self, novel_url):
        soup = utils.get_url(novel_url)
        title = soup.select('span[itemprop="articleSection"]')[0].text
        author = soup.select('span[itemprop = "author"]')[0].text
        novel_intro = bs(str(soup.select('div#novelintro')[0]).replace('<b>', ''), 'lxml')  # 标签树->文本->标签树，避免该标签导致换行
        summary = utils.loop_tag(novel_intro)
        novel_info = {
            'title': title,
            'author': author,
            'summary': summary
        }

        if novel_info:
            print('get novelinfo successfully.')
        else:
            print('get novelinfo failed.')

        return novel_info

    def get_chapters(self, novel_url):
        # 获取小说全部章节标题和链接，以字典形式存入列表
        soup = utils.get_url(novel_url)
        chapter_list = soup.select('tr[itemprop*="chapter"]')
        chapters = []

        for tr in chapter_list:
            # 判断章节是否被锁
            if tr.select('a[itemprop="url"]'):
                # 非 vip 章节
                if not tr.select('a[style="cursor:pointer"]'):
                    title = tr.select('a[itemprop="url"]')[0].text  # text 可以用 .text 获取，但是 href 只能用 get 方法获取（标签属性）
                    url = tr.select('a[itemprop="url"]')[0].get('href')
                    lastModify = tr.select('td')[5].find_next('span').text.lstrip().rstrip()
                    isvip = False

                # vip 章节
                else:
                    title = tr.select('a[itemprop="url"]')[0].text  # + tr.select('a')[1].text  # 加上 [VIP] 标志
                    url = tr.select('a[itemprop="url"]')[0].get('rel')[0]  # 不知道为什么返回的是个 list
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
                chapters.append(data)
            except:
                pass

        if len(chapters) > 0:
            print('get chapters successfully,', len(chapters), 'chapters totally.')
        else:
            print('get chapters failed.')

        return chapters

    # 获取每个章节文字内容
    def get_noveltext(self, chapter):
        if not chapter['isvip']:
            soup = utils.get_url(chapter['url'])
        else:
            soup = utils.get_url(chapter['url'], headers=self.headers)

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

        # 获取章节内容后面的作话
        # 必须放在获取章节文本前面，extract() 方法会导致获取 readsmall 标签失败
        # 改进：在"作者有话要说："后面加上换行
        auwords_pre = ''
        auwords_lst = ''
        readsmall_1 = ''
        readsmall_2 = ''
        # 如果写了异常处理的代码，即使 try 这段报错，也会继续执行下去，不会中断
        try:
            # 章节前面的作话
            readsmall_1 = soup.select('div[class="noveltext"] div#show')[0].find_next_sibling('div', attrs={'class': 'readsmall'})
            if readsmall_1:
                auwords_pre = utils.loop_tag(readsmall_1)
                auwords_pre = auwords_pre[:11] + '\n\n' + '    ' + auwords_pre[11:]
                auwords_pre = auwords_pre + '    ----' + '\n\n'
        except Exception as e:
            print(e)  # 如果这章没有前面的作话，会报错list index out of range，但是上面已经写了if了，不知道哪里出了问题，如果不想它报错可以把e去掉（因为先赋值了）

        try:
            # 章节后面的作话
            readsmall_2 = soup.select('div[class="noveltext"] div#favoriteshow_3')[0].find_next_sibling('div', attrs={'class': 'readsmall'}) # 应该是这句报错，如果不获取上面的正文，就不会报错，可能跟 soup 有关
            if readsmall_2:
                auwords_lst = utils.loop_tag(readsmall_2)
                auwords_lst = auwords_lst[:11] + '\n\n' + '    ' + auwords_lst[11:]
                auwords_lst = '    ----' + '\n\n' + auwords_lst
        except Exception as e:
            print(e)

        # 如果两个作话取出来是一样的，说明只有后一个作话，将前一个置为空
        if readsmall_1 == readsmall_2:
            auwords_pre = ''

        # 方法四，直接取 noveltext 的文本
        text = soup.select('div[class="noveltext"]')[0]
        [s.extract() for s in text(['script', 'div'])]  # 将标签中的子标签移除（传入 list 移除多个标签）
        novel = utils.loop_tag(text)

        novel_text = auwords_pre + novel + auwords_lst
        return novel_text

    def write_file(self, novel_info, chapters):
        # desktop = os.path.join(os.path.expanduser("~"), 'Desktop')
        # filepath = desktop + '\\' + novelinfo['title'] + '.txt'
        filepath = novel_info['title'] + '.txt'
        print('filepath:', filepath)
        print('start writing in...')

        with open(filepath, mode='w+', encoding='gb18030') as f:  # 先打开文件再进入循环，每次写入覆盖文件（如果文件不存在则先创建）
            f.write('    ' + novel_info['title'] + '\n\n')
            f.write('    ' + '作者：' + novel_info['author'] + '\n\n')
            f.write(novel_info['summary'] + '\n')

            for chapter in chapters[(self.chapter_bgn-1 if self.chapter_bgn else None): self.chapter_end]:  # 切片选择部分章节
                try:
                    chaptertext = self.get_noveltext(chapter)  # 这个函数没有处理异常，vip 章节读取从这里开始出错，后面都不会执行
                    print(chapter['num'], chapter['title'], '[VIP]' if chapter['isvip'] else '', chapter['summary'], chapter['url'], '字数:', chapter['wordCount'], '最近修改时间:', chapter['lastModify'])
                    print('(章节内容为空)') if chaptertext == '' else ''
                    f.write('    第' + chapter['num'] + '章 ' + chapter['title'] + '\n\n')
                    f.write(chaptertext + '\n')
                    time.sleep(random.uniform(2, 5))  # 暂时挂起
                except Exception as e:
                    pass

        print('write done.')

    def get_novel(self):
        novel_url = self.get_novelurl()
        novel_info = self.get_novelinfo(novel_url)
        chapters = self.get_chapters(novel_url)
        self.write_file(novel_info, chapters)


