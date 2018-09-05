#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y expect
sleep 10
sudo apt install -y xfce4 xfce4-goodies tightvncserver
sudo apt-get install -y apt-transport-https ca-certificates
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:x2go/stable -y
sudo apt-get update
sudo apt-get install -y x2goserver x2goserver-xsession
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo add-apt-repository ppa:webupd8team/java -y
sudo apt-get update
sudo apt-get install -y oracle-java8-installer
sudo mkdir /home/ubuntu/Desktop
sudo mkdir /home/ubuntu/Downloads
cd /home/ubuntu/Downloads
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i --force-depends google-chrome-stable_current_amd64.deb
sudo apt-get -f --force-yes --yes install
sudo wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo chmod 777 Miniconda3-latest-Linux-x86_64.sh
sudo bash Miniconda3-latest-Linux-x86_64.sh -b
echo 'export PATH=/home/ubuntu/miniconda3/bin:$PATH' >> ~/.bashrc