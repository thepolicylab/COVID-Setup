FROM hopkinsidd/covidscenariopipeline:latest

USER app

COPY --chown=app rsetup.R /tmp/rsetup.R
RUN Rscript /tmp/rsetup.R

COPY --chown=app pipelinesetup.sh /tmp/pipelinesetup.sh
RUN bash /tmp/pipelinesetup.sh

COPY --chown=app run.sh /home/app/covidsp/run.sh

RUN mkdir -p /home/app/covidsp/report

WORKDIR /home/app/covidsp
CMD ["bash", "./run.sh"]
