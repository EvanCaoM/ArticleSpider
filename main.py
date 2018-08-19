from scrapy.cmdline import execute

import sys
import os

# 获得当前py的目录
# print (os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 执行scrapy crawl jobbole
execute(["scrapy","crawl","jobbole"])
# execute(["scrapy","crawl","zhihu"])
# execute(["scrapy","crawl","zhihu_test"])
# execute(["scrapy","crawl","lagou"])
# execute(["scrapy","crawl","hahha"])