#!/bin/sh

# yum updates
yum -y update 

# install unzip
yum -y install unzip 

# install python36
sudo yum install python36

# install git 
sudo yum -y install git 

rm -Rf cdc-datapipeline 

# download cdc-pipeline from s3 bucket
aws s3 cp s3://mosaic.cdc.parser/cdc-datapipeline.zip cdc-datapipeline.zip

# unzip pipeline
unzip cdc-data*

# download corenlp
wget https://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip

# unzip and set up corenlp for cdc datapipeline
unzip stanford-corenlp* 
mkdir cdc-datapipeline/parser/corenlp
cp stanford-corenlp-full-2017-06-09/*.* cdc-datapipeline/parser/corenlp/

# download semafor
git clone https://github.com/Noahs-ARK/semafor.git cdc-datapipeline/parser/semafor

# replace script in semafor directory
aws s3 cp s3://mosaic.cdc.parser/config.sh cdc-dataparser/parser/semafor/bin
aws s3 cp s3://mosaic.cdc.parser/convertConll.sh cdc-dataparser/parser/semafor/bin

# download malt models
curl http://www.ark.cs.cmu.edu/SEMAFOR/semafor_malt_model_20121129.tar.gz


# unzip corenlp
unzip stanford-*

# untar models


# extract pipe line
unzip cdc-*

# change project directory 
cd cdc-datapipeline

# install dependencies 
python3 -m pip install -r requirements.txt 

# run script
python3 main.py




