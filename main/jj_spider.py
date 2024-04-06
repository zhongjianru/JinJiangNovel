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
        self.novelurl = 'https://www.jjwxc.net/onebook.php?novelid=5649664'
        self.index = 0

    def spider(self):
        novel = nl.Novel('', '', '', '')
        novelinfo = novel.get_novelinfo(self.novelurl)
        chapters = novel.get_chapters(self.novelurl)
        print(novelinfo)
        print(chapters)

        opt = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=opt, executable_path='/Users/kinyuchung/Downloads/chromedriver')
        driver.get(self.novelurl)
        time.sleep(5)

        print('start to login...')
        username = ''
        password = ''
        btn_login = driver.find_element_by_id('jj_login')
        btn_login.click()
        time.sleep(2)
        input1 = driver.find_element_by_name('loginname')
        input1.clear()
        input1.send_keys(username)
        time.sleep(2)
        input2 = driver.find_element_by_name('loginpassword')
        input2.clear()
        input2.send_keys(password)
        time.sleep(2)
        input3 = driver.find_element_by_id('login_registerRule')
        input3.click()
        time.sleep(2)
        smt_login = driver.find_element_by_id('window_loginbutton')
        smt_login.click()
        time.sleep(2)

        filepath = '../novel/' + novelinfo['title'] + '.txt'
        print('filepath:', filepath)
        print('start writing in...')

        with open(filepath, mode='w+', encoding='gb18030') as f:
            summary = ''
            summary = summary + novel.space + novelinfo['title'] + novel.newline
            summary = summary + novel.space + '作者：' + novelinfo['author'] + novel.newline
            summary = summary + novelinfo['summary'] + novel.newline
            f.write(summary)
            for chapter in chapters:
                time.sleep(5)
                print(chapter['num'], chapter['title'], '[VIP]' if chapter['isvip'] else '', chapter['summary'], chapter['url'], '字数:', chapter['wordCount'], '最近修改时间:', chapter['lastModify'])
                driver.get(chapter['url'])

                if chapter['isvip']:
                    # vip 章节替换混淆内容
                    f.write('    第 ' + chapter['num'] + ' 章\n\n')
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
