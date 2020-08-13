__author__ = 'zhongjr'

import novel as nl
import login as lg

if __name__ == '__main__':
    novel_name = '俯首为臣'
    chapter_bgn = 21
    chapter_end = 25
    username = ''
    password = ''

    cookies = lg.get_cookies(username, password)
    novel = nl.Novel(novel_name, chapter_bgn, chapter_end, cookies)
    novel.get_novel()

