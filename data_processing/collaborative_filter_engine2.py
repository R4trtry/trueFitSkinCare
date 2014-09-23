import re
import MySQLdb
import pandas as pd
# import 
import numpy as np
import math
from scipy.sparse import csr_matrix
from scipy.sparse import isspmatrix_csc
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from collections import OrderedDict


def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df

# filter the recommendations with category 
# return a list sorted by recommendation score
def cate_filter(score, category, product_list):
    score[np.array(product_list['category']!=category)]=0
    product_list['score']=score
    return product_list.sort('score',ascending=False)

# recommend list of product in [category] by comparing [usrProfile]
# with [simMatrix]
def recommender(simMatrix, usrProfile, category, product_list):
    
    print "Making recommendations score..."
    # score = simMatrix[usrProfile].sum(0)
    score = simMatrix[usrProfile[0]]
    score[score==0]=float('nan')
    # score=np.nanmean(score,0)
    score=np.array(usrProfile[1])*np.array(score).transpose()
    score = np.nanmean(score,1)
    product_c = cate_filter(score,category,product_list)
    
    # normalizing the score such that it's 1-5
    product_c['score']=product_c['score']/product_c['score'].max()*4+1
    return product_c

def prepare_itemcentric():
    product_list = sql2df('select distinct product_id, category from Product order by category, brand;')
    product_id = product_list['product_id'].tolist()
    reviewer_list = sql2df("""select reviewer_id from 
        (select reviewer_id, reviewer_name, count(Review.review_id) as c 
        from Reviewer join Review
        where Review.review_id = Reviewer.review_id 
        group by reviewer_id 
        order by reviewer_id) 
        as review_counts 
        where review_counts.c > 4;""")
    reviewer_id = reviewer_list['reviewer_id'].tolist()
    ratings = sql2df("""select reviewer_id, product_id, rating
            from Reviewer join Review
            where Review.review_id = Reviewer.review_id """)
    category_list = product_list['category']

    product_reviewer = []
    # Construct a matrix where one dimension is product, the other is reviewer, the value is rating
    # so for each product in the list
    counter = 0
    for product in product_id:
        counter += 1
        if counter %10 ==0:
            print "Product scanned: " + str(counter) + "/1177 ..."
        # grab all the ratings for that product
        product_rating = ratings[ratings['product_id']==product].drop('product_id',1).set_index('reviewer_id').to_dict()['rating']

        score = dict.fromkeys(reviewer_id,0)
        for key in product_rating.keys():
            if key not in reviewer_id:
                continue
            score[key] = product_rating[key]
        product_reviewer.append(score.values())

    print "Calculating similarity score..."
    sim = cosine_similarity(product_reviewer,product_reviewer)
    # sim[sim>.99] = 0

    print "Saving similarity matrix to csv..."
    np.savetxt("sim_product.csv", sim, delimiter=",")
    np.savetxt("sim_product2.csv", sim, delimiter=",", fmt='%.2f')
    return sim

def main():
    # category='face-wash-facial-cleanser'
    # category = 'face-serum'
    category = 'moisturizer-skincare'
    # sim = prepare_itemcentric()
    sim = np.loadtxt("sim_product.csv",delimiter=',')
    product_list = sql2df('select distinct product_id, category from Product order by category, brand;')
    product_c = recommender(sim, [[926, 1166, 559, 1099, 246, 688, 690],[5,4,5,5,5,4,5]], category, product_list)
    print product_c[0:100]


if __name__ == "__main__":
    main()
