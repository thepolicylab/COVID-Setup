FROM hopkinsidd/covidscenariopipeline:latest

ADD rsetup.R /tmp/rsetup.R
RUN Rscript /tmp/rsetup.R

ARG oauth_token
ENV OAUTH_TOKEN=$oauth_token

ADD pipelinesetup.sh /tmp/pipelinesetup.sh
RUN bash /tmp/pipelinesetup.sh

ADD run.sh /home/app/covidsp/run.sh
WORKDIR /home/app/covidsp
CMD ["bash", "./run.sh"]
