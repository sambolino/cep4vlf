# cep4vlf
Cep4vlf is a project for detection of SIDs (sudden ionospheric disturbances). It uses VLF data, associated with GOES satellite data. This is a pre-alpha version, which stages prepared historical data, whereas production-stage software will work with (near) real-time data.

## Technical description
This is a javaSE Maven project which uses [Esper](http://esper.espertech.com/release-8.8.0/reference-esper/html_single/index.html) complex event processing framework. Data preparation script from .mat files to .csv is written in python3, under /python directory. Prepared files should be copied to src/resources. Output is logged into log4j-application.log file.

## Theoretical info
Strong radiation from solar X-ray flares can produce increased ionization in the terrestrial D-region and change its structure. Moreover, extreme solar radiation in X-spectral range can create sudden ionospheric disturbances and can consequently affect devices on the terrain as well as signals from satellites and presumably cause numerous uncontrollable catastrophic events. Aim of this project is to enable automatic, real time detection of SID events, like flares, GRB's, lightning, etc. which can affect chemistry and physics of ionosphere. Moreover, it will enable real time modeling incorporating methods already introduced in [flarED](https://github.com/sambolino/flarED).
