import os
import numpy as np
import pandas as pd

dataset = pd.read_json("../data/preprocessed.json")
dataset = dataset.reset_index(drop=True)

def in_arange(s, e, step):
    return np.append(np.arange(s, e, step), e)

#################################################

## Creating a feature model to use it with gridsearchcv
from sklearn.base import BaseEstimator
from gensim import corpora
from gensim.models import ldamodel

 
class LDAModel(BaseEstimator):
    def __init__(self, num_topics=10, iterations=100):
        self.lda = None
        self.num_topics = num_topics
        self.iterations = iterations
 
    def fit(self, raw_documents, y=None):
        # Convert to tokens 2d matrix
        documents = [d.split() for d in raw_documents]
        # Build a corpus and extract features
        self.dictionary = corpora.Dictionary(documents)
        corpus = [self.dictionary.doc2bow(doc) for doc in documents]
        np.random.seed(0)  # Set a fixed seed cuz it's non-deterministic
        self.lda = ldamodel.LdaModel(corpus, id2word=self.dictionary, 
                                     num_topics=self.num_topics, iterations=self.iterations,
                                     alpha='symmetric', gamma_threshold=0.001, eta=None)
        return self
  
    def transform(self, raw_documents):
        X_output = []
        documents = [d.split() for d in raw_documents]
        for document in documents:
            # Filling with 0's
            topic_distribution = [0.0] * self.num_topics
            pred = self.lda[self.dictionary.doc2bow(document)]
            for t in pred:
                topic_distribution[t[0]] = t[1]
            X_output.append(topic_distribution)
        return np.array(X_output)

    def fit_transform(self, raw_documents, y=None):
        self.fit(raw_documents)
        return self.transform(raw_documents)

#################################################

from sklearn import svm
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedKFold
skf = StratifiedKFold(dataset["highest_reaction"], n_folds=10)


param_grid = {'lda__num_topics': [1000, 1500, 2000],
              'lda__iterations': [2000],
              'clf__C': [0.3, 1.0],
}

pipe_clf = Pipeline([('lda', LDAModel()),
                    ('clf', svm.LinearSVC())])

clf_grid = GridSearchCV(pipe_clf, 
                        param_grid=param_grid,
                        scoring="accuracy",
                        n_jobs=-1,
                        cv=skf,
                        verbose=3)

fitted = clf_grid.fit(dataset["preprocessed_stem_stop"], dataset["highest_reaction"])

print("best_params_: {}\n".format(clf_grid.best_params_))
print("best_score_: {}\n".format(clf_grid.best_score_))

# Best parameters
with open(os.path.splitext(os.path.basename(__file__))[0] + ".txt", 'w') as output:
    output.write("best_params_: {}\n\n".format(clf_grid.best_params_))
    output.write("best_score_: {}\n".format(clf_grid.best_score_))
