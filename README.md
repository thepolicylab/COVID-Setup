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

# Get the necessary shapefiles
mkdir data
python3 render.py shapefile -c config.yml --use-cache

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
  covid
```

After everything is finished, you should find a file whose name looks like `output.*.tar.gz` in
your output folder. This contains all the simulated output from the above command.

The easiest thing to do with this is to open up `hospitalization_plots.ipynb` in a jupyter
(Python) notebook and hit `Restart and Run All`, which will generate several plots.

In future runs, you can just execute the last line after switching up the `config.yml`.

### TODO

Figure out why our input rebuild script doesn't produce the same output as their input rebuild script.
