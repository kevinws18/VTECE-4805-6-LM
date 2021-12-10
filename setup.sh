#SETUP SCRIPT FOR LM_UAV COURIER TRANSMISSION SYSTEM
# AUTHOR: STEPHAN MULLER

echo "STARTING SETUP"
sleep 1

sudo apt update

# Install pip used for python package installation
sudo apt install -y python3-pip

# Install numpy and matplotlib for computations
python3 -m pip install numpy
python3 -m pip install matplotlib

# Install soapysdr for interacting via USB with LimeSDR
sudo apt install -y python3-soapysdr

# Install git used to fetch fec requirements
sudo apt install -y git

# Set up FEC requirents
git clone https://github.com/epeters13/pyreedsolomon.git
cd ./pyreedsolomon
python3 setup.py build
python3 setup.py install
cp ./build/lib.linux-x86_64*/*.so .
cd ..

echo "SETUP SUCCESSFUL"
