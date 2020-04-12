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

Rscript --vanilla create_reports.R

mkdir -p final_model_output
thedate=`date "+%Y-%m-%dT%H-%M-%S"`
filename="output-$thedate.tar.gz"
tar czvf "$filename" config.yml model_output hospitalization covid_model_report.pdf covid_model_report.tex covid_model_report_files covid_model_presentation.pdf covid_model_presentation.tex covid_model_presentation_files


cp "$filename" final_model_output
