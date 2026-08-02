# Time : 2024-03-30 23:03

# Author : zhongjr

# File : jj_spider.py

# Purpose: jjwxc

import re
import time
from selenium import webdriver
import novel as nl
import fonttext as ft
import utils

class jj_spider:
    def __init__(self):
        self.novelurl = 'https://www.jjwxc.net/onebook.php?novelid=6797599'
        self.index = 0
        self.chapter_bgn = 190  # 默认 None
        self.chapter_end = None  # 默认 None
        # self.driver = webdriver.Chrome(options=opt)  # 可以在这里定义driver，再在其他函数里使用

    def spider(self):
        # 使用已经打开的窗口进行操作，先在终端执行命令启动 Chrome 登陆好网站账户，再启动该脚本
        # 终端命令：/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/Users/kinyuchung/Downloads/ChromeFiles
        # 下载地址：https://googlechromelabs.github.io/chrome-for-testing/#stable
        driver_path = '/Users/kinyuchung/Downloads/chromedriver'
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('debuggerAddress', '127.0.0.1:9222')  # 比自动登陆多了一个配置项
        driver = webdriver.Chrome(options=opt, executable_path=driver_path)
        driver.get(self.novelurl)
        print(driver.title)
        time.sleep(5)

        novel = nl.Novel('', '', '', '')
        novelinfo = novel.get_novelinfo(self.novelurl)
        chapters = novel.get_chapters(self.novelurl)
        print(novelinfo)
        print(chapters)

        filepath = '../novel/' + novelinfo['title'] + '.txt'
        print('filepath:', filepath)
        print('start writing in...')

        with open(filepath, mode='w+', encoding='gb18030') as f:
            summary = ''
            summary = summary + novel.space + novelinfo['title'] + novel.newline
            summary = summary + novel.space + '作者：' + novelinfo['author'] + novel.newline
            summary = summary + novelinfo['summary'] + novel.newline
            f.write(summary)
            for chapter in chapters[(self.chapter_bgn-1 if self.chapter_bgn else None): self.chapter_end]:
                time.sleep(5)
                print(chapter['num'], chapter['title'], '[VIP]' if chapter['isvip'] else '', chapter['summary'], chapter['url'], '字数:', chapter['wordCount'], '最近修改时间:', chapter['lastModify'])
                driver.get(chapter['url'])

                if chapter['isvip']:
                    # f.write('    第' + chapter['num'] + '章 ' + chapter['title'] + '\n\n')
                    f.write('    ' + chapter['title'] + ' ' + chapter['summary'] + '\n\n')
                    textelement = driver.find_element_by_css_selector('div.novelbody div.noveltext div#paragraph_comment_content div[id*="content"]')
                    chaptertext = textelement.get_attribute('innerHTML')
                    chaptertext = chaptertext.replace('<br>', '\n')

                    # vip 章节有一些隐藏内容在span里面，以下是处理逻辑
                    repldict = []
                    spanelement = textelement.find_elements_by_css_selector('span[class^="c_"]')
                    for span in spanelement:
                        spanclass = span.get_attribute('class')
                        before = driver.execute_script("return window.getComputedStyle(arguments[0], '::before').getPropertyValue('content')", span)
                        after = driver.execute_script("return window.getComputedStyle(arguments[0], '::after').getPropertyValue('content')", span)
                        spandata = {
                            'class': spanclass,
                            'before': (before[1:-1] if before != 'none' else ''),
                            'after': (after[1:-1] if after != 'none' else '')
                        }
                        repldict.append(spandata)

                    def complex_repl(match, bgnpatt, endpatt):
                        self.index += 1
                        matchtext = match.group(0)  # 正则匹配结果
                        repl = re.sub(bgnpatt, repldict[self.index]['before'], matchtext)  # 用before替换标签开头
                        repl = re.sub(endpatt, repldict[self.index]['after'], repl)  # 用after替换标签结尾
                        return repl  # 返回替换后结果

                    # 获取before和after属性里面的内容，按照正则匹配后用index映射按顺序进行替换，正则对应 spanelement，匹配数量对不上就会 index out of range
                    self.index = -1
                    spanbgnpatt = r'<span class="c_(\w){3}">'
                    spanendpatt = r'</span>'
                    spanmidpatt = r'.*?'  # 非贪婪匹配，匹配尽可能短的结果（最近的一个闭合标签）
                    spanpattern = re.compile(spanbgnpatt + spanmidpatt + spanendpatt)
                    chaptertext = re.sub(spanpattern, lambda match: complex_repl(match, spanbgnpatt, spanendpatt), chaptertext)

                    # vip 章节替换混淆字
                    classlist = driver.find_element_by_css_selector('div.novelbody div').get_attribute('class').split()
                    pattern = 'jjwxcfont'
                    fontname = [font for font in classlist if re.search(pattern, font)]
                    fontname = ''.join(fontname)
                    chaptertext = ft.fonttext(chaptertext, fontname)

                # 非 vip 章节
                else:
                    free_title = driver.find_element_by_css_selector('div.noveltext h2').text
                    free_content = driver.find_element_by_css_selector('div#paragraph_comment_content').text
                    chaptertext = free_title + '\n' + free_content

                chaptertext = utils.re_text(chaptertext)  # 最后格式化章节内容：多余的段评等标签在这里处理（测试的时候可以把这行注释掉）
                f.write(chaptertext)
                time.sleep(2)

        print('write down.')
        driver.quit()


if __name__ == '__main__':
    jj_spider = jj_spider()
    jj_spider.spider()
