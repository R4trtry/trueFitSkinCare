import pickle
import MySQLdb
import pandas as pd
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import operator
from sklearn.metrics.pairwise import cosine_similarity

f = open('birch_NB_classifier.pickle')
classifier = pickle.load(f)
f.close()

def main():
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

def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df

def extract_feature_from_review(review,stopwords,stemmer):
    review_text = review['review_text']
#         review_text = review['quick_take']
    rating = review['rating']
    if rating<=2 :
        sentiment = False
    else:
        if (rating==5):
            sentiment = True
        else:
            sentiment = 'nan'
#                 return ()
    tokens = [word for sent in sent_tokenize(review_text) for word in word_tokenize(sent)]
    text = filter(lambda word: word not in ',.-?!\\//():[--]&;$[<br>][...]\'', tokens)
    words = [w.lower() for w in text if w.lower() not in stopwords]
    wordstem = []
    for word in words:
        try:
            wordstem.append(stemmer.stem(word))
        except:
            continue
#         words = [stemmer.stem(word).encode('Utf8') for word in words]
#         return (words,sentiment)
    return (wordstem,sentiment)
    
def document_features(document,ignore):
    document_words = set(document) 
    features = {}
    if ignore:
        for word in document:
            if word not in ignore:
                features[word] = True
    else:
        for word in document:
            features[word] = True
    return features

def precision_recall(labels, predicted_labels):
    TP = []
    for id in range(len(labels)):
        TP.append(predicted_labels[id] and labels[id])
    precision = float(len(find(TP)))/len(find(predicted_labels))
    recall    = float(len(find(TP)))/len(find(labels))
    return (precision, recall)

    from sklearn.metrics.pairwise import cosine_similarity


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

    category_list = product_list['category']

    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = SnowballStemmer("english")

    product_reviewer = []
    # Construct a matrix where one dimension is product, the other is reviewer, the value is rating
    # so for each product in the list
    for product in product_id:
        print "product id: " + product + "..."
        # grab all the ratings for that product
        # df = sql2df("select review_id, rating, review_text from review where product_id='P7109' and (rating<=2 or rating=5) ")
        df = sql2df("select reviewer_id, rating, review_text, quick_take from review join reviewer where review.review_id=reviewer.review_id and product_id='{0}'".format(product))
    #         len(df)

        sentiment = []
        product_prob = {}
        for id in range(len(df)):
            feature = extract_feature_from_review(df.ix[id],stopwords,stemmer)
            feature = document_features(feature[0],())
            sentiment.append(classifier.classify(feature))
            pdist = classifier.prob_classify(feature)
            product_prob[df.ix[id]['reviewer_id']]=pdist.prob(True)
    #             prob.append()
    #     print product_prob
        
        score = dict.fromkeys(reviewer_id,0)
        for key in product_prob.keys():
            if key not in reviewer_id:
                continue
            score[key] = product_prob[key]
        product_reviewer.append(score.values())
    #     break
        
    print "Calculating similarity score..."
    sim = cosine_similarity(product_reviewer,product_reviewer)
    sim[sim>.99] = 0

    print "Saving similarity matrix to csv..."
    np.savetxt("sim_product_review.csv", sim, delimiter=",")
    np.savetxt("sim_product_review2.csv", sim, delimiter=",", fmt='%.2f')
    return sim

def recommender(simMatrix, usrProfile, category, product_list):
    # score = ratingMatrix.transpose()*(similarity[])
    score = simMatrix[usrProfile].sum(0)
    print "Making recommendations score..."
    product_c = cate_filter(score,category,product_list)
    print product_c['score'].max()
    product_c['score']=product_c['score']/product_c['score'].max()*4+1
    return product_c

if __name__ == '__main__':
    main()