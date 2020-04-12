#!/usr/bin/env Rscript

rmarkdown::render("covid_model_report.Rmd", output_format="pdf_document")
rmarkdown::render("covid_model_report.Rmd", output_format="beamer_presentation", output_file="covid_model_presentation")
