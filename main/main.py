__author__ = 'zhongjr'

import novel as nl
import login as lg

if __name__ == '__main__':
    novel_name = '多此一女'
    chapter_bgn = None
    chapter_end = None
    username = '15603006502'
    password = 'zjr19941228'

    # lg.user_login(username, password)

    cookies = lg.get_cookies(username, password)
    novel = nl.Novel(novel_name, chapter_bgn, chapter_end, cookies)
    novel.get_novel()

