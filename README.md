online-centrality
=================

This repository contains the code used in the Online Centrality research of Ferenc Béres, [Róbert Pálovics](https://github.com/rpalovics) and András A. Benczúr at the [Institute for Computer Science and Control of the
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
      * **data processing:** pandas, numpy, bs4
      * **scientific:** scipy, networkx 
      * **visualization:** matplotlib, seaborn
      * **general:** sys, os, math, re, json, shutil, operator, collections, multiprocessing, functools, itertools, datetime

# Data

In this repository you can find the codebase that we are using during our research. **The USOpen 2017 dataset is available on the website of our [research group](https://dms.sztaki.hu/hu/letoltes/online-centrality-data-sets)** at the Institute for Computer Science and Control of the
Hungarian Academy of Sciences.

# Cite

### Complex Networks 2017

A former version of our research was presented at the 6th International Conference on Complex Networks and Their Applications. You can see our work in the [Book of Abstracts](http://complexnetworks.org/BookOfAbstracts.pdf#page=198) or on the [poster](https://github.com/ferencberes/online-centrality/blob/master/documents/complex_networks_2017_poster.pdf) that I presented.

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


