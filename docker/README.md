# Docker for COVID Pipeline

This docker file will run a RI based pipeline of the JHU model.

```
docker build -t covid .
```

Then to run do

```
mkdir output
docker run --rm -v "$(pwd)/config.yml:/home/app/covidsp/config.yml" -v "$(pwd)/output:/home/app/covidsp/final_model_output" covid:latest
```
