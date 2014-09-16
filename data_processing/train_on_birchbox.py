import MySQLdb
import pandas as pd
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import operator
import pickle
import random

def main():
    df = sql2df("SELECT * FROM insight.BirchboxReview limit 0,256778;")
    print "Fetched {0} record from database...".format(len(df))
    word_sets = []
    ratings = []

    # 
    id = 0
    error = 0
    while id < len(df):
        stopwords = nltk.corpus.stopwords.words('english')
        stemmer   = SnowballStemmer("english")
        word_set  =  extract_feature_from_review(df.ix[id],stopwords,stemmer)
        if word_set:
            word_sets.append(word_set)
            print id, word_set
        else:
            error +=1
        id+=1        
    # print "example of word sets..."
    # print word_set[:10]

    # Built vocabulary and ignore list
    vocabulary = Counter()
    for (word_set,r) in word_sets:
        for w in word_set:
            vocabulary[w]+=1
    f=open('vocabulary.csv','w')
    v = sorted(vocabulary.iteritems(), key=operator.itemgetter(1), reverse=True)
    for key, count in v:
        f.writelines(key+','+str(count)+'\n')
    f.close()

    ignore = []
    for w in vocabulary:
        if vocabulary[w]==1:
            ignore.append(w)
    ignore.extend(['skin','product','face','eye','thing','use','make','get','think','see','wash','put'])
    print "Built vocabulary of length {0}...\nBuilt ignore list of length {1}...".format(len(vocabulary),len(ignore))

    f=open('ignore.text','w')
    f.write(','.join(ignore))
    f.close()
    
    featuresets = [(document_features(d,ignore), c) for (d,c) in word_sets]
    print "Converted reviews into {0} feature sets...".format(len(featuresets))
    balanced_featuresets = balance_featuresets(featuresets)
    print "After balancing, {0} feature sets used for training...".format(len(balanced_featuresets))

    for itera in range(10):
        print "Trial "+str(itera) +"..."
        tp = int(round(len(balanced_featuresets)/10))
        random.shuffle(balanced_featuresets) #23.1 ms
        train_set, test_set = balanced_featuresets[tp:], balanced_featuresets[:tp] #5.47 ms
        classifier = nltk.NaiveBayesClassifier.train(train_set) #329 ms
        # classifier = nltk.DecisionTreeClassifier.train(train_set)
        accuracy = nltk.classify.accuracy(classifier, test_set) #232 ms"

        labels = [test[1] for test in test_set]
        predicted_labels = [ classifier.classify(test[0]) for test in test_set]
        # Precision, which indicates how many of the items that we identified were relevant, is TP/(TP+FP).
        # Recall, which indicates how many of the relevant items that we identified, is TP/(TP+FN).
        (precision,recall) = precision_recall(labels, predicted_labels)
        print "Testing metrics:\n\tAccuracy={0}...\n\tPrecision={1}...\n\tRecall={2}".format(accuracy,precision,recall)

    classifier = nltk.NaiveBayesClassifier.train(balanced_featuresets) #329 ms
    f = open('birch_NB_classifier.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()



def sql2df(sql):
    con = MySQLdb.connect('localhost', 'root', '', 'insight')
    with con:
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        df = pd.read_sql_query(sql,con)
    return df

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

def extract_feature_from_review(review,stopwords,stemmer):
    try:
        review_text = review['review_text']
        rating = review['rating']
        if rating<=2 :
            sentiment = False
        else:
            if (rating==5):
                sentiment = True
            else:
                return ()
        tokens = [word for sent in sent_tokenize(review_text) for word in word_tokenize(sent)]
        text = filter(lambda word: word not in ',.-?!\\//():[--]&;$[<br>][...]\'', tokens)
        words = [w.lower() for w in text if w.lower() not in stopwords]
        words = [stemmer.stem(word).encode('Utf8') for word in words]
        return (words,sentiment)
    except:
        return

def balance_featuresets(featuresets):
    count = sum(1 for f in featuresets if not f[1])
    # len(find([not f[1] for f in featuresets]))
    print count
    balanced_featuresets = []
    for feature in featuresets:
        if feature[1]==False:
            balanced_featuresets.append(feature)
        else:
            if count>0:
                balanced_featuresets.append(feature)
                count-=1
    return balanced_featuresets

def precision_recall(labels, predicted_labels):
# Precision, which indicates how many of the items that we identified were relevant, is TP/(TP+FP).
# Recall, which indicates how many of the relevant items that we identified, is TP/(TP+FN).
    TP = []
    for id in range(len(labels)):
        TP.append(predicted_labels[id] and labels[id])
    precision = float(count_true(TP))/count_true(predicted_labels)
    recall    = float(count_true(TP))/count_true(labels)
    return (precision, recall)

def count_true(alist):
    return sum(1 for a in alist if a)
    

if __name__=="__main__":
    main()