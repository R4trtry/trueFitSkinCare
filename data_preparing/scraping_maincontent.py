
# scrap main content of product

# browser is the selenium handle of a window
# path is the path to store scraped html

def scrap_maincontent(browser, path):

  while True:
    try:
      # wait while page's loading
      wait = WebDriverWait(browser, 10)
      wait.until(EC.presence_of_element_located((By.CLASS_NAME, "maincontent")))
      # get the div that contians the info
      maincontent = browser.find_element_by_class_name("maincontent")
      htmlstr = maincontent.get_attribute("innerHTML")
      # write it into a file 
      f = open(path + ".html","w")
      f.write(htmlstr.encode('utf8'))
      f.close
      return True
    except:
      # if failed, refresh and try again
      # sometimes chrome just plays dumb
      browser.refresh()
      time.sleep(1)
      continue

