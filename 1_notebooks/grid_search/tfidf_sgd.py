import os
import numpy as np
import pandas as pd

dataset = pd.read_json("../data/preprocessed.json")
dataset = dataset.reset_index(drop=True)

def in_arange(s, e, step):
    return np.append(np.arange(s, e, step), e)

#################################################

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedKFold
skf = StratifiedKFold(dataset["highest_reaction"], n_folds=10)

param_grid = {'vect__ngram_range': [(1, 2)],
              'vect__min_df': [1],
              'vect__max_df': [1.0],
              'tfidf__use_idf': [True],
              'clf__loss':["modified_huber"],
              'clf__penalty':["l2"],
              'clf__alpha':[1.0000000000000001e-05],
              'clf__n_iter': [10000],
}

pipe_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf',  SGDClassifier())])

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
