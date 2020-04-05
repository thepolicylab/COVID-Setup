#!/bin/bash

source ~/python_venv/bin/activate
mkdir -p .files
make clean
make

mkdir -p final_model_output
cp -r model_output final_model_output/model_output
cp -r report final_model_output/report
