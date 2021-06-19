#!/bin/bash

echo "### Download dataset ###"
bash ./scripts/download_data.sh

echo "### Calculate centrality scores ###"
echo "This step could take a lot of time!"
python ./experiments/CentralityScoreComputer.py rg17 43200 1
#3600

echo "### Run experiments ###"
#bash ./scripts/run_experiments.sh

echo "### DONE ###"