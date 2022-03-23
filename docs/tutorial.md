# Tutorial

This tutorial is a step-by-step instruction on how to implement a module that turns audio IUs into [MFCCs](https://en.wikipedia.org/wiki/Mel-frequency_cepstrum).

For this, the following units of the retico framework are used:
 - incremental units
 - incremental modules
 - the event system
 - connection of a network

## Creating an incremental unit

In order for the incremental module to output the MFCC information, there needs to be an IU class the holds this information. For this, we define a new class that inherits its functionality from the {class}`IncrementalUnit<retico_core.abstract.IncrementalUnit>`:

```python





```

