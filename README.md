# COVID19 Setup

Setup a COVID19 simulation for the JHU pipeline.

## Requirements

We assume you have Python 3.6 or greater and docker.

Next, you'll need to make some changes to the `config.yml.template`. First
create a copy named `config.yml`.

```bash
cp config.yml.template config.yml
```

Then you'll need at least to edit where you see things between `<< >>`.

After you have this setup, then you can run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create the makefile
python3 render.py makefile -c config.yml -o Makefile

# Create the report template
python3 render.py report -c config.yml -o state_report.Rmd

# Get the necessary shapefiles
python3 render.py shapefile -c config.yml --use-cache

# Get the model's seed
python3 render.py mobility -c config.yml --use-cache

# Build the docker file
cd docker
docker build -t covid .
cd ..

# Make the output directory
mkdir output

# Run the model
docker run --rm \
  -v "$(pwd)/config.yml:/home/app/covidsp/config.yml" \
  -v "$(pwd)/output:/home/app/covidsp/final_model_output" \
  -v "$(pwd)/data:/home/app/covidsp/data" \
  -v "$(pwd)/Makefile:/home/app/covidsp/Makefile" \
  -v "$(pwd)/state_report.Rmd:/home/app/covidsp/report/state_report.Rmd" \
  -v "$(pwd)/compile_Rmd.R:/home/app/covidsp/compile_Rmd.R" \
  covid
```

In future runs, you can just execute the last line after switching up the `config.yml`.
