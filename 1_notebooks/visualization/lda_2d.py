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


params = {'clf__C': 1, 'lda__iterations': 2000, 'lda__num_topics': 1000}

feature_model = LDAModel(num_topics=params['lda__num_topics'], iterations=params['lda__iterations'])
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
