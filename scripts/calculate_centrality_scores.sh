#!/bin/bash
echo "### Calculating centrality scores ###"
pushd ./ipython/experiments
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=36000 CentralityScoreComputer.ipynb
popd