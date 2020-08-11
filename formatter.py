# Time : 2020/4/12 5:03 下午

# Author : zhongjr

# File : formatter.py

# Purpose: 文本格式化
# 1、删除多余换行：以中文编码或者逗号结尾，不换行
# 2、半角标点符号转全角(没做) https://www.jianshu.com/p/152e081fec1b
# 3、中文数字和阿拉伯数字互转(没做)

def text_format(text):
    marks = ['。','？','！','”','章','》','※']
    result = ''
    # endchr = ''
    flag = True  # 换行标记，默认为True

    for line in text.split('\n'):
        line = line.strip().replace('　　','')

        if line == '':
            continue  # 空行不处理

        if flag:
            result = result + '\n\n' + '    ' + line
        else:
            result = result + line

        endchr = line[-1:]

        # 以中文编码或者逗号结尾，不换行
        if (('\u4e00' <= endchr <= '\u9fff') or endchr == '，') and endchr not in marks:
            flag = False
        else:
            flag = True

    f = open('RESULT.txt', mode='w+', encoding='gb18030')
    f.write(result)
    f.close()
    print('write down.')


if __name__ == '__main__':
    text = open('/Users/kinyuchung/documents/衡门之下.txt', mode='r', encoding='gb18030').read()
    text_format(text)
