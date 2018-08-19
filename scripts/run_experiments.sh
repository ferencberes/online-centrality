#!/bin/bash
pushd ./ipython/experiments
echo "### Running preprocessor ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 ScheduleScoreUpdater.ipynb
popd
