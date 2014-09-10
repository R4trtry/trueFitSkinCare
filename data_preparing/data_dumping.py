
# dump cleaned data into mysql database


import re
import os
import MySQLdb
import data_cleaning

# read all file in all categories in the data folder
rootpath = '../scrapping/sephora/'
folders = [f for f in os.listdir(rootpath) if os.path.isdir(rootpath+f)]

def main():
  #insert_product()
  insert_review()
  
def insert_product():
  # insert product information
  # Open database connection
  db = MySQLdb.connect("localhost","root","","insight" )
  # prepare a cursor object using cursor() method
  cursor = db.cursor()

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
        print 'inserted ' + str(counter) + ' rows into Product...'
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

def insert_review():
  # Open database connection
  db = MySQLdb.connect("localhost","root","","insight" )
  # prepare a cursor object using cursor() method
  cursor = db.cursor()

  counter = 0
  error_count = 0
  error_sql = []
  for category in folders:
    category_path = rootpath + category + '/'
    files = [f for f in os.listdir(category_path) if re.search('_',f) ]

    for filepath in files:

      # get product info using data_cleaning functions
      reviews = data_cleaning.clean_review(category_path + filepath)
      
      for p in reviews:
        # prepare the sql insert script by sub in fileds of p  
        sql1 = """INSERT INTO Review(review_id,rating,quick_take,review_text,product_id,review_time,helpful,nohelpful) VALUES ({0},{1},'{2}','{3}','{4}','{5}',{6},'{7}')""".format(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7])

        sql2 = """INSERT INTO Reviewer(review_id,reviewer_id,reviewer_name,reviewer_loc,reviewer_skin,reviewer_age) VALUES ({0},{1},'{2}','{3}','{4}','{5}')""".format(p[0],p[8],p[9],p[10],p[11],p[12])

        try:
          # Execute the SQL command
          cursor.execute(sql1)
          # Commit your changes in the database
          db.commit()
          if counter%1000 == 0:
            print 'inserted ' + str(counter) + ' rows into Review...'
          counter += 1
        except MySQLdb.Error as e:
          # Rollback in case there is any error
          db.rollback()
          if e.args[0] == 1062:
            #print 'Product {0} already in database...'.format(p[0])
            pass
          else:
            #if e.args[0] == 1366:
            #  sql1="""INSERT INTO Review(review_id,rating,quick_take,review_text,product_id,review_time,helpful,nohelpful) VALUES ('{0}',{1},'{2}','{3}','{4}','{5}',{6},'{7}')""".format(p[0],p[1],p[2],'',p[4],p[5],p[6],p[7])
            #  cursor.execute(sql1)
            #else:
            error_count+=1
            error_sql.append(sql1)
            pass

        try:
          # Execute the SQL command
          cursor.execute(sql2)
          # Commit your changes in the database
          db.commit()
        except MySQLdb.Error as e:
          # Rollback in case there is any error
          db.rollback()
          if e.args[0] == 1062:
            print 'Review {0} already in database...'.format(p[0])
            pass
          else:
            error_count+=1
            error_sql.append(sql2)
            pass

  db.close()
  print error_count
  f_err = open('sql_error_log.txt','w')
  f_err.write('\n'.join(error_sql))
  f_err.close()

if __name__ == "__main__":
  main()
