import os
from flask import render_template, jsonify
import MySQLdb
from app import app
import MySQLdb

db = MySQLdb.connect(user="root", host="localhost", port=3306, db="insight")
# db = mdb.connect(user="root", host="localhost", db="world_innodb", charset='utf8')

@app.route("/")
def hello():
    print "hi!"
    return render_template('index.html') 

@app.route("/jquery")
def index_jquery():
    return render_template('index_js.html') 

@app.route("/db")
def cities_page():
    db.query("SELECT product_id FROM Product;")

    query_results = db.store_result().fetch_row(maxrows=0)
    cities = ""
    for result in query_results:
        cities += unicode(result[0], 'utf8')
        cities += "<br>"
    return cities

# @app.route("/db_fancy")
# def cities_page_fancy():
#     db.query("SELECT Name, CountryCode, Population FROM city ORDER BY Population;")

#     query_results = db.store_result().fetch_row(maxrows=0)
#     cities = []
#     for result in query_results:
#         cities.append(dict(name=unicode(result[0], 'utf8'), country=result[1], population=result[2]))
#     return render_template('cities.html', cities=cities) 


# @app.route("/db_json")
# def cities_json():
#     db.query("SELECT Name, CountryCode, Population FROM city;")

#     query_results = db.store_result().fetch_row(maxrows=0)
#     cities = []
#     for result in query_results:
#         cities.append(dict(City=unicode(result[0], 'utf8'), CountryCode=result[1], Population=result[2]))
#     return jsonify(dict(cities=cities))

@app.route("/db_json")
def images_json():
    # category = $("#someId").val()
    db.query("SELECT product.sku_id, category, count(distinct review_id) as ct \
        from product join review where product.product_id = review.product_id \
        group by product.product_id order by ct desc;")

    query_results = db.store_result().fetch_row(maxrows=0)
    products = []
    for result in query_results:
        products.append(dict(sku_id=result[0], category=result[1]))
    # print products[0]['category']
    return jsonify(dict(products=products))

# @app.route("/<category>")
# def images_json():
#     db.query("""SELECT sku_id FROM Product where category='{0}';""".format(category))
#     query_results = db.store_result().fetch_row(maxrows=0)
#     products = []
#     for result in query_results:
#         products.append(dict(sku_id=result[0]))
#     return jsonify(dict(products=products))

@app.route('/<pagename>') 
def regularpage(pagename=None): 
    """ 
    Route not found by the other routes above. May point to a static template. 
    """ 
    return "You've arrived at " + pagename
    db.query("SELECT Name, CountryCode, Population FROM city ORDER BY Population;")
    query_results = db.store_result().fetch_row(maxrows=0)
    return query_results
    #if pagename==None: 
    #    raise Exception, 'page_not_found' 
    #return render_template(pagename) 



