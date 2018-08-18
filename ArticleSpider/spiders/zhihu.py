# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import datetime
from selenium import webdriver
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem,ZhihuAnswerItem
from settings import user_agent_list
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
try:
    import urllparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdci_info&limit={1}&offset={2}&sort_by=default"

    import random
    random_index = random.randint(0, len(user_agent_list)-1)
    random_agent = user_agent_list[random_index]

    headers = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    # 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
    'User-Agent': random_agent

        # Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36
    }

    # 重写settings.py
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path='G:\迅雷下载\chromedriver2_win32/chromedriver.exe')
        super(ZhihuSpider, self).__init__()
        # 信号
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭browser
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行下一步爬取
        如果提取的url中格式为/question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                # question_id = match_obj.group(2)

                # 每个requests都要写，复用性太低
                # import random
                # random_index = random.randint(0, len(user_agent_list) - 1)
                # random_agent = user_agent_list[random_index]
                # self.headers["User-Agent"] = random_agent

                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)


    def parse_question(self, response):
        # 处理question页面，从页面中提取出具体的question item

        if "QuestionHeader-title" in response.text:
            # 处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                # request_url = match_obj.group(1)
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-actions button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
            item_loader.add_css("topics", "QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
        else:
            # 处理旧版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                # request_url = match_obj.group(1)
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num", "*[@id='zh-question-side-header-wrap']/text()|")
            item_loader.add_css("topics", "zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()


        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        # totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None  # 可能不存在
            answer_item["content"] = answer["content"] if "content" in answer["content"] else None  # 可能不存在
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    """
    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback = self.login)]
        # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
    """
    def login(self, response):
        """
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)  # 不指定re.DOTALL默认只匹配一行数据
        xsrf = ""
        if match_obj:
            print(match_obj.group(1))


        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "15221204645",
                "password": "123456"
                "captcha": ""
            }
            
            import time
            t = str(int(time.time()*1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            yield scrapy.Request(captcha_url, headers = self.headers, meta = {"post_data":post_data}, callback = self.login_after_captcha() )
            
            

            
            
    def login_after_captcha(self, response):
    
        with open("captcha.jpg","wb") as f:
            f.write(response.body)
            f.close()
    
        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass
        
        post_data = response.meta.get("post_data",{})
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url = post_url,
            # formdata={
            #     "_xsrf": xsrf,
            #     "phone_num": "15221204645",
            #     "password": "123456"
            # }
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]        
        """ # post登陆

        # selenium模拟登陆
        browser = webdriver.Chrome(executable_path='G:\迅雷下载\chromedriver2_win32/chromedriver.exe')
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_css_selector(".Login-qrcode Button.Button--plain").click()
        time.sleep(10)
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, headers=self.headers)
        # return [scrapy.FormRequest(
        #     url=self.start_urls[0],
        #     headers=self.headers,
        #     # callback=self.check_login
        # )]

    def check_login(self, response):
        # 验证服务器的返回数据判断是否成功，不需要保存cookies，默认放进来
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登陆成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
