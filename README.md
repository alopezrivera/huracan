# Huracan

Huracan is an open source, 0-dimensional, object-oriented airbreathing engine 
modelling package for preliminary analysis and design of airbreathing engines, 
divulgation and educational purposes.

At the moment Huracan is capable of modelling engines with an arbitrary number of 
components connected by an arbitrary number of shafts. It allows for a single 
combustion chamber per stream and reheating. Multiple-stream systems can be modelled, 
as well as splitting (such as the bypass flow of a turbofan) and mixing streams (such 
as in the nozzle of a mixed exhaust turbofan).

The inspiration for the project lies in traditional thermodynamic plant diagrams, 
and similar architectures are used in well known proprietary tools such as 
[GasTurb](https://www.gasturb.de/) and [NLR's GSP](https://www.gspteam.com/index.html).

[The API reference is available here.](https://huracan-docs.github.io/)

`Antonio Lopez Rivera, 2021`

## Install

    pip install huracan

## Examples

| **[Single spool turboprop engine.](https://github.com/alopezrivera/huracan/blob/master/examples/turboprop/turboprop_1s-1s.py)** | **[Twin-spool, reheated turbojet engine with an electrical power plant.](https://github.com/alopezrivera/huracan/blob/master/examples/turbojet/turbojet_1s-2s.py)** | **[Three-spool, separated exhaust turbofan engine.](https://github.com/alopezrivera/huracan/blob/master/examples/turbofan/turbofan_2s-3s.py)** |
| --- | --- | --- |
| <p align="top"><img width=300 src="docs/figures/log_turboprop.png" /></p> | <p align="top"><img width=300 src="docs/figures/log_turbojet.png" /></p> | <p align="top"><img width=300 src="docs/figures/log_turbofan.png" /></p> |
| ![alt text](docs/figures/Tp_turboprop.png "T-p plot") | ![alt text](docs/figures/Tp_turbojet.png "T-p plot") | ![alt text](docs/figures/Tp_turbofan.png "T-p plot") |
| ![alt text](docs/figures/pV_turboprop.png "p-V plot") | ![alt text](docs/figures/pV_turbojet.png "p-V plot") | ![alt text](docs/figures/pV_turbofan.png "p-V plot") |

---
[Back to top](#huracan)
