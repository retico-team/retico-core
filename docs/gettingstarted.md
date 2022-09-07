# Getting started

This section describes how to install retico_core and its dependencies on your machine
and outlines how to implement a "hello world" incremental network to test that
everything is working.

## Installation

Retico_core provides the main functionality of incremental modules and units. This
includes basic audio processing, which is defined in the {ref}`Audio Module`. To provide
this functionality, retico_core relies on [PortAudio](http://www.portaudio.com) as a
dependency.

### PortAudio

PortAudio is a cross-plattform audio I/O library. This section describes how to install
it on your machine. Because the installation process depends on which operating system
you use, this section is split up into different parts.

#### MacOS

On MacOS you will need a package manager to install PortAudio. This might either be
[Homebrew](https://brew.sh) or [MacPorts](https://macports.org).

With **Homebrew** you can install PortAudio with the following command:

```bash
brew install portaudio
```

With **MacPorts** you have to use the following command:

```bash
sudo port install portaudio
```

#### Linux

The package managers on most linux distributions will have portaudio in their
repositories.

For apt-based distributions, use the following command:

```bash
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
```

For other distributions, you most likely have to search for ways to install portaudio or
build it yourself.

#### Windows

Under Windows, PortAudio is automatically installed as a dependency. You do not need
to install anything in this step.

### Installing retico-core

To install the current version of retico-core, you can use `pip`:

```bash
pip install retico-core
```

This will install the [PyAudio](https://pypi.org/project/PyAudio/) dependency, that
allows retico-core to access the PortAudio interface. If the installation of this
dependency fails, please check your {ref}`PortAudio` installation.

### See if everything works

To see if everything worked smoothly, create a python script with the following code:

```python
import retico_core
print(retico_core.__version__)
```

You should now be able to see the current version number of retico_core.

## Creating an incremental network

To test the functionality of retico_core, you can build a small incremental network
consisting of two modules sending incremental units between each other. In this example,
we use classes of the {ref}`Audio Module` to record audio via the microphone and output
the same audio to the speakers. For this, you need to import `retico_core` and create
a {class}`MicrophoneModule<retico_core.audio.MicrophoneModule>` as well as a
{class}`SpeakerModule<retico_core.audio.SpeakerModule>`:

```python
from retico_core.audio import MicrophoneModule, SpeakerModule

microphone_module = MicrophoneModule()
speaker_module = SpeakerModule()
```

Both the MicrophoneModule and the SpeakerModule take `chunk_size` as an argument. This
argument specifies how many *samples* of audio are packaged into each incremental unit.
Per default, the modules work with $44100\,Hz$, (which means 44100 samples per second).
So in our case, each IU contains $100\,ms$ (or 0.1 seconds) of audio.

Now let's connect the two modules:

```python
microphone_module.subscribe(speaker_module)
```

The *output* of the MicrophoneModule will be sent to the SpeakerModule in the form
of incremental units, each with $100\,ms$ of audio.

After that, we can run the network. **Warning: If you do not connect a headset, this network
can cause a feedback loop, as you output exactly what the microphone records!**

```python
microphone_module.run()
speaker_module.run()

input()

microphone_module.stop()
speaker_module.stop()
```
