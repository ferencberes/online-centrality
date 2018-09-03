#!/bin/bash
pushd ./experiments
echo "### Running preprocessor ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 ScheduleScoreUpdater.ipynb
echo "### Running tennis player predictions ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=7200 PredictTennisPlayer.ipynb
echo "### Running concept drift experiment ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=3600 ConceptDrift.ipynb
popd
