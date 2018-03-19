#!/bin/bash
mkdir -p ./data
cd data
wget https://dms.sztaki.hu/sites/dms.sztaki.hu/files/download/2018/usopen_raw_data.zip
echo "USOpen data set was downloaded."
unzip usopen_raw_data.zip
echo "Compressed USOpen data set was unzipped."
wget https://dms.sztaki.hu/sites/dms.sztaki.hu/files/download/2018/polina_graphs.zip
echo "Small data sets were downloaded."
unzip polina_graphs.zip
echo "Compressed small data sets were unzipped."