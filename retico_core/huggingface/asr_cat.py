import os
import numpy as np
import threading
from os import path
from retico_core.core import abstract
from retico_core.core.text import SpeechRecognitionIU
from retico_core.core.audio import AudioIU


# # word filtering
# from nltk.corpus import wordnet as wn
# from nltk.corpus import words
# from nltk.stem import WordNetLemmatizer

#voice activity
# import webrtcvad
# import Levenshtein

# For managing audio file
import wave
import pyaudio
import librosa
import time

#Importin Pytorch
import torch

#Importing Wav2Vec
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer

# handling errors
import traceback

# logger
from colorama import Fore
from colorama import Style

# regular expression for filtering
import re

class OfflineASRModule(abstract.AbstractModule):
    """A Module that recognizes speech locally by utilizing the Wav2Vec2-Base-960h base model from huggingface."""

    def __init__(self, test_mode=False, save_results=True, results_file_name='localASR', **kwargs):
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
        self.save_results = save_results
        self.results_file_name = results_file_name
        self.first = True
        self.tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
        self.model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        self.silence_start_time = time.time()
        self.last_pred = ""

        # voice activity variables
        # self.frame_duration = 10  # 62
        # self.vad = webrtcvad.Vad(2)

        # the boolean for the prediction function: whether it should predict or not
        self.predict_thread_on = True

        #optimization variables
        self.wordCountAtm = 0  # tell you how many word count we have in the partial text prediction

        # result
        self.previousResult = ""  ## hold the previous prediction at every iteration
        self.previousResultTime = time.time()  ## hold the previous prediction time at every iteration
        self.result = ""  ## the predicted result so far
        self.finalResult = "" ## the very final result when commit happens

        # latency testing variables
        self.sentence_prediction_total_time = 0  ## holds the total prediction latency time at certain iteration
        self.sentence_prediction_total_time_final = 0 ## holds the total prediction final latency time
        self.latestFile = ""

        # TODAY
        self.lastTranscription = ""
        self.isFileSaved = False

        # revoke count testing
        self.revoke_count = 0

        super().__init__(**kwargs)

    @staticmethod
    def name():
        return "Offline ASR Module"

    @staticmethod
    def description():
        return "A Module that recognizes speech offline."

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
        # voice activity test
        # frame = b'\x00\x00' * int(self.rate * self.frame_duration / 1000)
        # frame = input_iu.raw_audio * int(self.rate * self.frame_duration / 1000)
        # print('Contains speech: %s' % (self.vad.is_speech(frame, self.rate)))
        # return None

        if self.test_mode:
            if self.frames is None:
                self.frames = input_iu.wavAudio
            else:
                self.frames = np.concatenate((self.frames, input_iu.wavAudio), axis=0)
            self.latestFile = input_iu.currentFileName
        else:
            self.frames.append(input_iu.raw_audio)  # Only append the new audio and let the PredictSpeech take care of it

        if len(self.frames) > 500000:
            # TODAY
            lengthToRemove = int(len(self.frames) * 0.30)  # upto 80% size is two words, roughly
            self.frames = self.frames[lengthToRemove:]
            # TODAY

        return None

    def setup(self):
        t = threading.Thread(target=self.PredictSpeech)
        t.start()
        pass

    def shutdown(self):
        self.predict_thread_on = False
        pass

    def findNewIUs(self, string1, string2):
        list1 = string1.split(" ")
        list2 = string2.split(" ")

        result = []
        # special case when list1 is bigger, meaning the prediction shrunk
        if len(list1) > len(list2):
            index = -1
            for i in range(0, len(list2)):  # because list2 is the smaller one
                if list1[i] != list2[i]:
                    index = i
                    break
            if index == -1:  # everything matched until the extra part
                for i in range(len(list2), len(list1)):
                    if list1[i] != "":
                        result.append("Revoke: " + list1[i])
            else:
                for i in range(index, len(list1)):
                    if list1[i] != "":
                        result.append("Revoke: " + list1[i])
                for i in range(index, len(list2)):
                    if list2[i] != "":
                        result.append("Add: " + list2[i])
            return result

        index = -1
        for i in range(0, len(list1)):
            if list1[i] != list2[i]:
                index = i
                break

        # first string is empty or fully match
        if index == -1:
            if string1 == "":
                for i in range(0, len(list2)):
                    if list2[i] != "":
                        result.append("Add: " + list2[i])
            else:
                for i in range(len(list1), len(list2)):
                    if list2[i] != "":
                        result.append("Add: " + list2[i])
        # all existing words revoked
        elif index == 0:
            for i in range(0, len(list1)):
                if list1[i] != "":
                    result.append("Revoke: " + list1[i])
            for i in range(0, len(list2)):
                if list2[i] != "":
                    result.append("Add: " + list2[i])
        else:
            for i in range(index, len(list1)):
                if list1[i] != "":
                    result.append("Revoke: " + list1[i])
            for i in range(index, len(list2)):
                if list2[i] != "":
                    result.append("Add: " + list2[i])

        return result


    def GetFileSaveStatus(self):
        return self.isFileSaved
    
    def PredictSpeech(self):  # inner function
        # when we reach word three length, we know where to trim off and how much of info is permanent
        while self.predict_thread_on is True:
            if self.first:
                time.sleep(0.7)
                print("START")
                self.first = False
            else:
                time.sleep(0.07)
            try:
                # latency testing varialbe
                process_start_time = time.time()

                audio = self.frames

                if audio is None:
                    print("AUDIO IS NONE")
                    continue

                if len(audio) == 0:
                    print("AUDIO IS NONE")
                    continue
                
                # get prediction
                input_values = self.tokenizer(audio, return_tensors="pt").input_values
                logits = self.model(input_values).logits
                prediction = torch.argmax(logits, dim=-1)
                transcription = self.tokenizer.batch_decode(prediction)[0]
                transcription = re.sub('[.,!/;-@#$%^&*?]', '', transcription)

                wordCount = len(transcription.split(" "))
                self.wordCountAtm = wordCount

                
                # get IUs (adds/revokes)
                generatedIUs = self.findNewIUs(self.result, transcription)
                for iu in generatedIUs:
                    if iu.startswith("Revoke"):
                        self.revoke_count = self.revoke_count + 1
                        print(Fore.RED + str(iu) + Style.RESET_ALL)
                    else:
                        print(Fore.CYAN + str(iu) + Style.RESET_ALL)

                # end time for latency test
                self.sentence_prediction_total_time = self.sentence_prediction_total_time + (time.time() - process_start_time)
                print('sentence_prediction_total_time', self.sentence_prediction_total_time)

                if(self.result != transcription):
                    self.silence_start_time = time.time()

                self.result = transcription

                currentTime = time.time()

                # silence limit 0.8 seconds taking acount the processing delay to make it a second, 
                # previousResultTime indicates that although there is no silence, no new info came up
                if currentTime - self.silence_start_time >= 0.8:
                    print('TIME')
                    self.silence_start_time = time.time()
                    self.finalResult = self.result
                    self.result = ""
                    self.previousResult = ""
                    transcription = ""
                    self.previousResultTime = time.time()
                    self.predict_thread_on = False
                    self.sentence_prediction_total_time_final = self.sentence_prediction_total_time
                    self.sentence_prediction_total_time = 0
                    

                if self.result == "" and self.finalResult != "":
                    print('FIN')
                    if self.test_mode:
                        if self.save_results:
                            print(Fore.RED + "saving data" + Style.RESET_ALL)
                            # latency
                            if not path.exists(self.results_file_name + "Latency.txt"):
                                file = open(self.results_file_name + "Latency.txt", "w+")
                                file.write(str(self.sentence_prediction_total_time_final/len(self.finalResult.split(" "))) + "\n")
                                file.close()
                            else:
                                with open(self.results_file_name + "Latency.txt", "a") as file:
                                    file.write(str(self.sentence_prediction_total_time_final/len(self.finalResult.split(" "))) + "\n")
                                    file.close()
                            # prediction
                            if not path.exists(self.results_file_name + "Prediction.txt"):
                                file = open(self.results_file_name + "Prediction.txt", "w+")
                                file.write(str(self.latestFile) + ", " + str(self.finalResult) + "\n")
                                file.close()
                                self.isFileSaved = True
                            else:
                                with open(self.results_file_name + "Prediction.txt", "a") as file:
                                    file.write(str(self.latestFile) + ", " + str(self.finalResult) + "\n")
                                    file.close()
                                    self.isFileSaved = True
                            # revoke percentage
                            totalIUs = len(self.finalResult.split(" ")) + self.revoke_count
                            revoke_percentage = self.revoke_count/totalIUs
                            self.revoke_count = 0
                            print("revoke_percentagef: " + str(revoke_percentage))

                            if not path.exists(self.results_file_name + "Revoke.txt"):
                                file = open(self.results_file_name + "Revoke.txt", "w+")
                                file.write(str(revoke_percentage) + "\n")
                                file.close()
                            else:
                                with open(self.results_file_name + "Revoke.txt", "a") as file:
                                    file.write(str(revoke_percentage) + "\n")
                                    file.close()
                            print(Fore.RED + "SAVED" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "NOT saving data" + Style.RESET_ALL)
                            self.isFileSaved = True
                    print(Fore.GREEN + "Commit: " + str(self.finalResult) + Style.RESET_ALL)
                    avgTime = self.sentence_prediction_total_time_final / len(self.finalResult.split(" "))
                    print("Average prediction time per word: " + str(avgTime) + "s")
                    self.finalResult = ""
                    self.sentence_prediction_total_time_final = 0
                    self.frames = None
            except:
                print("Exceptions happened")
                traceback.print_exc()