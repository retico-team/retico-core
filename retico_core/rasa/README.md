# retico-core-rasa
  

This project includes the core functionality of the retico rasa module

## How to install
This will also install the retico-core-core modules that are required for all of retico to function


via pip:

  

```bash

$ pip  install  retico-core-rasa

```

## Usage
For this module you must have a rasa pretrained model saved in the system then pass it to the NLU

```
from retico_core.modules.rasa.retico_nlu import RasaNLUModule
nlu = RasaNLUModule(model_dir=<PATH TO MODEL DIRECTORY>, incremental=False)
```

## Import
```
import retico_nlu
```

## Retico
Documentation for the main retico project can be found here
[![Documentation Status](https://readthedocs.org/projects/retico-core/badge/?version=latest)](https://retico-core.readthedocs.io/en/latest/?badge=latest)