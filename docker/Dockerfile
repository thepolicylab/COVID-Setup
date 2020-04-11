FROM hopkinsidd/covidscenariopipeline:latest

USER app

COPY --chown=app build /tmp/build

# r
RUN Rscript /tmp/build/rsetup.R

# github repos
RUN bash /tmp/build/pipelinesetup.sh

# python
RUN sudo apt-get update && sudo apt-get -y install python python3-pip texlive-latex-base texlive-latex-extra
RUN /usr/bin/python3 -m pip install -r /tmp/build/requirements.txt

# files needed in run
COPY --chown=app run /home/app/covidsp

RUN mkdir -p /home/app/covidsp/report

WORKDIR /home/app/covidsp
CMD ["bash", "run.sh"]
