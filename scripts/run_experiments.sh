#!/bin/bash
echo "### Running parameter notebook 'USOParams.ipynb' ###"
pushd ./ipython/parameters
jupyter nbconvert --to notebook --execute USOParams.ipynb
popd
pushd ./ipython/experiments
echo "### Running preprocessor ###"
jupyter nbconvert --to notebook --execute  --ExecutePreprocessor.timeout=1800 ScheduleScoreUpdaterUSO.ipynb
echo "### Running player predict experiment ###"
jupyter nbconvert --to notebook --execute  --ExecutePreprocessor.timeout=1800 uso_predict_player.ipynb
echo "### Concept Drift experiments ###"
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 ConceptDrift.ipynb
popd