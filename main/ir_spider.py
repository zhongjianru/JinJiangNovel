# purpose: spider for ireader

import time
from selenium.webdriver import Chrome, ChromeOptions

# 终端命令：/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/Users/kinyuchung/Downloads/ChromeFiles
opt = ChromeOptions()
opt.add_experimental_option('debuggerAddress', '127.0.0.1:9222')  # 连接已经登陆好的窗口
driver_path = '/Users/kinyuchung/Downloads/chromedriver'
driver = Chrome(options=opt, executable_path=driver_path)

chapter_bgn = 2
chapter_num = 89
chapter_end = chapter_num + 1
novel_url = 'https://www.ireader.com.cn/index.php?ca=Chapter.Index&pca=Chapter.Index&bid=13208985&cid='
novel_title = '还璧'
filepath = '../novel/' + novel_title + '.txt'

with open(filepath, mode='w+', encoding='gb18030') as f:
    for i in range(chapter_bgn, chapter_end):
        page_url = novel_url + str(i)
        driver.get(page_url)
        driver.implicitly_wait(10)  # 智能等待
        driver.switch_to.frame('iframe_chapter')

        title = driver.find_element_by_css_selector('div.h5_mainbody [class*=text-title]').get_attribute('innerHTML')
        title = title.replace('<span class="content-word-small">', '').replace('</span>', '').replace('<br>', '').lstrip().rstrip().replace('\n    \n    \n    ', ' ')
        f.write('    ' + title + '\n')

        text = ''
        text_elements = driver.find_elements_by_css_selector('div.h5_mainbody p.bodytext')
        for element in text_elements:
            text = text + '    ' + element.text + '\n'
        f.write(text + '\n')
        print(title + text[:10] + '\n')
        time.sleep(20)

