online-centrality
=================

This repository contains the code used in the Online Centrality research of [Ferenc Béres](https://ferencberes.github.io/), [Róbert Pálovics](https://github.com/rpalovics) and András A. Benczúr at the [Institute for Computer Science and Control of the
Hungarian Academy of Sciences](https://dms.sztaki.hu/en).

# Introduction

Online Centrality is a centrality measure updateable by the
edge stream in a dynamic network. It incorporates the elapsed time of edge activations as time decay.

# Requirements

   * UNIX environment
   * **Python 3.5** conda environment with pre-installed jupyter:

   ```bash
   conda create -n YOUR_CONDA_PY3_ENV python=3.5 jupyter
   source activate YOUR_CONDA_PY3_ENV
   ```
   * Install the following packages with *conda* or *pip*:
      * **data processing:** pandas, numpy
      * **scientific:** scipy, networkx 
      * **visualization:** matplotlib, seaborn
      * **general:** sys, os, math, re, json, shutil, operator, collections, multiprocessing, functools, itertools, datetime

# Data

In this repository you can find the codebase that we are using in our research. **The USOpen 2017 dataset is available on the website of our [research group](https://dms.sztaki.hu/hu/letoltes/online-centrality-data-sets)** at the Institute for Computer Science and Control of the
Hungarian Academy of Sciences.

You can also download all related data sets with the following command
```bash
bash ./scripts/download_data.sh
```

# Usage

After you have downloaded the data sets (see previous section) you can run the experiments with the provided scripts or you can experiment with the Jupyter notebooks as well.

You can simply run all the following steps with one script but it will take many time. Look for details in the next section (Calculate centrality scores).

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/run_all.sh
```

If you read further, you can see the details and instructions related to each task in our experimental setting. 

## 1. Calculate centrality scores

You can calculate centrality scores for hourly snapshots with the following script.

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/calculate_centrality_scores.sh
```

**It could take several hours** to calculate the scores for all parametrizations that is required for the following steps. That is the reason why we use **--ExecutePreprocessor.timeout=7200** configuration for  the **jupyter nbconvert** command. If the execution don't finish in 2 hours on your computer then you should increase this time limit.

**Related notebooks (execute them in this order):**

   * [parameter notebook](ipython/parameters/centrality_params.ipynb):  setting parameters for centrality score computation
   * [score calculator notebook](ipython/experiments/centrality_score_computer.ipynb): export score files into folder **./data/centrality_scores/usopen_epoch_t505_d3600**.

#### Notations of centrality scores

   * *olr*: Online Centrality - our model
   * *tpr*: Temporal PageRank
   * *spr*: static PageRank
   * *hc*: static Harmonic Centrality
   * *nbm*: static negative-Beta Measure
   * *indeg*: static indegree
   * *olid*: decayed indegree

## 2. Experiments

You can run the experiments with the following script:

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/run_experiments.sh
```

**Related notebooks (execute them in this order):**

   * [parameter notebook](ipython/parameters/USOParams.ipynb):  setting parameters for centrality score computation
   * [USOpen evaluator notebook](ipython/experiments/uso_predict_player.ipynb): Evaluate centrality measure toplists based on daily tennis players of US Open 2017.
   * [Concept drift notebook](ipython/experiments/ConceptDrift.ipynb): Unsupervised evaluation for concept drifts. 

# Cite

### Complex Networks 2017

A former version of our research was presented at the 6th International Conference on Complex Networks and Their Applications. You can see our work in the [Book of Abstracts](http://past.complexnetworks.org/BookOfAbstracts.pdf#page=198) or on the [poster](https://github.com/ferencberes/online-centrality/blob/master/documents/complex_networks_2017_poster.pdf) that I presented.

Please cite our work if you use this code or the [Roland-Garros 2017 dataset](https://dms.sztaki.hu/hu/letoltes/roland-garros-2017-twitter-collection):

```
@conference{beres17oc,
  author       = {Ferenc Béres and András A. Benczúr}, 
  title        = {Online Centrality in Temporally Evolving Networks},
  booktitle    = {Book of Abstracts of the 6th International Conference on Complex Networks and Their Applications},
  pages        = {184--186},
  year         = {2017},
  isbn = {978-2-9557050-2-5},
}
```

You can find the related codebase on a different [branch](https://github.com/ferencberes/online-centrality/tree/complex_networks_2017).

# Troubleshooting

If you get a **"TimeoutError: Cell execution timed out"** when you run any of the provided bash scripts then you should increase the execution time limit for the **jupyter nbconvert** command for the notebook that had broken down. You can do this by using

```bash
jupyter nbconvert --to notebook --execute  --ExecutePreprocessor.timeout=HIGHER_TIME_LIMIT BROKEN_DOWN_NOTEBOOK.ipynb
```
 
 or just execute the given notebook through the Jupyter browser.
