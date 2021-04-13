import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import AlexbankItem
from itemloaders.processors import TakeFirst
import requests

urls = ['https://www.alexbank.com/aboutUsSectionServlet/?operation=getPressNewsArchiveList', "https://www.alexbank.com/aboutUsSectionServlet/?operation=getPressNewsList"]

payload="{\"component\":\"7619c525-b089-4192-955d-0200eecd32c7\",\"bankName\":\"ALEX\",\"numberLastYears\":\"1\",\"language\":\"\"}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/plain, */*',
  'contextPath': '',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'Content-Type': 'application/json',
  'Origin': 'https://www.alexbank.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.alexbank.com/retail/about-us/media-and-news.html',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '_ga=GA1.2.870306792.1618228573; _gid=GA1.2.1234074563.1618228573; _cs_c=1; _fbp=fb.1.1618228573298.284536388; cookie_status_bar=accepted; gdpr_cookie_consent="Necessary-Cookies,Performance-Cookies,Targeting-Cookies"; _cs_cvars=%7B%221%22%3A%5B%22Page%20Type%22%2C%22pressNewsDetailPage%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22ALEX%3ARetail%3AAbout%20Us%3AMedia%20And%20News%3A%3AEgypt%20Speaks%20Handcrafts%20%22%5D%2C%223%22%3A%5B%22Intesa%20Bank%22%2C%22ALEX%22%5D%2C%224%22%3A%5B%22Site%20Language%22%2C%22Ar%22%5D%2C%225%22%3A%5B%22Site%20Country%22%2C%22Egypt%22%5D%2C%226%22%3A%5B%22Portal%20Section%22%2C%22public%22%5D%2C%227%22%3A%5B%22Visitor%20Type%22%2C%22guest%22%5D%2C%228%22%3A%5B%22Customer%20Segment%22%2C%22Retail%22%5D%7D; _cs_id=43ca1d86-17c5-a0f7-efe0-00e34ab2c580.1618228573.3.1618314520.1618314506.1.1652392573838.Lax.0; _cs_s=2.1; __CT_Data=gpv=4&ckp=tld&dm=alexbank.com&apv_39_www56=4&cpv_39_www56=4; _gat_UA-129304750-4=1; _gat_UA-129304750-5=1; JSESSIONID=XXG6mRNvzVwyPrwoaM8E-AntEMhPwv9wM-DUE9Aj; JSESSIONID=XXG6mRNvzVwyPrwoaM8E-AntEMhPwv9wM-DUE9Aj'
}


class AlexbankSpider(scrapy.Spider):
	name = 'alexbank'
	start_urls = ['https://www.alexbank.com/retail/about-us/media-and-news.html']

	def parse(self, response):
		for url in urls:
			data = requests.request("POST", url, headers=headers, data=payload)
			raw_data = json.loads(data.text)
			for post in raw_data:
				link = post['readMoreLink']
				date = post['date']
				title = post['title']
				print(date, title)
				yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="cmsTextWrpper section__contentWrapper"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AlexbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
