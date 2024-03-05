# retico-core-asr
  

This project includes the core functionality of the retico asr module

## How to install
This will also install the retico-core-core modules that are required for all of retico to function


via pip:

  

```bash

$ pip  install  retico-core-asr

```

## Import
```
import asr
import asr_cat
import asr_deepspeech
```

## Retico
Documentation for the main retico project can be found here
[![Documentation Status](https://readthedocs.org/projects/retico-core/badge/?version=latest)](https://retico-core.readthedocs.io/en/latest/?badge=latest)

## Sample Program
```
from retico_core.core.audio import MicrophoneModule
from retico_core.core.debug import DebugModule
from asr import OfflineASRModule


debug = DebugModule()

microphone = MicrophoneModule(rate=16000)
localAsr = OfflineASRModule()

'''
subscribe to modules in a cascading pattern
Microphone is needed by localAsr so subscribe to localAsr
debug will relay the information form localAsr so subscribe localAsr to debug
'''

microphone.subscribe(localAsr)
localAsr.subscribe(debug)


# run modules
microphone.run()
localAsr.run()
debug.run()


input()

# stop modules
microphone.stop()
localAsr.stop()
debug.stop()
```