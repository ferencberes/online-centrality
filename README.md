online-centrality
=================

This repository contains the code used in the Online Centrality research of [Ferenc Béres and András A. Benczúr](https://dms.sztaki.hu/en/tagok).

# Introduction

Online Centrality is a centrality measure updateable by the
edge stream in a dynamic network. It incorporates the elapsed time of edge activations as time decay.

## Cite

I presented a [poster](https://github.com/ferencberes/online-centrality/blob/master/documents/complex_networks_2017_poster.pdf) at the 6th International Conference on Complex Networks and Their Applications. You can see our work in the [Book of Abstracts](http://past.complexnetworks.org/BookOfAbstracts.pdf#page=198) as well. 

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

# Requirements

   * UNIX environment
   * **Python 3.5** conda environment with pre-installed jupyter:

   ```bash
   conda create -n YOUR_CONDA_PY3_ENV python=3.5 jupyter
   source activate YOUR_CONDA_PY3_ENV
   ```
   * Install the following packages with *conda* or *pip*:
      * **data processing:** pandas, numpy, bs4
      * **scientific:** scipy, networkx 
      * **visualization:** matplotlib, seaborn
      * **general:** sys, os, math, re, json, shutil, operator, collections, multiprocessing, functools, itertools, datetime


# Usage

In this repository you can find the codebase that we using during our research. **The Roland-Garros 2017 dataset is available on the website of our research group [SZTAKI DMS](https://dms.sztaki.hu/hu/letoltes/roland-garros-2017-twitter-collection).**

You can simply run all the following steps with one script but it will take many time. Look for details in this section **"Calculate centrality scores"**.

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/run_all.sh
```

If you read further, you can see the details and instructions related to each task in our experimental setting. 

## i.) Data

The dataset is not part of this repository. You can download the data with the following command

```bash
bash ./scripts/download_data.sh
```

After you executed the previous script, you can find the uncompressed raw data in folder **./data/raw**.

### Schedule information

In folder **./data/raw/schedule**, you can find HTML and PDF files downloaded from the official [website](http://www.rolandgarros.com/en_FR/scores/schedule/) of Roland-Garros 2017.

### Twitter mention network

The mention network is provided in the following file, ehich consists of 3 columns.

```bash
head -5 data/raw/rg17_mentions.csv
```

```
1495576813 127836 127836
1495576832 83738 90241
1495576832 83738 100020
1495576840 73667 61794
1495576840 73667 65554
```

The first column is the UNIX timestamp, the second is the source and the third column is the target of the given mention. For example the first row (1495576813,127836,127836) represents that node 127836 mentioned node 127836 at May 23, 2017 10:00:13 PM GMT time (May 24, 2017 00:00:13 AM GMT+2 time - Paris timezone). All node identifiers in this file are hashed, so most of them cannot be linked to any Twitter account.

### Tennis players in the dataset

In order to show the impact of our results we also provide our Twitter account to tennis player assigments:

```bash
head -5 data/raw/tennis_player_matches.csv
```

```
generated_id|screen_name|player_name
88736|AdrianMannarino|Adrian Mannarino
17016|Ajlatom|Ajla Tomljanovic
41651|Alarosolska|Alicja Rosolska
24999|AleGonzalezpro|Alejandro Gonzalez
```

The first columns **generated_id** correcponds to the node identifiers mentioned in the previous section. The second column **screen_name** is  an account identifier of the node on Twitter. Finally, **player_name** is the name of the tennis player that we assigned to this node from the official event schedule. Here we only list the accounts of tennis players of Roland-Garros 2017 that we could identify with our semi-automatic assigment method. 

## ii.) Pipelines

In order to make my experiments reproducible I use JSON [configuration files](pipelines/). The parameters in these files can be easily managed by a few pre-provided Jupyter notebooks. [These](ipython/parameters/) parameter notebooks also tailor file paths to your working directory. So **always run the parameter notebook before running any other notebooks from any pipeline.** 

If you run notebooks with the following bash scripts then all parameter notebooks will be executed automatically in the right order.

### 1. Preprocessing data

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/preprocess_data.sh
```

**Related notebooks**

   *  There is only one [preprocessor notebook](ipython/preprocessing/ScheduleScoreUpdater.ipynb) that you have to run before further experiment tasks.

### 2. Calculate centrality scores

You can calculate centrality scores for hourly snapshots with the following script.

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/calculate_centrality_scores.sh
```

**It could take even more than an hour** to calculate the scores for all parametrizations that is required for the following steps. That is the reason why in the following notebook an additional configuration **--ExecutePreprocessor.timeout=5400** is used with the **jupyter nbconvert** command. If the execution don't finish in 90 minutes on your computer then you should increase this time limit.

**Related notebooks**

   * [parameter notebook](ipython/parameters/centrality_params.ipynb) for centrality score computation
   * [score calculator notebook](ipython/experiments/centrality_score_computer.ipynb), that will export score files into folder **./data/centrality_scores**.

#### Notations of centrality scores

   * *olr*: Online Centrality - our model
   * *tpr*: Temporal PageRank
   * *spr*: static PageRank
   * *hc*: static Harmonic Centrality
   * *nbm*: static negative-Beta Measure
   * *indeg*: static Indegree

### 3. Evaluation

You can run all the remaining experiments with the following script:

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/run_experiments.sh
```

**Related notebooks**

   * You can compute the the ratio of nodes with non-constant Online Centrality score with [this](ipython/experiments/roland_garros_olr_const_ratios.ipynb) notebook.
   * You can also evaluate how efficiently can the formerly mentioned centrality measures predict daily tennis players in advance if you execute [this](ipython/experiments/roland_garros_predict_player.ipynb) notebook.

# Troubleshooting

If you get a **"TimeoutError: Cell execution timed out"** when you run any of the bash scripts then you should increase the execution time limit for the **jupyter nbconvert** command for the notebook that had broken down. You can do this by using **jupyter nbconvert --to notebook --execute  --ExecutePreprocessor.timeout=HIGHER\_TIME\_LIMIT BROKEN_DOWN_NOTEBOOK.ipynb** or just execute the given notebook through the Jupyter browser.
