import MySQLdb
import urllib

con = MySQLdb.connect('localhost', 'root', '', 'insight')

with con:
    cur = con.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select sku_id from Product')
    data = cur.fetchall()
    
for d in data:
    src="http://www.sephora.com/productimages/sku/s{0}-main-grid.jpg".format(d.values()[0])
    urllib.urlretrieve(src, "/Users/xuanzhang/Developer/python/scrapping/sephora/static/{0}.jpg".format(d.values()[0]))
    
