# -*- coding: UTF-8 -*- 
import os

# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.by import By

from lxml import html
from time import sleep
import pandas as pd

from utils import timer, get_item, get_item_links, get_detail_item

def crawl_to_csv():
    # https://stackoverflow.com/questions/66892502/chromedriver-desired-capabilities-has-been-deprecated-please-pass-in-an-options
    option = webdriver.ChromeOptions()
    option.add_argument("--disable-infobars")
    option.add_argument("--start-maximized")
    option.add_argument("--disable-notifications")
    # https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Remote(
        'http://selenium:4444/wd/hub',
        options=option
        )
    base_link = 'https://batdongsan.com.vn'
    type_link = '/cho-thue-can-ho-chung-cu-'
    district_links = ['quan-1','quan-2','quan-3','quan-4','quan-5','quan-6','quan-7','quan-8']
    # district = 'quan-3'

    all_items = pd.DataFrame()

    for district in district_links:
        # start crawl inside 1 district
        link = base_link + type_link + district
        # all_items = all_items.append(get_item(link=link,driver=driver))
        sleep(3)
        
        # then continue to crawl in next pages, based on pagination-button
        driver.get(link)
        sleep(3)
        while True:
            # try:
        
            next_page_xpath = '//a[@class="re__pagination-icon"]/i[@class="re__icon-chevron-right--sm"]'
            driver.find_element(By.XPATH, next_page_xpath).click()
            sleep(3)
            print(driver.current_url)
            current_outer_page = driver.current_url
            all_items = all_items.append(get_item(link=current_outer_page,driver=driver))       # sau khi chạy câu này xong, driver.current_url sẽ bị thay đổi, nên item cuối cùng của trang 2 bị load lại, và ta không thể qua trang 3.
            driver.get(current_outer_page)
            sleep(3)

            # except:
            #     break
            
        all_items.to_csv('/data/item_{}.csv'.format(district), index=False)

    driver.quit()