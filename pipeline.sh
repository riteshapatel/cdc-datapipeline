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
rm -f *.gz
rm -f *.zip
rm -Rf stanford-corenlp-*
rm -Rf cdc-datapipeline

# download cdc-pipeline from s3 bucket
git clone https://github.com/riteshapatel/cdc-datapipeline.git cdc-datapipeline

# download corenlp
wget https://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip

# unzip and set up corenlp for cdc datapipeline
unzip stanford-corenlp* 
cp stanford-corenlp-full-2017-06-09/*.* cdc-datapipeline/parser/corenlp/

# download semafor
git clone https://github.com/Noahs-ARK/semafor.git cdc-datapipeline/parser/semafor

# replace script in semafor directory
aws s3 cp s3://mosaic.cdc.parser/config.sh cdc-datapipeline/parser/semafor/bin/config.sh
aws s3 cp s3://mosaic.cdc.parser/convertConll.sh cdc-datapipeline/parser/semafor/bin/convertConll.sh

# download malt models
wget http://www.ark.cs.cmu.edu/SEMAFOR/semafor_malt_model_20121129.tar.gz

# unzip corenlp
unzip stanford-*

# tar models and move it under models directory
tar -xvzf semafor_malt_*
mv semafor_malt_model_20121129 cdc-datapipeline/parser/models/

# change project directory 
cd cdc-datapipeline

# install dependencies 
python3 -m pip install -r requirements.txt 

# run script
python3 main.py




