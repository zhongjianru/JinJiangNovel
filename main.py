__author__ = 'zhongjr'

import novel as nl

if __name__ == '__main__':
    novelname = '俯首为臣'
    bgnchapter = None
    endchapter = 10
    vipcookie = ''

    novel = nl.Novel(novelname, bgnchapter, endchapter, vipcookie)
    novel.get_novel()

