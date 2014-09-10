
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
                'bb-cream-cc-cream']

  print categories

if __name__ == "__main__":
    main()
