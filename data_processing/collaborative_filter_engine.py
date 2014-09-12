import re
import MySQLdb
import pandas as pd
# import 
import numpy as np
import math
from scipy.sparse import csr_matrix
from scipy.sparse import isspmatrix_csc
from sklearn.metrics.pairwise import cosine_similarity

def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df
        
product_list = sql2df('select distinct product_id from Product order by category;')['product_id']
product_id = product_list.tolist()
reviewer_id = sql2df("""select reviewer_id from 
    (select reviewer_id, reviewer_name, count(Review.review_id) as c 
    from Reviewer join Review
    where Review.review_id = Reviewer.review_id 
    group by reviewer_id 
    order by c desc) 
    as review_counts 
    where review_counts.c > 1;""")['reviewer_id'].tolist()
ratings = sql2df("""select reviewer_id, product_id, rating
        from Reviewer join Review
        where Review.review_id = Reviewer.review_id """)

reviewer_product = {}
for reviewer in reviewer_id:
    product_rating = ratings[ratings['reviewer_id']==reviewer].drop('reviewer_id', 1).set_index('product_id').to_dict()['rating']
    score = dict.fromkeys(product_id,0)
    for key in product_rating.keys():
        score[key] = product_rating[key]
    reviewer_product[reviewer] = score.values()

csr_Rv_Pd = csr_matrix(reviewer_product.values())

test = csr_Rv_Pd[150:151]
result = cosine_similarity(test, csr_Rv_Pd)[0]

print product_list[find(result>.5)].dropna()
#plt.hist(result[result>.5],bins=10)
