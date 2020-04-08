#!/bin/bash
set -x
set -o 

source ~/python_venv/bin/activate
mkdir -p .files

cd COVIDScenarioPipeline/data
python build-model-input.py
cd ../..
make clean
make

mkdir -p final_model_output
thedate=`date "+%Y-%m-%dT%H-%M-%S"`
filename="output-$thedate.tar.gz"
tar czvf "$filename" config.yml model_output hospitalization
cp "$filename" final_model_output
