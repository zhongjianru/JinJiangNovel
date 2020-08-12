# Time : 2020-08-09 23:03

# Author : zhongjr

# File : otherweb_po18.py

# Purpose: po18

import os
import time
from selenium import webdriver


def popo_spider():
    login_url = 'https://members.po18.tw/apps/login.php'
    main_url = 'https://www.po18.tw'
    book_id = '682382'
    novel_url = main_url + '/books/' + book_id
    articles_url = novel_url + '/articles?page={}'

    opt = webdriver.FirefoxOptions()  # 创建chrome参数对象
    driver = webdriver.Firefox(options=opt)
    username = ''  # 账号
    password = ''  # 密码

    print('start to login...')
    driver.get(login_url)
    input1 = driver.find_element_by_name('account')
    input1.clear()
    input1.send_keys(username)
    input2 = driver.find_element_by_name('pwd')
    input2.clear()
    input2.send_keys(password)
    btn_login = driver.find_element_by_class_name('btn_func')
    btn_login.click()
    time.sleep(1)

    print('getting novel...')
    driver.get(novel_url)
    novelname = driver.find_element_by_class_name('book_name').text
    author = driver.find_element_by_class_name('book_author').text
    chapter_num = driver.find_element_by_class_name('statu').text
    print('novelname:', novelname, ', author:', author)
    filepath = os.getcwd() + '/' + novelname + '.txt'

    page = 1  # 页数要准确，可以由上面的章节总数确定
    step = 100  # 每页 100 章
    chapter_list = []
    compath = '//div[@class="list-view"]/div[{}]/div'

    path = {
        'num': compath + '/div[@class="l_counter"]',  # error
        'name': compath + '/div[@class="l_chaptname"]/a',
        'url': compath + '/div[@class="l_chaptname"]/a'
    }

    for p in (list(range(1, page+1))):
        try:
            driver.get(articles_url.format(str(p)))
            print('getting page', p, ',', page, 'totally.')
            for i in (list(range(1, step+1))):
                try:
                    num = driver.find_element_by_xpath(path['num'].format(str(i))).text
                    name = driver.find_element_by_xpath(path['name'].format(str(i))).text
                    url = driver.find_element_by_xpath(path['url'].format(str(i))).get_attribute('href')
                    chapter = {
                        'num': num,
                        'name': name,
                        'url': url
                    }
                    print(chapter)
                    chapter_list.append(chapter)
                except Exception as e:
                    break
        except Exception as e:
            print(e)
            break

    print('get', len(chapter_list), 'chapter(s).')

    with open(filepath, mode='w+', encoding='utf-8') as f:

        print('writing...')

        f.write('    ' + novelname + '\n\n')
        f.write('    ' + '作者：' + author + '\n\n')

        # text = ''
        # 循环获取章节文本
        for chap in chapter_list:
            try:
                driver.get(chap['url'])
                time.sleep(10)  # 等待页面加载
                content = driver.find_element_by_xpath('//div[@id="readmask"]/div[1]').text  # 如果获取不到内容，可以加一个提醒
                text = '    ' + chap['num'] + ' ' + chap['name'] + '\n\n'  # + content + '\n\n'
                for line in content.splitlines():
                    # line = line.replace('　　', '\n\n    ').lstrip()
                    text = text + '    ' + line.lstrip() + '\n\n'
                f.write(text)
            except Exception as e:
                print(e)

        print('write down.')

    driver.quit()


if __name__ == '__main__':
    popo_spider()
