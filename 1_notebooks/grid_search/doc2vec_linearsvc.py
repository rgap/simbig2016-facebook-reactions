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
from gensim.models.doc2vec import Doc2Vec, LabeledSentence


class Doc2VecModel(BaseEstimator):
    def __init__(self, size=100, min_count=1):
        self.d2v_model = None
        self.size = size
        self.min_count = min_count
 
    def fit(self, raw_documents, y=None):
        # Initialize
        self.d2v_model = Doc2Vec(dm=0, min_count=self.min_count, window=10, size=self.size, sample=1e-4, negative=6, workers=3)
        # Building a vocabulary
        labeled_sentences = []
        for index, row in raw_documents.iteritems():
            tag = '{}_{}'.format("SENT", index)
            tokens = row.split()
            labeled_sentences.append(LabeledSentence(words=tokens, tags=[tag]))
        self.d2v_model.build_vocab(labeled_sentences)
        
        for epoch in range(300):
            np.random.shuffle(labeled_sentences)
            self.d2v_model.train(labeled_sentences)
            # self.d2v_model.alpha -= 0.002  # decrease the learning rate
            # self.d2v_model.min_alpha = self.d2v_model.alpha  # fix the learning rate, no decay

        return self
  
    def transform(self, raw_documents):
        X = []
        for index, row in raw_documents.iteritems():
            X.append(self.d2v_model.infer_vector(row))
        X = pd.DataFrame(X, index=raw_documents.index)
        return X

    def fit_transform(self, raw_documents, y=None):
        self.fit(raw_documents)
        return self.transform(raw_documents)

#################################################

from sklearn import svm
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedKFold
skf = StratifiedKFold(dataset["highest_reaction"], n_folds=3)


param_grid = {'doc2vec__size': [300, 400],
              'doc2vec__min_count': [2,4,8,16],
              'clf__C': [1, 2],
}

pipe_clf = Pipeline([('doc2vec', Doc2VecModel()),
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
