#!/bin/bash
echo "### Calculating centrality scores ###"
pushd ./experiments
python CentralityScoreComputer.py
popd