import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib  # 兼容py2/py3
import re


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
# 加载cookie
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    'User-Agent': agent
}


def is_login():
    # 通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():
    # 获取xsrf code
    response = session.get("https://www.zhihu.com", headers = header)
    # print(response.text)

    # text = '<input type="hidden" name="_xsrf" value="126asfsaf2a1afas12fasf1"/>'
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        print(match_obj.group(1))
    else:
        return ""

# 调用cookie登陆，引入cookie之后不再返回首页解决方法，将网页保存下来
def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("OK")


# 获得验证码
def get_captcha():
    import time
    t = str(int(time.time()*1000))
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
    t = session.get(captcha_url, headers = header)  # 只能用session
    with open("captcha.jpg","wb") as f:
        f.write(t.content)
        f.close()

    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass

    captcha = input("输入验证码\n>")
    return captcha



# 输入密码登陆
def zhihu_login(account, password):
    # 知乎登陆
    if re.match("^1\d{10}",account):
        print("手机号码登陆")
        post_url = "https://www.zhihu.com/login/phone_num"
        captcha = get_captcha()
        post_data = {
            "_xsrf": get_xsrf,
            "phone_num": account,
            "password": password,
            "captcha": get_captcha()
        }
    else:
        if "@" in account:
            print("邮箱登陆")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf,
                "email": account,
                "password": password
            }
    response_text = session.post(post_url, data = post_data, headers = header)
    session.cookies.save()



# zhihu_login("15221204645", "123456")
# get_index()
is_login()