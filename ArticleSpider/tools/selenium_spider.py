from selenium import webdriver
from scrapy.selector import Selector
import time



# browser = webdriver.Chrome(executable_path='G:\迅雷下载\chromedriver2_win32/chromedriver.exe')
# browser.get("https://baike.baidu.com/item/%E5%BC%80%E6%BA%90%E4%B8%AD%E5%9B%BD/5462428?fr=aladdin")
# print(browser.page_source)

# browser.find_element_by_css_selector(".Login-qrcode Button.Button--plain").click()
time.sleep(5)

""" 模拟鼠标下滑
# selenium 执行js代码
for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    time.sleep(3)
"""


# t_selector = Selector(text=browser.page_source)
# t_selector.css()
# browser.quit()


""" 设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(executable_path='G:\迅雷下载\chromedriver2_win32/chromedriver.exe', chrome_options=chrome_opt)
browser.get("https://www.taobao.com")
"""

"""# phantomjs, 无界面的浏览器，多进程情况下phantomjs性能会下降很严重
browser = webdriver.PhantomJS(executable_path='G:/迅雷下载/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe')
browser.get("https://www.taobao.com")
print (browser.page_source)
browser.quit()
"""