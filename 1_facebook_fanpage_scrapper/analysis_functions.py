import numpy as np
import matplotlib.pyplot as plt

class AnalysisFunctions:

	"""
	Computes the (average, standard deviation), min and max for different function metrics in multiple dataframes.
	"""
	def fun_avgs_maxes_mins(dfs, functions):
		# intialize dicts to hold results
		all_avgs = {}
		all_maxes = {}
		all_mins = {}

		MAX_INT = 999999999

		# iterate over functions
		for func in functions:

			avgs = [(sub, dfs[sub][func.__name__].mean(), np.std(dfs[sub][func.__name__])) for sub in dfs]
			avgs.sort(key=itemgetter(1))
			all_avgs[func.__name__] = avgs

			# compute, sort, and store maxes
			maxes = []
			for sub in dfs:
				post_title = ""
				num_reactions = 0
				tmp = 0
				for val, title, reactions in zip(dfs[sub][func.__name__], dfs[sub]["post_title"], dfs[sub]["num_reactions"]):
					if val > tmp:
						post_title = title
						num_reactions = reactions
						tmp = val
				maxes.append((sub, tmp, num_reactions, post_title))

			maxes.sort(key=itemgetter(1))
			all_maxes[func.__name__] = maxes

			mins = [(sub, dfs[sub][func.__name__].min()) for sub in dfs]

			mins = []
			for sub in dfs:
				post_title = ""
				num_reactions = 0
				tmp = MAX_INT
				for val, title, reactions in zip(dfs[sub][func.__name__], dfs[sub]["post_title"], dfs[sub]["num_reactions"]):
					if val < tmp and val != 0:
						post_title = title
						num_reactions = reactions
						tmp = val
				mins.append((sub, tmp, num_reactions, post_title))

			mins.sort(key=itemgetter(1))
			all_mins[func.__name__] = mins
			
		# return result
		return all_avgs, all_maxes, all_mins


	"""
	Graphs a field vs a metric 
	Args:
		String metric: metric to use for x axis
		String field: field to use for y axis
		String title: title for graph
		Dictionary dfs: dict of subreddit to dataframe
		List subreddits: list of subreddit names
		(Optional) Float xmax: highest x to show in graph
	"""
	def graph_field_vs_metric(metric, field, title, df, xmax=None, all=None):
		# initialize lists for storing all xs and ys
		all_x = []
		all_y = []
		# get metric data
		x = df[metric]
		all_x += [i for i in x]
		# make plot
		plt.figure()
		plt.title(title)
		# get y and scatter
		y = df[field]
		all_y += [i for i in y]
		plt.scatter(x,y,all_x,all_y, alpha=0.5)
		# axes
		plt.xlabel(metric)
		plt.ylabel(field)
		if xmax is not None:
			plt.xlim(0,xmax)
		# show plot
		plt.show()
		return