
# dump cleaned data into mysql database


import re
import os
import MySQLdb
import data_cleaning


# Open database connection
db = MySQLdb.connect("localhost","root","","insight" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# read all file in all categories in the data folder
rootpath = '../scraping/sephora/'
folders = [f for f in os.listdir(rootpath) if os.path.isdir(rootpath+f)]

# insert product information
counter = 0
for category in folders
  category_path = rootpath + category + '/'
  files = [f for f in os.listdir(category_path) if not re.search('_',f) ]
  
  for filepath in files:
    counter += 1

    maincontent = data_cleaning.get_maincontent(filepath) 
  
    sql = """INSERT INTO Product(product_id,sku_id,product_name,brand,brand_id,category,price,ingredients,discription) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}',{6},'{7}','{8}')""".format(product_id,sku_id,product_name,brand,brand_id,category,price,ingredients,discription)

    try:
      # Execute the SQL command
      cursor.execute(sql)
      # Commit your changes in the database
      db.commit()
      print 'inserted ' + str(counter) + ' rows'
    except IntegrityError as e:
      # Rollback in case there is any error
      db.rollback()
      code, msg = e.orig
        if code == 1062:
          print 'Product {0} already in database ...'
          continue
        else:
          db.close()
          print e
          break





