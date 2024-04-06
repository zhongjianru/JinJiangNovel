import os
import operator
import requests
from fontTools.ttLib import TTFont
from bs4 import BeautifulSoup as bs


# 将字体文件转换为 xml
def getfontxml(fontname):
    fontpath = '../files/' + fontname + '.woff2'
    xmlpath = '../files/' + fontname + '.xml'
    font = TTFont(fontpath)
    font.saveXML(xmlpath)
    # order = files.getGlyphOrder()
    with open(file=xmlpath, encoding='utf-8') as f:
        xml = f.read().replace('<TTGlyph name="glyph00000"/>', '')
    return xml


# 获取每个混淆字的显示坐标
def getwordsxy(xml):
    soup = bs(xml, 'xml')

    codelist = []
    glyphid = soup.select('GlyphID')
    for gl in glyphid[1:]:  # 去掉第一个
        ls = {
            'code': gl.get('name'),
            'order': int(gl.get('id'))-1  # 共 201 个字，下标为 0-200
        }
        codelist.append(ls)

    words = []
    glyphs = soup.select('TTGlyph')
    for tt in glyphs[1:]:  # 去掉第一个
        # code = re.findall('TTGlyph name="(.*?)"', str(glyphs))
        code = tt.get('name')
        xcor = []
        ycor = []
        order = None
        for ct in tt.select('contour'):
            for pt in ct.select('pt'):
                x = xcor.append(pt.get('x'))
                y = ycor.append(pt.get('y'))

        for co in codelist:
            if co['code'] == code:
                order = co['order']

        word = {
            'code': code,
            'order': order,
            'xcor': xcor,
            'ycor': ycor,
        }
        words.append(word)
    return words


# 将章节字体与基础字体的显示坐标进行比较，得出混淆字的实际文字
def findwords(basewords, currwords):
    with open('../files/re_list.txt', 'r+') as f:
        re_list = f.read()
    res = []
    for p1 in basewords:
        for p2 in currwords:
            if operator.eq(p1['xcor'], p2['xcor']) and operator.eq(p1['ycor'], p2['ycor']):
                word = re_list[int(p1['order'])]
                rs = {
                    'basecode': p1['code'].replace('uni', '\\u').lower(),
                    'currcode': p2['code'].replace('uni', '\\u').lower(),
                    'order': p1['order'],
                    'word': word,
                    'wordcode': word.encode('unicode_escape').decode('utf-8')  # 中文 -> unicode编码(byte) -> 字符串(str)
                }
                res.append(rs)
    return res


# 替换混淆字
def rewords(text, res):
    text = text.encode('unicode_escape')   # 转为unicode编码->byte
    # text = eval('"%s"' % text)  # 显示两个斜杠（实际上只有一个）->str
    text = str(text, encoding='utf-8')  # byte->str
    text = text.replace('\\u200c', '')  # 去除干扰字符->str
    # text = [text.replace(rs['currcode'], rs['wordcode']) for rs in res]
    for rs in res:
        text = text.replace(rs['currcode'], rs['wordcode'])
    text = bytes(text, encoding='utf-8').decode('unicode_escape').lstrip('b\'').rstrip('\'')  # ->bytes->中文
    return text


# 调度入口
def fonttext(text, fontname):
    # 下载章节字体
    url = 'http://static.jjwxc.net/tmp/fonts/' + fontname + '.woff2?h=my.jjwxc.net'
    fontpath = '../files/' + fontname + '.woff2'
    xmlpath = '../files/' + fontname + '.xml'
    response = requests.get(url)
    with open(fontpath, 'wb+') as f:
        f.write(response.content)

    # 章节字体处理
    currfont = getfontxml(fontname)
    currwords = getwordsxy(currfont)

    # 基础字体处理
    basefont = getfontxml('base')
    basewords = getwordsxy(basefont)

    # 匹配混淆字的实际文字，并进行替换
    res = findwords(basewords, currwords)
    text = rewords(text, res)

    # 删除章节字体文件
    if os.path.exists(fontpath):
        os.remove(fontpath)
    if os.path.exists(xmlpath):
        os.remove(xmlpath)

    return text
