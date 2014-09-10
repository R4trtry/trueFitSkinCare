
# scraping product information and user reviews from Sephora.com
# scraped htmls are stored in folders by categories

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import time
import re
import scrap_maincontent
import scrap_reviews

def main():
  path_to_chromedriver = "/Users/xuanzhang/Developer/python/scrapping/chromedriver"
  browser0 = webdriver.Chrome(executable_path = path_to_chromedriver)
  website = "http://www.sephora.com/"

  # categories to work for now
  categories = ['face-wash-facial-cleanser',\
                'facial-toner-skin-toner',\
                'night-cream',\
                'eye-cream-dark-circles',\
                'moisturizer-skincare',\
                'bb-cream-cc-cream',\
                'face-serum']
  category = categories[-1]

  # if no such directory for the html, create on
  category_path = './sephora/' + category
  if not os.path.isdir(category_path):
      os.makedirs(category_path)
  # in case aborted, check what pages have been scraped
  files = [f for f in os.listdir(category_path) if f[-4:]=='html' ]
  product_list = [re.findall(r'(P\w+)',file)[0] for file in files]

  
  page_number = 0
  # scrap and hit 'arrow-right' to scrap 
  while EC.element_to_be_clickable((By.CLASS_NAME, "arrow arrow-right")):
    page_number += 1

    # pageSize = -1 s.t. each page has 300 items
    url = website + category + '?pageSize=-1&currentPage=' + str(page_number)
    browser0.get(url)
    
    # get item list by tag sku-item, and go through the list to scrap    
    items = browser0.find_elements_by_class_name('sku-item')
    for item in items:
      product_id = item.get_attribute('data-product_id')
      product_path = category_path + '/' + product_id

      # if product page is already scrapped, skip to next product
      if (product_id in product_list) and\
         (product_id+'_reviews' in product_list):
        continue
      time.sleep(.5)

      # open a new browser window for reviews
      browser1 = webdriver.Chrome(executable_path = path_to_chromedriver)
      browser1.get(item.get_attribute('href'))

      # scrap maincontent or reviews, whichever is not scraped  
      if product_id not in product_list:
        flag1 = scrap_maincontent(browser1, product_path)
      else:
        flag1 = True
      if product_id+'_reviews' not in product_list:
        flag2 = scrap_reviews(browser1, product_path, product_id)
      else:
        flag2 = True
      
      print product_id, flag1, flag2


if __name__ == "__main__":
    main()
