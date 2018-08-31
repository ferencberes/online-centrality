#!/bin/bash
pushd ./experiments
echo "### Running preprocessor ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 ScheduleScoreUpdater.ipynb
echo "### Running tennis player predictions ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=7200 PredictTennisPlayer.ipynb
popd
