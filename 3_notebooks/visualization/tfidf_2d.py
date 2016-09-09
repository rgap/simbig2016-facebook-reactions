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

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

params = {'vect__ngram_range': (1, 2), 'tfidf__use_idf': True, 'clf__C': 0.29999999999999999, 
          'vect__min_df': 2, 'vect__max_df': 1.0}

vectorizer = CountVectorizer(ngram_range=params['vect__ngram_range'],
                             min_df=params['vect__min_df'], max_df=params['vect__max_df'])
compressed_matrix = vectorizer.fit_transform(dataset["preprocessed_stem_stop"])
compressed_matrix = TfidfTransformer().fit_transform(compressed_matrix)
X = pd.DataFrame(compressed_matrix.toarray(), index=dataset.index)
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
