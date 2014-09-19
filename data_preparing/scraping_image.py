import MySQLdb
import urllib

con = MySQLdb.connect('localhost', 'root', '', 'insight')

with con:
    cur = con.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select sku_id from Product')
    data = cur.fetchall()
    
counter = 0
for d in data:
	counter += 1
	if counter % 10 == 0 :
		print "Retrieved", counter, "images from sephora..."
    
	src="http://www.sephora.com/productimages/sku/s{0}-main-hero-300.jpg".format(d.values()[0])
	urllib.urlretrieve(src, "/Users/xuanzhang/Developer/python/scrapping/sephora/static/img300/{0}.jpg".format(d.values()[0]))
    
