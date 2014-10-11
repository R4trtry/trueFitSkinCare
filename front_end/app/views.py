import os
from flask import render_template, jsonify
import MySQLdb
from app import app
import collaborative_filter_engine2 as cfg
import numpy as np

# load pre-trained similarity matrix
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
csv_url = os.path.join(SITE_ROOT, "static", "sim_product2.csv")
simMatrix = np.loadtxt(csv_url, delimiter=',')
#simMatrix = np.loadtxt('./front_end/app/static/sim_product2.csv',delimiter=',')

# home page
@app.route("/")
def hello():
    return render_template('index.html') 

@app.route("/graph")
def graph():
    return render_template('graph.html') 

@app.route("/slides")
def slides():
    return render_template('slides.html') 

@app.route("/slides2")
def slides2():
    return render_template('slides2.html')

@app.route("/slidesbw")
def slidesbw():
    return render_template('slides_bw.html')

@app.route("/matrix")
def matrix():
    return render_template('matrix.html') 


# load result page
@app.route("/results/<inputvar>")
def results(inputvar):
    category = inputvar.split('&')[0]
    usrProfile = '&'+'&'.join(inputvar.split('&')[1:])
    return render_template('results.html',category=category,usrProfile=usrProfile)

# load recommendation result and return a html
@app.route("/result_json/<inputvar>")
def result_json(inputvar):
    category = inputvar.split('&')[0]
    usrProfile = inputvar.split('&')[1:]
    numRows = 10
    product_list = cfg.sql2df('select brand, product_name, product_id, sku_id, category, price, discription from Product order by category;')
    sku_id = product_list.sku_id.tolist()
    usrProfile = [sku_id.index(u) for u in usrProfile]
    #print'\n\n\n\n'
    #print category
    #print usrProfile
    #print'\n\n\n\n'
    scores = cfg.recommender(simMatrix, usrProfile, category, product_list)
    #print scores[0:numRows]
    result = scores[:numRows]
    result = result.drop('category',1)
    result = result.set_index('product_id')
    result['image'] = [r'<img src="/static/images/'+ids+'.jpg" height="182" width="182">'.encode('Utf-8') for ids in result['sku_id'].tolist()]
    products = []
    for id in range(numRows):
        products.append(dict(product_name=result.ix[id]['product_name'],product_id=result.index[id],brand=result.ix[id]['brand'],image=result.ix[id]['image'],price=result.ix[id]['price'],score=result.ix[id]['score'],discription=result.ix[id]['discription']))
    print products
    return jsonify(dict(products=products))

# load images for landing page
@app.route("/images_json")
def images_json():
    product_list = cfg.sql2df('SELECT Product.sku_id, category, brand, product_name, count(distinct review_id) as ct \
        from Product join Review where Product.product_id = Review.product_id \
        group by Product.product_id order by ct desc;')
    products = []
    for i in range(len(product_list)):
        result = product_list.ix[i]
        products.append(dict(sku_id=result.sku_id, category=result.category, brand=result.brand, product_name=result.product_name))
    return jsonify(dict(products=products))
