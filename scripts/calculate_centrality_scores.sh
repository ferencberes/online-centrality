#!/bin/bash
echo "### Calculating centrality scores ###"
pushd ./ipython/experiments
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=7200 CentralityScoreComputer.ipynb
popd