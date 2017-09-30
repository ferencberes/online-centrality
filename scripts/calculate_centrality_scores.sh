#!/bin/bash
echo "### Running parameter notebook 'centrality_params.ipynb' ###"
pushd ./ipython/parameters
jupyter nbconvert --to notebook --execute  centrality_params.ipynb
popd
echo "### Calculating centrality scores ###"
pushd ./ipython/experiments
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=5400 centrality_score_computer.ipynb
popd