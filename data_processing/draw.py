import pylab
import MySQLdb
import pandas as pd
import numpy as np

def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df


plist = sql2df("select avg(rating) as ar, product.product_id, brand, price, count(review_id) as ct from product join review where product.product_id=review.product_id group by product.product_id order by price")
ct = plist['ct']
pr = plist['price']
ar = plist['ar']
colors = np.random.rand(len(ar))
pylab.figure()
pylab.scatter(ct,pr,s=ar*15,alpha = .5,c=colors)
pylab.show()
