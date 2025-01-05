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
        self.novelurl = 'https://www.jjwxc.net/onebook.php?novelid=3468506'
        self.index = 0
        self.chapter_bgn = 433  # 默认 None
        self.chapter_end = 440  # 默认 None
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
                    # vip 章节替换混淆内容
                    f.write('    第 ' + chapter['num'] + ' 章 ' + chapter['title'] + '\n\n')
                    repldict = []
                    def complex_repl(match, pos):
                        repl = repldict[self.index][pos]
                        if repl == 'none':
                            repl = ''
                        else:
                            repl = repl[1:-1]  # 文本前后带的双引号去掉
                        self.index += 1
                        return repl
                    textelement = driver.find_element_by_css_selector('div.novelbody div.noveltext div[id*="content"]')
                    spanelement = driver.find_elements_by_css_selector('div.novelbody div.noveltext div[id*="content"] span')
                    chaptertext = textelement.get_attribute('innerHTML')

                    for span in spanelement:
                        spanclass = span.get_attribute('class')
                        before = driver.execute_script("return window.getComputedStyle(arguments[0], '::before').getPropertyValue('content')", span)
                        after = driver.execute_script("return window.getComputedStyle(arguments[0], '::after').getPropertyValue('content')", span)
                        spandata = {
                            'class': spanclass,
                            'before': before,
                            'after': after
                        }
                        repldict.append(spandata)
                    chaptertext = chaptertext.replace('<br>', '\n')
                    self.index = 0
                    chaptertext = re.sub(r'\<span class="(\w+)"\>', lambda match: complex_repl(match, pos='before'), chaptertext)
                    self.index = 0
                    chaptertext = re.sub(r'\</span\>', lambda match: complex_repl(match, pos='after'), chaptertext)

                    # vip 章节替换混淆字
                    classlist = driver.find_element_by_css_selector('div.novelbody div').get_attribute('class').split()
                    pattern = 'jjwxcfont'
                    fontname = [font for font in classlist if re.search(pattern, font)]
                    fontname = ''.join(fontname)
                    chaptertext = ft.fonttext(chaptertext, fontname)
                else:
                    chaptertext = driver.find_elements_by_css_selector('div.novelbody div')[0].text

                chaptertext = utils.re_text(chaptertext)
                f.write(chaptertext)
                time.sleep(2)

        print('write down.')
        driver.quit()


if __name__ == '__main__':
    jj_spider = jj_spider()
    jj_spider.spider()
