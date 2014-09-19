import re
import MySQLdb
import pandas as pd
import numpy as np
import math
from sklearn.metrics.pairwise import cosine_similarity
import random

def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df

def cate_filter(score, category, product_list):
    score[np.array(product_list['category']!=category)]=float('nan')
    score = [math.sqrt(s) for s in score]
    product_list['score']=score
    return product_list.sort('score',ascending=False)

def recommender(simMatrix, usrProfile, category, product_list, rating):
    # score = ratingMatrix.transpose()*(similarity[])
    count = np.array([len(row.nonzero()[0]) for row in simMatrix.transpose()])
    score = simMatrix[usrProfile]
    score[score==0]=float('nan')
    if not rating:
        score=np.nanmean(score,0)
    else:
        score=np.array(rating)*np.array(score).transpose()
        score = np.nanmean(score,1)
        
#     print "Making recommendations score..."
    product_c = cate_filter(score/count,category,product_list)
#     print product_c['score'].max()
#     product_c['score']=product_c['score']/product_c['score'].max()*4+1
    return product_c['product_id'].tolist()

# def train_itemcentric():
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
reviewer_test = sql2df("""select reviewer_id from 
    (select reviewer_id, reviewer_name, count(Review.review_id) as c 
    from Reviewer join Review
    where Review.review_id = Reviewer.review_id 
    group by reviewer_id 
    order by reviewer_id) 
    as review_counts 
    where review_counts.c >=5;""")
reviewer_id = reviewer_list['reviewer_id'].tolist()


for iteration in range(10):
    print "iteration", iteration, '...'
    reviewer_id = reviewer_list['reviewer_id'].tolist()
    reviewer_id_test = reviewer_test['reviewer_id'].tolist()
    random.shuffle(reviewer_id_test)
    reviewer_id_test = reviewer_id_test[:800]

    reviewer_id_train = list(set(reviewer_id)-set(reviewer_id_test))
    # print "Use {0} reviewers for training, {1} reviewers for testing".format(len(reviewer_id_train),len(reviewer_id_test))

    ratings = sql2df("""select reviewer_id, product_id, rating
            from Reviewer join Review
            where Review.review_id = Reviewer.review_id """)
    category_list = product_list['category']

    product_reviewer = []
    # Construct a matrix where one dimension is product, the other is reviewer, the value is rating
    # so for each product in the list
    # counter = 0
    for product in product_id:
        # counter += 1
        # if counter %100 ==0:
            # print "Product scanned: " + str(counter) + "/1177 ..."
        # grab all the ratings for that product
        product_rating = ratings[ratings['product_id']==product].drop('product_id',1).set_index('reviewer_id').to_dict()['rating']

        score = dict.fromkeys(reviewer_id_train,0)
        for key in product_rating.keys():
            if key not in reviewer_id_train:
                continue
            score[key] = product_rating[key]
        product_reviewer.append(score.values())

    print "Calculating similarity score..."
    sim = cosine_similarity(product_reviewer,product_reviewer)

    # reviewer_id_test
    test_data = []
    # counter = 0
    for reviewer_id in reviewer_id_test:
        # counter+=1
        # if counter % 10 == 0 :
            # print "Scanned reviewers: {0} / {1}...".format(counter, len(reviewer_id_test))
        df = sql2df("""select product.product_id as product_id, rating, category 
                        from review join reviewer join product 
                        where reviewer.review_id=review.review_id 
                        and review.product_id=product.product_id 
                        and reviewer_id={0} and rating>=4;""".format(reviewer_id))
        
        usrLikes = df['product_id'].tolist()
        df['usrProfile'] = [product_id.index(p) for p in usrLikes]
        test_data.append(df.to_dict())
    print "Scanned reviewers: {0} / {1}...".format(len(reviewer_id_test), len(reviewer_id_test))

    cat_count = sql2df("""select category, count(*) from product group by category""")
    cat_count = cat_count.set_index("category").to_dict().values()[0]

    acc = []
    # counter = 0
    for data in test_data:
        # counter+=1
        usrProfile = list(set(data['usrProfile'].values()))
    #     rating = data['rating'].values()
        hit = 0
        miss = 0
        for i in range(1,len(usrProfile)+1):
            category = data['category'][i-1]        
            product_c = recommender(sim, usrProfile[:(i-1)]+usrProfile[i:], category, product_list,())
            if product_c.index(data['product_id'][i-1])<=max(round(cat_count[category]/5),20):
                hit +=1
            else:
                miss +=1
        try:
            uacc = float(hit)/(hit+miss)
        except:
            uacc = 0
            pass
        acc.append([hit, miss, uacc])
        # print counter, hit, miss, float(hit)/(hit+miss)
        
    # plt.hist([c for (a,b,c) in acc], bins=20, range=(0,1)) 
    hits = [a for (a,b,c) in acc]
    misses =[b for (a,b,c) in acc]
    counts = [a+b for (a,b,c) in acc]
    acces =[c for (a,b,c) in acc]
    print float(sum(hits))/sum(counts)
    f = open('crossvalidation_full.csv','a')
    f.write(','.join([str(n) for n in hits])+'\n')
    f.write(','.join([str(n) for n in misses])+'\n')
    f.write(','.join([str(n) for n in counts])+'\n')
    f.write(','.join([str(n) for n in acces])+'\n')
    f.close()
    