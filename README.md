Reproduce the Experiments in "[Predicting Reactions to Blog Headlines](http://bit.ly/2czObz2)" - It isn't published yet!

## Environment

- Mac OS X El Capitan
- Python 3
- Python packages are listed on requirements.txt
NOTE: Some of them had to be installed from their source code, you need to install them if you want to run the notebooks in localhost.

## Help lectures

Some useful lectures about feature models and useful stuff are on "lectures" folder.

## Getting started

### Checkout the Project

```sh
git clone https://github.com/rgap/simbig2016-facebook-reactions.git
```

### Facebook scraper

Facebook data has been extracted using my "[Facebook fanpage scrapper](https://github.com/rgap/facebook-fanpage-scraper)". Although, you will be able to understand and reproduce my experiments just by executing the Jupyter notebooks.

### Notebooks

Right after having extracted all data from a list of facebook fanpages, I saved my dataset on.

1_notebooks/data/facebook_pages_data.json

It is the only dataset I used on my paper. If you want to reproduce the experiments you should check out each ".ipynb" file.

### Paper and its latex source code

The paper latex source code is located in

2_paper/acl2016.tex
