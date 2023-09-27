#!/bin/bash

# Check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "conda could not be found"
    exit
fi

# Prompt user to confirm if the desired conda environment is activated
read -p "Is your desired conda environment activated? (Y/N): " answer
case ${answer:0:1} in
    y|Y )
        echo "Proceeding with package installation..."
    ;;
    * )
        echo "Please create and/or activate the desired conda environment, and then rerun."
        exit
    ;;
esac

# Install specific packages with conda
conda install -y pyyaml==5.4.1 scipy osqp

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found"
    exit
fi

# Install remaining packages from requirements.txt with pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt --ignore-installed
else
    echo "requirements.txt not found in the current directory"
    exit 1
fi

if [ -f setup.py ]; then
    python setup.py install
else
    echo "setup.py not found in the current directory"
    exit 1
fi

echo "All packages installed successfully"
