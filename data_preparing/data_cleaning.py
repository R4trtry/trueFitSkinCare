
# functions that 
#          clean scraped html
#          extract information
#          make them ready to be dumping into db

import re
from dateutil.parser import parse

def main():
  print "clean"


def clean_maincontent(filepath):
  f = open(filepath)
  htmltext = f.read()
  f.close()

  product_id   = re.split(r'/',filepath)[-1][0:-5]
  brand        = re.sub("'","''", re.findall(r'class="brand-link">(.*?)</a>',htmltext)[0])
  brand_id     = re.findall(r'"brand-name"><a href="/(\S+)\?icid2',htmltext)[0]
  product_name = re.sub("'","''", re.findall(r'<br>\s+(.*?)</h1>',htmltext)[0])
  sku_id       = re.findall(r'value OneLinkNoTx">(\w+)</span>',htmltext)[0]
  try:
    ingredients  = re.sub("'","''",'\n'.join(re.split(r'<.*?>', re.findall(r'<p class="sku-ingredients">(.*?)</p>', htmltext)[0])))
  except:
    ingredients = ''
  ingredients = re.sub('\xef\xbc\x88', '(', ingredients)
  ingredients = re.sub('\xef\xbc\x89', ')', ingredients)
  price         = re.findall(r'<span class="price">(.*?)</span>', htmltext)[0]
  discription   = re.sub("'","''",'\n'.join(re.split(r'<.*?>', re.findall(r'"short-description hidden">\s+([\S\s]*?)</div>',htmltext)[0])))
 
 # print '\t'.join((product_id, sku_id, str(len(str(ingredients))), str(len(discription)), brand, product_name, price))

  return (product_id,sku_id,product_name,brand,brand_id,price,ingredients,discription)

# return field values given a datafile 
def clean_review(filepath):
  f = open(filepath)
  htmltext = f.read()
  f.close()
  product_id   = re.split(r'/',filepath)[-1][0:-13]
  reviews = []

  # separate review blocks
  review_blocks = re.split('<div id="BVRRDisplayContentReviewID_',htmltext)[1:]

  for text in review_blocks:
    # review info
    review_id     = re.findall(r'(\w+)"',text)[0]
    try:
      rating      = re.findall(r'"BVImgOrSprite" alt="(\w)',text)[0]
    except:
      rating      = '0'
    quick_take    = ', '.join(re.findall(r'"BVRRTag">([\w\s]+)</span>',text))
    try:
      review_text   = re.sub('"',"''",re.sub("'","''",re.findall(r'<span class="BVRRReviewText">(.*?)</span>',text)[0]))
    except:
      review_text = ''
    review_text   = re.sub(r"\\", "",review_text)
    try:
      review_time   = parse(re.findall(r'BVRRReviewDate">(\S+)</span>',text)[0]).strftime("%Y-%m-%d")
      votes         = re.findall(r'<span class="BVDINumber">(\w+)</span>',text)
      helpful       = votes[0]
      nohelpful     = votes[1]
    except:
      continue
    # reviewer info
    reviewer_name = re.findall(r'"BVRRNickname">(\S+ )<',text)[0]
    try:
        reviewer_loc  = re.findall(r'BVRRUserLocation">([\w\s]+)</span>', text)[0]
    except:
        reviewer_loc  = ''
    try:
        reviewer_skin = re.findall(r'BVRRContextDataValueskinType">([\w\s]+)</span>', text)[0]
    except:
        reviewer_skin = ''
    try:
        reviewer_age  = re.findall(r'BVRRContextDataValueage">([\w\s]+)</span>', text)[0]
    except:
        reviewer_age  = ''
    if reviewer_name != 'Anonymous ':
        reviewer_id = re.findall(r'_ReadAllReviews_(\w+)\" class',text)[0]
    else:
        reviewer_id = 0
        continue

    reviews.append((review_id, rating, quick_take, review_text, product_id, review_time, helpful, nohelpful, reviewer_id, reviewer_name, reviewer_loc, reviewer_skin, reviewer_age))

  return reviews


if __name__ == "__main__":
  main() 
