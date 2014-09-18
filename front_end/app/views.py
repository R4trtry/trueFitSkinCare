import os
from flask import render_template, jsonify
import MySQLdb
from app import app
import collaborative_filter_engine2 as cfg
import numpy as np

# specify db connection
db = MySQLdb.connect(user="root", host="localhost", port=3306, db="insight")

# load pre-trained similarity matrix
simMatrix = np.loadtxt('data_processing/sim_product2.csv',delimiter=',')

# home page
@app.route("/")
def hello():
    print "hi!"
    return render_template('index.html') 

# load result page
@app.route("/results/<category>")
def results(category):
    print "hi!"
    return render_template('results.html',category=category)

# load recommendation result and return a html
@app.route("/result_json/<category>")
def result_json(category):
    test         = 21   
    product_list = cfg.sql2df('select brand, product_name, product_id, sku_id, category, price from Product order by category;')
    usrProfile = [123,293,902,694,381]
    scores = cfg.recommender(simMatrix, usrProfile, category, product_list)
    print scores[0:10]
    result = scores[:10]
    result = result.drop('category',1)
    result = result.set_index('product_id')
    result['image'] = [r'<img src="/static/images/'+ids+'.jpg">'.encode('Utf-8') for ids in result['sku_id'].tolist()]
    products = []
    for id in range(10):
        products.append(dict(product_name=result.ix[id]['product_name'],brand=result.ix[id]['brand'],image=result.ix[id]['image'],price=result.ix[id]['price'],score=result.ix[id]['score']))
    
    return jsonify(dict(products=products))

# load images for landing page
@app.route("/images_json")
def images_json():
    
    # run the query to get product info
    db.query("SELECT product.sku_id, category, brand, product_name, count(distinct review_id) as ct \
        from product join review where product.product_id = review.product_id \
        group by product.product_id order by ct desc;")

    # compile the query results into json and return
    query_results = db.store_result().fetch_row(maxrows=0)
    products = []
    for result in query_results:
        products.append(dict(sku_id=result[0], category=result[1], brand=result[2], product_name=result[3]))
    return jsonify(dict(products=products))
