#!/bin/bash
mkdir -p ./data
cd data
wget https://dms.sztaki.hu/sites/dms.sztaki.hu/files/download/2017/rg_raw_data.zip
echo "Dataset was downloaded."
unzip rg_raw_data.zip
echo "Compressed dataset file was unzipped."