#!/bin/bash

echo "### Download dataset ###"
bash ./scripts/download_data.sh

echo "### Calculate centrality scores ###"
echo "This step could take a lot of time!"
bash ./scripts/calculate_centrality_scores.sh

echo "### Run experiments ###"
bash ./scripts/run_experiments.sh

echo "### DONE ###"