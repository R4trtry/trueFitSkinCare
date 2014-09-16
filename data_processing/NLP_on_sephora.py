import pickle
import MySQLdb
import pandas as pd
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import operator
import matplotlib.pyplot as plt

def main():
    f = open('birch_NB_classifier.pickle')
    classifier = pickle.load(f)
    f.close()
    # df = sql2df("select review_id, rating, review_text from review where product_id='P7109' and (rating<=2 or rating=5) ")
    df = sql2df("select review_id, rating, review_text, quick_take from review where product_id='P7109' ")
    len(df)

    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = SnowballStemmer("english")
    sentiment = []
    rating = []
    prob = []
    for id in range(len(df)):
        feature = extract_feature_from_review(df.ix[id],stopwords,stemmer)
        # rating.append(feature[1])
        feature = document_features(feature[0],())
        sentiment.append(classifier.classify(feature))
        pdist = classifier.prob_classify(feature)
        prob.append(pdist.prob(True))
        
    # precision_recall(rating,sentiment)
    # prob
    # sentiment
    plt.plot(sorted([p*4+1 for p in prob]))
    plt.plot(sorted(df['rating']))
    plt.show()


def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df

def extract_feature_from_review(review,stopwords,stemmer):
    # try:
    # review_text = review['review_text']
    review_text = review['quick_take']
    rating = review['rating']
    if rating<=2 :
        sentiment = False
    else:
        if (rating==5):
            sentiment = True
        else:
            sentiment = 'nan'
    tokens = [word for sent in sent_tokenize(review_text) for word in word_tokenize(sent)]
    text = filter(lambda word: word not in ',.-?!\\//():[--]&;$[<br>][...]\'', tokens)
    words = [w.lower() for w in text if w.lower() not in stopwords]
    wordstem = []
    for word in words:
        try:
            wordstem.append(stemmer.stem(word))
        except:
            continue
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
# Precision, which indicates how many of the items that we identified were relevant, is TP/(TP+FP).
# Recall, which indicates how many of the relevant items that we identified, is TP/(TP+FN).
    TP = []
    for id in range(len(labels)):
        TP.append(predicted_labels[id] and labels[id])
    precision = float(count_true(TP))/count_true(predicted_labels)
    recall    = float(count_true(TP))/count_true(labels)
    return (precision, recall)

if __name__ == '__main__':
    main()