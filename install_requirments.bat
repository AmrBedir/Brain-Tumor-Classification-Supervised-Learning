#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install Python3 and pip if not already installed
echo "Installing Python3 and pip..."
sudo apt-get install -y python3 python3-pip

# Install required Python libraries
echo "Installing Python libraries..."
pip3 install numpy opencv-python scikit-learn seaborn matplotlib

echo "All required libraries have been installed successfully!"
