
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
rootpath = '../scrapping/sephora/'
folders = [f for f in os.listdir(rootpath) if os.path.isdir(rootpath+f)]

# insert product information
counter = 0
for category in folders:
  category_path = rootpath + category + '/'
  files = [f for f in os.listdir(category_path) if not re.search('_',f) ]
  
  for filepath in files:

    # get product info using data_cleaning functions
    p = data_cleaning.clean_maincontent(category_path + filepath) 

    # prepare the sql insert script by sub in fileds of p  
    sql = """INSERT INTO Product(product_id,sku_id,product_name,brand,brand_id,category,price,ingredients,discription) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}',{6},'{7}','{8}')""".format(p[0],p[1],p[2],p[3],p[4],category,p[5],p[6],p[7])

    try:
      # Execute the SQL command
      cursor.execute(sql)
      # Commit your changes in the database
      db.commit()
      print 'inserted ' + str(counter) + ' rows...'
      counter += 1
    except MySQLdb.Error as e:
      # Rollback in case there is any error
      db.rollback()
      if e.args[0] == 1062:
        print 'Product {0} already in database...'.format(p[0])
        continue
      else:
        print sql
        db.close()
        print e
        break





