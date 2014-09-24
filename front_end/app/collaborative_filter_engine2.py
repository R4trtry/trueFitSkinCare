import MySQLdb
import pandas as pd
import numpy as np
import math


# get data from database in the form of pandas dataframe
# given a sql script
def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', 'dumbled0re', 'insight', charset='utf8')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql(sql,con)
    return df

# filter the recommendations with category 
# return a list sorted by recommendation score
def cate_filter(score, category, product_list):
    score[np.array(product_list['category']!=category)]=0
    product_list['score']=score
    product_list = product_list.dropna()
    print product_list[:10].sort('score',ascending=False)
    return product_list.sort('score',ascending=False)

# recommend list of product in [category] by comparing [usrProfile]
# with [simMatrix]
def recommender(simMatrix, usrProfile, category, product_list):
    
    print "Making recommendations score..."
    # score = simMatrix[usrProfile].sum(0)
    score = simMatrix[usrProfile]
    score[score==0]=float('nan')
    score=np.nanmean(score,0)
    product_c = cate_filter(score,category,product_list)
    print product_c[:10] 
    # normalizing the score such that it's 1-5
    product_c['score']=product_c['score']/product_c['score'].max()*4+1
    return product_c


#---------------------------------------------------------------#
# below are used for training, not used in the front end app    #
#---------------------------------------------------------------#
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
    for product in product_id:
        print "product id: " + product + "..."
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
    sim[sim>.99] = 0

    print "Saving similarity matrix to csv..."
    np.savetxt("sim_product.csv", sim, delimiter=",")
    np.savetxt("sim_product2.csv", sim, delimiter=",", fmt='%.2f')
    return sim

def main():
    # category='face-wash-facial-cleanser'
    category = 'face-serum'
    sim = prepare_itemcentric()
    product_list = sql2df('select distinct product_id, category from Product order by category, brand;')
    product_c = recommender(sim, [123,293,902,694,381], category, product_list)
    print product_c[0:10]
    # return product_c[0:10]
    result = product_c[:10]
    result = result.drop('category',1)
    result = result.set_index('product_id')
    return result.to_json()


if __name__ == "__main__":
    main()
