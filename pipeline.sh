sudo yum -y update

# install unzip
sudo yum -y install unzip

# install python36
sudo yum install -y python36

# remove openjdk java
sudo yum -y remove java*

# install oracle java
wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u141-b15/336fa29ff2bb4ef291e347e091f7f4a7/jdk-8u141-linux-x64.rpm
sudo yum install -y jdk-8u141-linux-x64.rpm

# set java home
export JAVA_HOME=/usr/java/default

# print java version
java -version

# install maven
wget -O /home/ec2-user/apache-maven-3.5.2-bin.tar.gz http://www-eu.apache.org/dist/maven/maven-3/3.5.2/binaries/apache-maven-3.5.2-bin.tar.gz
tar xzvf apache-maven-3.5.2-bin.tar.gz
export PATH=$PATH:/home/ec2-user/apache-maven-3.5.2/bin

# install git
sudo yum -y install git
rm -Rf cdc-datapipeline
rm -f *.gz
rm -f *.zip
rm -Rf stanford-corenlp-*
rm -Rf cdc-datapipeline

# download cdc-pipeline from s3 bucket
git clone https://github.com/riteshapatel/cdc-datapipeline.git /home/ec2-user/cdc-datapipeline

# download corenlp
wget -O /home/ec2-user/stanford-corenlp-full-2017-06-09.zip https://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip

# unzip and set up corenlp for cdc datapipeline
unzip stanford-corenlp*
cp stanford-corenlp-full-2017-06-09/*.* /home/ec2-user/cdc-datapipeline/parser/corenlp/

# download semafor
git clone https://github.com/Noahs-ARK/semafor.git /home/ec2-user/cdc-datapipeline/parser/semafor

cd /home/ec2-user/cdc-datapipeline/parser/semafor
mvn package

cd ~

# replace script in semafor directory
aws s3 cp s3://mosaic.cdc.parser/config.sh /home/ec2-user/cdc-datapipeline/parser/semafor/bin/config.sh
aws s3 cp s3://mosaic.cdc.parser/convertConll.sh /home/ec2-user/cdc-datapipeline/parser/semafor/bin/convertConll.sh
aws s3 cp s3://mosaic.cdc.parser/smaller.jl /home/ec2-user/cdc-datapipeline/smaller.jl

# download malt models
wget -O /home/ec2-user/semafor_malt_model_20121129.tar.gz http://www.ark.cs.cmu.edu/SEMAFOR/semafor_malt_model_20121129.tar.gz

# unzip corenlp
unzip stanford-*

# tar models and move it under models directory
tar -xvzf semafor_malt_*
mv semafor_malt_model_20121129 /home/ec2-user/cdc-datapipeline/parser/models/

# change project directory
cd cdc-datapipeline

# install dependencies
sudo python3 -m pip install -r requirements.txt

# run script
sudo python3 main.py