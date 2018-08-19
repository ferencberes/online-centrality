Temporal Katz centrality
========================

This repository contains the code related to the shared research of [Ferenc Béres](https://github.com/ferencberes), [Róbert Pálovics](https://github.com/rpalovics) and András A. Benczúr. If you are interested then you can read the full [paper](https://appliednetsci.springeropen.com/articles/10.1007/s41109-018-0080-5) or check out the [poster](documents/mlg_2018_poster.pdf) that I presented at the 14th International Workshop on
Mining and Learning with Graphs (KDD18).

# Cite

Please cite our work if you use this code or the [Twitter tennis datasets](https://dms.sztaki.hu/en/letoltes/temporal-katz-centrality-data-sets) that we collected:

```
@Article{Beres2018,
author="B{\'e}res, Ferenc
and P{\'a}lovics, R{\'o}bert
and Ol{\'a}h, Anna
and Bencz{\'u}r, Andr{\'a}s A.",
title="Temporal walk based centrality metric for graph streams",
journal="Applied Network Science",
year="2018",
volume="3",
number="1",
pages="32",
issn="2364-8228",
}
```

A former version of our research was presented at the 6th International Conference on Complex Networks and Their Applications. You can find the related codebase on a different [branch](https://github.com/ferencberes/online-centrality/tree/complex_networks_2017).


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

**The US Open 2017 (UO17) and Roland-Garros 2017 (RG17) Twitter datasets are available on the [website](https://dms.sztaki.hu/hu/letoltes/temporal-katz-centrality-data-sets) of our research group.

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

**NOTE: In most of the notebooks you have to select from the tennis dataset "rg17" or "uo17".**

## 1. Calculate centrality scores

You can calculate centrality scores for hourly snapshots with the following script.

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/calculate_centrality_scores.sh
```

**It could take several hours** to calculate the scores for all parametrizations that is required for the following steps. That is the reason why we use **--ExecutePreprocessor.timeout=7200** configuration for  the **jupyter nbconvert** command. If the execution don't finish in 2 hours on your computer then you should increase this time limit.

**Related notebooks (execute them in this order):**

   * [Centraity score computer](ipython/experiments/CentralityScoreComputer.ipynb): export score files into folder **./data/DATASET_ID/centrality_scores/**.

#### Notations of centrality scores

   * *tk*: temporal Katz centrality
   * *ttk*: truncated temporal Katz centrality
   * *tpr*: temporal PageRank
   * *spr*: static PageRank
   * *hc*: static Harmonic Centrality
   * *nbm*: static negative-Beta Measure
   * *indeg*: static indegree
   * *did*: decayed indegree

## 2. Experiments

You can run the experiments with the following script:

```bash
source activate YOUR_CONDA_PY3_ENV
bash ./scripts/run_experiments.sh
```

**Related notebooks (execute them in this order):**

   * [Schedule Score Updater](ipython/experiments/ScheduleScoreUpdater.ipynb): Extract relevant nodes related to daily tennis player accounts. Prepare labels for the supervised evaluation.

# Troubleshooting

If you get a **"TimeoutError: Cell execution timed out"** when you run any of the provided bash scripts then you should increase the execution time limit for the **jupyter nbconvert** command for the notebook that had broken down. You can do this by using

```bash
jupyter nbconvert --to notebook --execute  --ExecutePreprocessor.timeout=HIGHER_TIME_LIMIT BROKEN_DOWN_NOTEBOOK.ipynb
```
 
 or just execute the given notebook through the Jupyter browser.
