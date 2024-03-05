import os
import numpy as np
import threading
from os import path
from retico_core.core import abstract
from retico_core.core.text import SpeechRecognitionIU
from retico_core.core.audio import AudioIU

# word filtering
from nltk.corpus import wordnet as wn
from nltk.corpus import words

# Managing audio file
import wave
import pyaudio
import librosa
import time

# Import deepspeech
import deepspeech

# handling errors
import traceback

# logger
from colorama import Fore
from colorama import Style

# regular expression for filtering
import re

class DeepSpeechLocalASRModule(abstract.AbstractModule):
    """A Module that recognizes speech locally by utilizing the 0.9.3 release of Deep Speech, an open speech-to-text engine."""

    def __init__(self, test_mode=False, **kwargs):
        """Initialize the ASR module with the given arguments.
            roughly about 16 input_ius equals to 1 seconds

        Args:
        """
        self.test_mode = test_mode
        self.sample_width = 2
        self.pyaudio_instance = pyaudio.PyAudio()
        self.format = self.pyaudio_instance.get_format_from_width(self.sample_width)
        self.channels = 1
        self.rate = 16000
        self.wave_output_filename = os.getcwdb().decode("utf-8") + "\\output.wav"
        if path.exists(self.wave_output_filename):
            os.remove(self.wave_output_filename)
        if self.test_mode:
            self.frames = None
        else:
            self.frames = []

        self.model = deepspeech.Model("/Users/ryanpacheco/git/retico-core/retico_core/modules/huggingface/deepspeech-0.9.3-models.pbmm")
        self.model.enableExternalScorer("/Users/ryanpacheco/git/retico-core/retico_core/modules/huggingface/deepspeech-0.9.3-models.scorer")


        self.silence_start_time = time.time()
        self.last_pred = ""

        # the boolean for the prediction function: whether it should predict or not
        self.predict_thread_on = True

        #optimization variables
        self.wordCountAtm = 0  # tell you how many word count we have in the partial text prediction

        # results
        self.previousResult = ""  ## hold the previous prediction at every iteration
        self.previousResultTime = time.time()  ## hold the previous prediction time at every iteration
        self.result = ""  ## the predicted result so far
        self.finalResult = "" ## the very final result when commit happens
        
        # latency testing variables
        self.sentence_prediction_total_time = 0  ## holds the total prediction latency time at certain iteration
        self.sentence_prediction_total_time_final = 0 ## holds the total prediction final latency time
        self.latestFile = ""

        # revoke count testing
        self.revoke_count = 0

        super().__init__(**kwargs)


    @staticmethod
    def name():
        return "DeepSpeech ASR Module"

    @staticmethod
    def description():
        return "A Module that recognizes speech offline using DeepSpeech."

    @staticmethod
    def input_ius():
        return [AudioIU]

    @staticmethod
    def output_iu():
        return SpeechRecognitionIU
    
    def process_update(self, update_message):
        for iu,um in update_message:
            if um == abstract.UpdateType.ADD:
                self.process_iu(iu)
            elif um == abstract.UpdateType.REVOKE:
                self.process_revoke(iu)

    def process_iu(self, input_iu):

        if self.test_mode:
            if self.frames is None:
                self.frames = input_iu.wavAudio
            else:
                self.frames = np.concatenate((self.frames, input_iu.wavAudio), axis = 0)
            self.latestFile = input_iu.currentFileName
        else:
            self.frames.append(input_iu.raw_audio)

        if len(self.frames) > 500000:
            lengthToRemove = int(len(self.frames) * 0.30)  # upto 80% size is two words, roughly
            self.frames = self.frames[lengthToRemove:]
        return None

    def setup(self):
      t = threading.Thread(target=self.predict_speech)
      t.start()
      pass

    def shutdown(self):
        self.predict_thread_on = False
        pass

    def predict_speech(self):
        stream_context = self.model.createStream()
        while self.predict_thread_on:
            if self.test_mode:
                currentFrames = self.frames
            else:
                currentFrames = self.frames
                # if path.exists(self.wave_output_filename):
                #     os.remove(self.wave_output_filename)
                # wf = wave.open(self.wave_output_filename, 'wb')
                # wf.setnchannels(self.channels)
                # wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.format))
                # wf.setframerate(self.rate)
                # wf.writeframes(b''.join(currentFrames))
                # wf.close()
                # audio, rate = librosa.load(self.wave_output_filename, sr=16000)

                # raw = b''.join(currentFrames)
                # raw = np.frombuffer(raw, dtype='int32')
                # audio = raw / 2147483648

            someTime = time.time()
            if currentFrames is None:
                print("AUDIO IS NONE")
                continue

            if len(currentFrames) == 0:
                    print("AUDIO IS NONE")
                    continue

            for frame in currentFrames:
                if frame is not None:
                  stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
                  inter = stream_context.intermediateDecode()
                  print(inter)

                else:
                    transcription = stream_context.finishStream()
                    print("Recognized: %s" % transcription)
                    stream_context = self.model.createStream()



