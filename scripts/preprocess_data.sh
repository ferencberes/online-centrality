#!/bin/bash
pushd ./ipython/preprocessing
jupyter nbconvert --to notebook --execute ScheduleScoreUpdater.ipynb
popd