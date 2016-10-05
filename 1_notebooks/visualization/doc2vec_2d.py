import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
sns.set_context("paper")    

y_labels = ["love", "haha", "wow", "angry", "sad"]

dataset = pd.read_json("../data/preprocessed.json")
dataset = dataset.reset_index(drop=True)

#############################################


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
        
        for epoch in range(200):
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


params = {'doc2vec__min_count': 2, 'clf__C': 1, 'doc2vec__size': 400}

feature_model = Doc2VecModel(size=params['doc2vec__size'], min_count=params['doc2vec__min_count'])
vectors = feature_model.fit_transform(dataset["preprocessed_stem_stop"])
X = pd.DataFrame(vectors, index=dataset.index)
y = dataset["highest_reaction"]

print("Feature set: {}".format(X.shape))

#############################################

from sklearn.decomposition import PCA

def plot2D_features(features, legend_labels=[], labels=None, num_rows=None, annotate=False,
                    marker_size=40, plot_size=6, annotate_fontsize=0.5):
    if num_rows == None or num_rows > features.shape[0]:
        num_rows = features.shape[0]
    print("PCA...")
    pca = PCA(n_components=2)
    pca.fit(features[:num_rows])
    reduced = pd.DataFrame(pca.transform(features[:num_rows]), columns=["x", "y"], index=features.index[:num_rows])

    print("Plotting...")
    if not labels is None:
        reduced["c"] = labels[:num_rows]
        sns.lmplot("x", "y", data=reduced, hue="c", fit_reg=False, size=plot_size, aspect=2,
                   scatter_kws={"s": marker_size, "linewidths": 0.2, "edgecolor": "black"}, legend=False)
        plt.legend(legend_labels, scatterpoints=1, fontsize=14, fancybox=True, framealpha=0.1, bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
        plt.xlabel("x", fontsize=14)
        plt.ylabel("y", fontsize=14)
        plt.tick_params(labelsize=13)
    else:
        plt.scatter(reduced["x"], reduced["y"], s=marker_size, linewidths=0.2, edgecolor="black", color="green")
        plt.xlabel("x", fontsize=14)
        plt.ylabel("y", fontsize=14)
        plt.tick_params(labelsize=13)
        
    plt.tight_layout()
    if annotate:
        for index, row in reduced.iterrows():
            plt.annotate(index, xy=(row["x"], row["y"]), fontsize=annotate_fontsize)    
    plt.savefig('../notebook_figures/{}.pdf'.format(os.path.splitext(os.path.basename(__file__))[0]),
                bbox_inches='tight')
    plt.savefig('../notebook_figures/{}.png'.format(os.path.splitext(os.path.basename(__file__))[0]),
                bbox_inches='tight', dpi=600)
    plt.show()

plot2D_features(X, labels=y, legend_labels=y_labels, annotate=False)
