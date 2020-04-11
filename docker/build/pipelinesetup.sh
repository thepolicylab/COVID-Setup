#!/bin/bash
mkdir -p ~/covidsp
cd ~/covidsp
git clone https://github.com/thepolicylab/COVIDScenarioPipeline
sudo apt-get install -y git-lfs
git lfs install
cd COVIDScenarioPipeline/data/united-states-commutes
git lfs fetch
git lfs checkout commute_data.csv
git lfs checkout census_tracts_2010.csv

