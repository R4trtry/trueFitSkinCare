import os
from flask import render_template, jsonify
import MySQLdb
from app import app
import MySQLdb
import collaborative_filter_engine as cfg

db = MySQLdb.connect(user="root", host="localhost", port=3306, db="insight")
# db = mdb.connect(user="root", host="localhost", db="world_innodb", charset='utf8')
ratingMatrix = cfg.prepare()

@app.route("/")
def hello():
    print "hi!"
    return render_template('index.html') 

@app.route("/results")
def results():
    print "hi!"
    return render_template('results.html') 

@app.route("/result_json")
def result_json():
    test         = 21   
    category     ='face-wash-facial-cleanser'
    product_list = cfg.sql2df('select distinct product_id, sku_id, category from Product order by category;')
    print "here"
    scores = cfg.recommender(ratingMatrix, ratingMatrix[test:(test+1)], category, product_list)
    result = scores[:10]
    result = result.drop('category',1)
    result = result.set_index('product_id')
    result['image'] = [r'<img src="/static/images/'+ids+'.jpg">'.encode('Utf-8') for ids in result['sku_id'].tolist()]
    # result'/static/images/'+products[i]['sku_id'] + '.jpg'
    print result.to_html(escape=False)
    result = result.drop('sku_id',1)
    # result = result[['product_id','image','score']]
    return result.to_html(escape=False)#json()

@app.route("/db_json")
def images_json():
    # category = $("#someId").val()
    db.query("SELECT product.sku_id, category, brand, product_name, count(distinct review_id) as ct \
        from product join review where product.product_id = review.product_id \
        group by product.product_id order by ct desc;")

    query_results = db.store_result().fetch_row(maxrows=0)
    products = []
    for result in query_results:
        products.append(dict(sku_id=result[0], category=result[1], brand=result[2], product_name=result[3]))
    # print products[0]['category']
    return jsonify(dict(products=products))


# @app.route("/jquery")
# def index_jquery():
#     return render_template('index_js.html') 

# @app.route("/db")
# def cities_page():
#     db.query("SELECT product_id FROM Product;")

#     query_results = db.store_result().fetch_row(maxrows=0)
#     cities = ""
#     for result in query_results:
#         cities += unicode(result[0], 'utf8')
#         cities += "<br>"
#     return cities

# @app.route("/<category>")
# def images_json():
#     db.query("""SELECT sku_id FROM Product where category='{0}';""".format(category))
#     query_results = db.store_result().fetch_row(maxrows=0)
#     products = []
#     for result in query_results:
#         products.append(dict(sku_id=result[0]))
#     return jsonify(dict(products=products))

# @app.route('/<pagename>') 
# def regularpage(pagename=None): 
#     """ 
#     Route not found by the other routes above. May point to a static template. 
#     """ 
#     return "You've arrived at " + pagename
#     db.query("SELECT Name, CountryCode, Population FROM city ORDER BY Population;")
#     query_results = db.store_result().fetch_row(maxrows=0)
#     return query_results
#     #if pagename==None: 
#     #    raise Exception, 'page_not_found' 
#     #return render_template(pagename) 
