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

def cate_filter(score, category, product_list):
    score[np.array(product_list['category']!=category)]=0
    product_list['score']=score
    return product_list.sort('score',ascending=False)

def recommender(ratingMatrix, test, category, product_list):
    similarity = cosine_similarity(test, ratingMatrix)[0]
    count = np.array([len(row.nonzero()[0]) for row in ratingMatrix.transpose()])
    score = ratingMatrix.transpose()*(similarity**5)
    product_c = cate_filter(score/count,category,product_list)
    print product_c['score'].max()
    product_c['score']=product_c['score']/product_c['score'].max()*5
    return product_c

def prepare():
    product_list = sql2df('select distinct product_id, category from Product order by category;')
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

    reviewer_product = {}
    for reviewer in reviewer_id:
        product_rating = ratings[ratings['reviewer_id']==reviewer].drop('reviewer_id', 1).set_index('product_id').to_dict()['rating']
        score = dict.fromkeys(product_id,0)
        for key in product_rating.keys():
            score[key] = product_rating[key]
        reviewer_product[reviewer] = score.values()

    return csr_matrix(reviewer_product.values())


def main():
    test    = 21   
    category='face-wash-facial-cleanser'
    ratingMatrix = prepare()
    product_list = sql2df('select distinct product_id, category from Product order by category;')
    product_c = recommender(ratingMatrix, ratingMatrix[test:(test+1)], category, product_list)
    print product_c[0:10]
    # return product_c[0:10]
    result = product_c[:10]
    result = result.drop('category',1)
    result = result.set_index('product_id')
    return result.to_json()


if __name__ == "__main__":
    main()
