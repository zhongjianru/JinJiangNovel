import utils
import time
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

cookie_file = 'cookies.txt'
login_url = 'http://my.jjwxc.net/'
chap_url = 'http://my.jjwxc.net/onebook_vip.php?novelid=3288706&chapterid=22'


# 新增：读取本地 cookies 文件
def read_cookies():
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r+') as f:
            cookies = f.read()
    else:
        with open(cookie_file, 'w+') as f:
            cookies = ''
            f.write(cookies)

    print('reading', cookie_file, '...')
    return cookies


# 测试本地 cookies 是否可用
def test_cookies(cookies):
    headers = utils.get_headers(cookies)
    soup = utils.get_url(chap_url, headers=headers)
    noveltext = ''
    isvalid = True
    try:
        noveltext = soup.select('div[class="noveltext"]')[0]
    except:
        pass
    if noveltext == '':
        isvalid = False
    return isvalid


# 用户登录
def user_login(username, password):
    # 打开登录页面
    opt = webdriver.FirefoxOptions()
    opt.add_argument('--headless')
    driver = webdriver.Firefox(options=opt)
    driver.get(login_url)

    # 等待页面加载
    exp = EC.presence_of_element_located((By.ID, 'jj_login'))
    wait = WebDriverWait(driver, 60)
    tar = wait.until(exp)

    # 登录
    btn_login = driver.find_element_by_xpath('//*[@id="jj_login"]')
    btn_login.click()

    input_name = driver.find_element_by_id('loginname')
    input_name.clear()
    input_name.send_keys(username)

    input_pwd = driver.find_element_by_id('loginpassword')
    input_pwd.clear()
    input_pwd.send_keys(password)

    input_keep = driver.find_element_by_id('cookietime')
    input_keep.click()

    time.sleep(2)

    btn_submit = driver.find_element_by_xpath('//*[@id="login_form"]/ul/div[@id="logininput"]/li[3]/input')
    btn_submit.click()

    time.sleep(5)

    # 访问 vip 章节，获取 cookie
    driver.get(chap_url)
    cookie_list = driver.get_cookies()  # 格式化打印cookie
    cookie_dict = {}
    cookies = ''

    for one in cookie_list:
        cookie_dict[one['name']] = one['value']
        cookies = cookies + one['name'] + '=' + one['value'] + '; '

    cookies = cookies.rstrip('; ')

    # 写入 cookie
    with open(cookie_file, mode='w+') as f:
        f.write(cookies)

    # 退出浏览器窗口
    driver.quit()


# 获取可用 cookies
def get_cookies(username, password):
    cookies = read_cookies()
    isvalid = test_cookies(cookies)
    if isvalid:
        print('cookie is valid.')
    else:
        print('cookie is invalid, start to login...')
        user_login(username, password)
        print('login successfully.', cookie_file, 'write done.')

    cookies = read_cookies()
    return cookies
