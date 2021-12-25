__author__ = 'zhongjr'

import novel as nl
import login as lg

if __name__ == '__main__':
    novel_name = '实用主义者的爱情'
    chapter_bgn = 110
    chapter_end = None
    username = ''
    password = ''

    # lg.user_login(username, password)

    cookies = lg.get_cookies(username, password)
    novel = nl.Novel(novel_name, chapter_bgn, chapter_end, cookies)
    novel.get_novel()

