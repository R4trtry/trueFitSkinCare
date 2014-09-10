#!usr/local/bin/python2.7
# scraping reviews from Sephora.com

# reviews are shown five per page, have to constantly request next page
# get_review  gets the reviews in one page
# get_reviews take care of changin page and recording reciews


# get review from a page
# same thing with scraping_maincontent, no need to refresh though because the url requested is a plain html file that never seems to fail
def get_review(browser):
  while True:
    try:
      wait = WebDriverWait(browser, 10)
      wait.until(EC.presence_of_element_located((By.CLASS_NAME, "BVRRDisplayContentBody")))
      reviews = browser.find_element_by_class_name("BVRRDisplayContentBody")
      htmlstr = reviews.get_attribute("innerHTML")
      return htmlstr
    except:
      time.sleep(.5)
      continue

    
# get reviews from all pages for a product
def scrap_reviews(browser, path, product_id):
  wait = WebDriverWait(browser, 10)
  page_num = 0
  # open a file to write the html
  f = open(path + "_reviews.html","a")
    while True:
      # get next page using the url, which has no css and js s.t. it loads fast!
      page_num += 1
      review_url = "http://reviews.sephora.com/8723abredes/"+product_id+"/reviews.htm?format=embedded&page="+str(page_num)
      browser.get(review_url)
      
      # get review on this page and dump into a file
      htmlstr = get_review(browser)
      f.write(htmlstr.encode('utf8'))
      try:    
        wait.until(EC.presence_of_element_located((By.NAME, 'BV_TrackingTag_Review_Display_NextPage')))
      except TimeoutException:
        # time out means no more next page, done
        break
  # close the html file and quit the browser 
  f.close
  browser.quit()
  return True

