#!/bin/bash
echo "### Running parameter notebook 'RGParams.ipynb' ###"
pushd ./ipython/parameters
jupyter nbconvert --to notebook --execute RGParams.ipynb
popd
pushd ./ipython/experiments
echo "### Calculating non-constant ratios ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 roland_garros_olr_const_ratios.ipynb
echo "### Running player predict experiment ###"
jupyter nbconvert --to notebook --execute  --ExecutePreprocessor.timeout=1800 roland_garros_predict_player.ipynb
popd