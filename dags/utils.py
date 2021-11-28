
# -*- coding: UTF-8 -*-
  
from selenium import webdriver
from lxml import html
from time import sleep
import pandas as pd
import functools
import time


def timer(func): 
    # https://realpython.com/python-timer/#a-python-timer-decorator
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return value
    return wrapper_timer


def get_item_links(outer_page_link, driver):
    """ return a list of item-detail-href inside a page"""

    driver.get(outer_page_link)
    sleep(3)
    driver_page_source = driver.page_source
    tree = html.fromstring(driver_page_source)
    detail_item_links = []
    current_page_xpath = '//a[@class="js__product-link-for-product-id"]'
    for item in tree.xpath(current_page_xpath):
        base_link = 'https://batdongsan.com.vn'
        detail_item_link = base_link + item.xpath('./@href')[0]
        detail_item_links.append(detail_item_link)

    return detail_item_links


def get_detail_item(detail_item_link, driver):
    """Return 1 json record."""
    
    print('Scraping {}'.format(detail_item_link))
    driver.get(detail_item_link)
    sleep(3)
    my_driver_page_source = driver.page_source
    item = html.fromstring(my_driver_page_source)

    record = {
        'district': item.xpath('.//a[@class="re__link-se" and @level="3"]/text()'), 
        'title': item.xpath('.//h1[@class="re__pr-title pr-title"]/text()'), 
        'price': item.xpath('//div[span[text()="Mức giá"]]/span[@class="value"]/text()'),
        'area': item.xpath('//div[span[text()="Diện tích"]]/span[@class="value"]/text()'),
        'phone': item.xpath('.//span[@class="hidden-mobile m-on-title"]/@raw'),

        'bedroom': item.xpath('//div[span[text()="Số phòng ngủ:"]]/span[@class="value"]/text()'),
        'toilet': item.xpath('//div[span/text()="Số toilet:"]/span[@class="value"]/text()'),
        'project_name': item.xpath('//div[span/text()="Tên dự án:"]/span[@class="value"]/text()'),
        'project_id_link': item.xpath('//a[@class="re__link-pr link"]/@href'),
        'investor': item.xpath('//div[span/text()="Chủ đầu tư:"]/span[@class="value"]/text()'),
        # 'location_googlemap':,
        'contact_name': item.xpath('//span[@class="re__contact-name js_contact-name"]/text()'),
        'created_date': item.xpath('//div[span/text()="Ngày đăng"]/span[@class="value"]/text()'),
        'expire_date': item.xpath('//div[span/text()="Ngày hết hạn"]/span[@class="value"]/text()'),
        'posting_type': item.xpath('//div[span/text()="Loại tin"]/span[@class="value"]/text()'),
        'posting_id': item.xpath('//div[span/text()="Mã tin"]/span[@class="value"]/text()'),
        'posting_url': '',
        }
    
    return record
    

@timer
def get_item(link, driver):
    """Return a list of item """
    item_list = []
    for item in get_item_links(outer_page_link=link,driver=driver):
        item_list.append(get_detail_item(detail_item_link=item, driver=driver))
        sleep(3)

    df = pd.DataFrame(item_list)
    return df