CRAN <- "https://cran.r-project.org"

install.packages("tidyverse", repos = CRAN, dependencies = TRUE)
install.packages("nnls", repos = CRAN, dependencies = TRUE)
install.packages("splines2", repos = CRAN, dependencies = TRUE) 
install.packages("optparse", repos = CRAN, dependencies = TRUE)

install.packages('devtools', repos = CRAN, dependencies = TRUE)

devtools::install_github(repo='HopkinsIDD/covidImportation', ref="v1.5")
devtools::install_github(repo='HopkinsIDD/COVIDScenarioPipeline', subdir='R/pkgs/covidcommon', ref="3f042f8b2eec504c1d2e3dde95d33daf444bf281")
devtools::install_github(repo='HopkinsIDD/COVIDScenarioPipeline', subdir='R/pkgs/hospitalization', ref="3f042f8b2eec504c1d2e3dde95d33daf444bf281")
devtools::install_github(repo='HopkinsIDD/COVIDScenarioPipeline', subdir='R/pkgs/report_generation', ref="3f042f8b2eec504c1d2e3dde95d33daf444bf281")
install.packages("reticulate", repos = CRAN, dependencies = TRUE)
install.packages("kableExtra", repos = CRAN, dependecies = TRUE)
install.packages("xml2", repos = CRAN, dependencies = TRUE)

devtools::install_github('HopkinsIDD/globaltoolboxlite')
