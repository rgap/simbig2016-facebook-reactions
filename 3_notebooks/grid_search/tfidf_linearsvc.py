import os
import numpy as np
import pandas as pd

dataset = pd.read_json("../data/preprocessed.json")
dataset = dataset.reset_index(drop=True)

def in_arange(s, e, step):
    return np.append(np.arange(s, e, step), e)

#################################################

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn import svm
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedKFold
skf = StratifiedKFold(dataset["highest_reaction"], n_folds=10)

# param_grid = {'vect__ngram_range': [(1, 1), (1, 2), (2, 2)],
#               'vect__min_df': in_arange(1, 30, 1),
#               'vect__max_df': in_arange(0.7, 1.0, 0.1),
#               'tfidf__use_idf': [True],
#               'clf__C': in_arange(0.1, 2.0, 0.3),
# }

# param_grid = {'vect__ngram_range': [(1, 2)],
#               'vect__min_df': in_arange(1, 20, 1),
#               'vect__max_df': in_arange(0.01, 0.5, 0.1),
#               'tfidf__use_idf': [True],
#               'clf__C': in_arange(0.1, 2.0, 0.1),
# }

## TOO MANY FEATURES with min_df = 1 (this gives 0.73 but it has 5 times more features than with 2)
# param_grid = {'vect__ngram_range': [(1, 2)],
#               'vect__min_df': [1],
#               'vect__max_df': in_arange(0.01, 0.2, 0.01),
#               'tfidf__use_idf': [True],
#               'clf__C': [1.5],
# }

param_grid = {'vect__ngram_range': [(1, 2)],
              'vect__min_df': [2],
              'vect__max_df': [1.0],
              'tfidf__use_idf': [True],
              'clf__C': in_arange(0.05, 2.0, 0.05),
}

pipe_clf = Pipeline([('vect', CountVectorizer()),
                    ('tfidf', TfidfTransformer()),
                    ('clf', svm.LinearSVC())])

clf_grid = GridSearchCV(pipe_clf, 
                        param_grid=param_grid,
                        scoring="accuracy",
                        n_jobs=-1,
                        cv=skf,
                        verbose=1)

fitted = clf_grid.fit(dataset["preprocessed_stem_stop"], dataset["highest_reaction"])

print("best_params_: {}\n".format(clf_grid.best_params_))
print("best_score_: {}\n".format(clf_grid.best_score_))

# Best parameters
with open(os.path.splitext(os.path.basename(__file__))[0] + ".txt", 'w') as output:
    output.write("best_params_: {}\n\n".format(clf_grid.best_params_))
    output.write("best_score_: {}\n".format(clf_grid.best_score_))
