import os
import numpy as np
import threading
from os import path
from retico_core.core import abstract
from retico_core.core.text import SpeechRecognitionIU
from retico_core.core.audio import AudioIU
from retico_core.core.debug import DebugModule

# word filtering
from nltk.corpus import wordnet as wn
from nltk.corpus import words

#voice activity
# import webrtcvad

# For managing audio file
import wave
import pyaudio
import librosa
import time

#Importin Pytorch
import torch

#Importing Wav2Vec
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer, Wav2Vec2CTCTokenizer

# handling errors
import traceback

# logger
from colorama import Fore
from colorama import Style

# regular expression for filtering
import re

class OfflineASRModule(abstract.AbstractModule):
    """A Module that recognizes speech locally by utilizing the Wav2Vec2-Base-960h base model from huggingface."""

    def __init__(self, test_mode=False, **kwargs):
        """Initialize the ASR module with the given arguments.
            roughly about 16 input_ius equals to 1 seconds

        Args:
        """
        self.predictions = []
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

    def WordLookup(self, word):
        """
            This function looks for a word in the WordNet corpus

            Parameters:
                word (string): The word we are looking for
            Returns:
                boolean: true if word is valid and false otherwise
                """
        # TODO: WordNet and nltk corpus mistakes some common words (e.g. "YOU")
        if len(word) == 1:
            return self.OneLetterWord(word)
        if word.lower() in words.words() or word.capitalize() in words.words(): ## if you use words corpus
        #if len(wn.synsets(word)) > 0: ## if you use WordNet corpus
            return True
        return False

    def OneLetterWord(self, word):
        """
            This function filters out the only two one letter words in English "A" and "I" since nltk mistakes about it

            Parameters:
                word (string): The word we are looking for
            Returns:
                boolean: true if word is a valid one letter word and false otherwise
        """
        if word.upper() == "A" or word.upper() == "I":
            return True
        return False

    def NormalizeSpaces(self, string1, string2):
        """
            This function takes in two string and resolves how many spaces you need in between to properly add them.

            Parameters:
                string1 (string): The first string
                string2 (string): The second string

            Returns:
                string: the properly concatenated string

            Example:
                    stringToLookFor: "I DO NOT KNOW YOU BUT I WILL FI"
                    stringToLookIn: "ND YOU AND"

                    returns: 'I DO NOT KNOW YOU BUT I WILL FIND YOU AND'

        """
        if string1.endswith(" ") or string2.startswith(" "):
            return string1 + string2

        string1Split = string1.split(" ")
        string2Split = string2.split(" ")
        wordToLook = string1Split[len(string1Split) - 1] + string2Split[0]
        if self.WordLookup(wordToLook):
            return string1 + string2
        return string1 + " " + string2

    def TrimPrediction(self, sentence):
        """
            This function takes in a string and trims the start and end depending on whether the start and end is valid English word

            Parameters:
                sentence (string): The string that contains the prediction

            Returns:
                string: trimmed string

            Example:
                sentence: "ddd I LIVE IN MAINE ddd"

                returns: "I LIVE IN MAINE"

        """
        splitted = sentence.split(" ")

        try:
            if len(splitted) >= 1:
                if not self.WordLookup(splitted[0]):
                    sentence = sentence.split(' ', 1)[1]
                if not self.WordLookup(splitted[len(splitted) - 1]):
                    sentence = sentence.rsplit(' ', 1)[0]
            return sentence
        except IndexError:
            return sentence

    def TrimBeginningOfString(self, string):
        """
            This function takes in a string and trims the start depending on whether the start is valid English word

            Parameters:
                sentence (string): The string that contains the prediction

            Returns:
                string: trimmed string

            Example:
                sentence: "ddd I LIVE IN MAINE"

            returns: "I LIVE IN MAINE"

        """
        try:
            result = string
            result = result.split(' ', 1)[1]
        except IndexError:
            result = ""
        return result

    def GetProperStringToAdd(self, stringToLookFor, stringToLookIn):
        """
            This function takes in two strings and returns the best substring of stringToLookIn to merge with stringToLookFor without loss of data.

            Parameters:
            stringToLookFor (string): The string that contains the prediction from the beginning
            stringToLookIn (string): The string that contains the next partial prediction

            Returns:
            string: the part of the stringToLookIn that is not in stringToLookFor

            Example:
                stringToLookFor: "I DO NOT KNOW YOU BUT I WILL FI"
                stringToLookIn: "I WILL FIND YOU AND"

                returns: 'ND YOU AND'

        """
        copyOfStringToLookFor = stringToLookFor
        while copyOfStringToLookFor != "":
            if stringToLookIn.startswith(copyOfStringToLookFor):
                lenToTrim = len(copyOfStringToLookFor)
                stringToLookIn = stringToLookIn[lenToTrim:]
                return stringToLookIn
            elif self.TrimBeginningOfString(stringToLookIn).startswith(copyOfStringToLookFor):
                lenToTrim = len(copyOfStringToLookFor)
                stringToLookIn = self.TrimBeginningOfString(stringToLookIn)[lenToTrim:]
                return stringToLookIn
            copyOfStringToLookFor = copyOfStringToLookFor[1:]

        return self.TrimPrediction(stringToLookIn)

    def GetFileSaveStatus(self):
        return self.isFileSaved
    def PredictSpeech(self):  # inner function
        # when we reach word three length, we know where to trim off and how much of info is permanent
        wordThreeLength = 0
        print("START")
        while self.predict_thread_on is True:
            if self.first:
                time.sleep(0.7)
                self.first = False
            else:
                time.sleep(0.07)
            try:
                # latency testing varialbe
                process_start_time = time.time()

                if self.test_mode:
                    audio = self.frames
                else:
                    currentFrames = self.frames
                    if path.exists(self.wave_output_filename):
                        os.remove(self.wave_output_filename)
                    wf = wave.open(self.wave_output_filename, 'wb')
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.format))
                    wf.setframerate(self.rate)
                    wf.writeframes(b''.join(currentFrames))
                    wf.close()
                    audio, rate = librosa.load(self.wave_output_filename, sr=16000)

                    # raw = b''.join(currentFrames)
                    # raw = np.frombuffer(raw, dtype='int32')
                    # audio = raw / 2147483648

                someTime = time.time()

                if audio is None:
                    print("AUDIO IS NONE")
                    continue
                if len(audio) == 0:
                    print("AUDIO IS NONE")
                    continue
                input_values = self.tokenizer(audio, return_tensors="pt").input_values
                logits = self.model(input_values).logits
                prediction = torch.argmax(logits, dim=-1)
                transcription = self.tokenizer.batch_decode(prediction)[0]
                #print("before trim: " + str(transcription))
                transcription = self.TrimPrediction(transcription)
                transcription = re.sub('[.,!/;-@#$%^&*?]', '', transcription)
                # print("transcription: " + str(transcription))
                someTimeTwo = time.time()
                # optimization
                wordCount = len(transcription.split(" "))
                self.wordCountAtm = wordCount  # self.wordCountAtm + wordCount

                # this tells us the position where to cut off chunks, or how much of the sentence is permanent
                if self.wordCountAtm >= 2 and wordThreeLength == 0:
                    if not self.test_mode:
                        wordThreeLength = int(len(currentFrames) / wordCount * 2)  # len(currentFrames) # the 2 says the size upto second word

                if self.lastTranscription != transcription:
                    self.previousResultTime = time.time()
                    self.lastTranscription = transcription

                # reached 5 word limit, means we can cut of upto two word length
                if self.wordCountAtm >= 5:
                    if self.test_mode:
                        lengthToRemove = int(len(self.frames) * 0.35) # upto 40% size is two words, roughly
                        self.frames = self.frames[lengthToRemove:]
                    else:
                        self.frames = self.frames[wordThreeLength:]
                    wordThreeLength = 0
                    self.previousResult = self.result
                    # TODAY self.previousResultTime = time.time()
                    currentResult = self.result
                    self.result = self.NormalizeSpaces(self.result, self.GetProperStringToAdd(self.result, transcription))
                    generatedIUs = self.findNewIUs(currentResult, self.result)
                    for iu in generatedIUs:
                        if iu.startswith("Revoke"):
                            self.revoke_count = self.revoke_count + 1
                            print(Fore.RED + str(iu) + Style.RESET_ALL)
                        else:
                            print(Fore.CYAN + str(iu) + Style.RESET_ALL)

                    # end time for latency test
                    self.sentence_prediction_total_time = self.sentence_prediction_total_time + (time.time() - process_start_time)

                if len(transcription.split(" ")) == len(self.last_pred.split(" ")):     # word level
                    if self.last_pred != transcription:     # sentence level
                        self.last_pred = transcription
                        self.silence_start_time = time.time()

                elif len(transcription.split(" ")) > len(self.last_pred.split(" ")):
                    self.last_pred = transcription
                    self.silence_start_time = time.time()
                else:
                    self.last_pred = transcription
                    self.silence_start_time = time.time()

                currentTime = time.time()
                # print("OUTSIDE currentTime - self.silence_start_time: " + str(currentTime - self.silence_start_time))
                # print("OUTSIDE currentTime - self.previousResultTime: " + str(currentTime - self.previousResultTime))
                # silence limit 0.8 seconds taking acount the processing delay to make it a second, previousResultTime indicates that although there is no silence, no new info came up
                if currentTime - self.silence_start_time >= 0.8 or currentTime - self.previousResultTime >=2.0:
                    # print("currentTime - self.silence_start_time: " + str(currentTime - self.silence_start_time))
                    # print("currentTime - self.previousResultTime: " + str(currentTime - self.previousResultTime))
                    self.silence_start_time = time.time()
                    if path.exists(self.wave_output_filename):
                        os.remove(self.wave_output_filename)
                    if self.test_mode:
                        self.frames = None
                    else:
                        self.frames = []
                    self.finalResult = self.result + self.GetProperStringToAdd(self.result, self.last_pred)
                    generatedIUs = self.findNewIUs(self.result, self.finalResult)
                    for iu in generatedIUs:
                        if iu.startswith("Revoke"):
                            self.revoke_count = self.revoke_count + 1
                            print(Fore.RED + str(iu) + Style.RESET_ALL)
                        else:
                            print(Fore.CYAN + str(iu) + Style.RESET_ALL)
                    self.result = ""
                    self.previousResult = ""
                    self.previousResultTime = time.time()
                    # TODAY
                    self.lastTranscription = ""
                    # TODAY
                    self.last_pred = ""
                    self.sentence_prediction_total_time_final = self.sentence_prediction_total_time
                    self.sentence_prediction_total_time = 0
                    #print("RESET")

                if self.result == "" and self.finalResult != "":
                    if self.test_mode:
                        # TODAY print("revoke count: " + str(self.revoke_count) + ", " + "total count: " + str(len(self.finalResult.split(" "))))
                        print(Fore.RED + "saving data" + Style.RESET_ALL)
                        # latency
                        if not path.exists("localAsrLatency.txt"):
                            file = open("localAsrLatency.txt", "w+")
                            file.write(str(self.sentence_prediction_total_time_final/len(self.finalResult.split(" "))) + "\n")
                            file.close()
                        else:
                            with open("localAsrLatency.txt", "a") as file:
                                file.write(str(self.sentence_prediction_total_time_final/len(self.finalResult.split(" "))) + "\n")
                                file.close()
                        # prediction
                        if not path.exists("localAsrPrediction.txt"):
                            file = open("localAsrPrediction.txt", "w+")
                            file.write(str(self.latestFile) + ", " + str(self.finalResult) + "\n")
                            #print(Fore.CYAN + "TODAY: file name: " + self.latestFile + Style.RESET_ALL)
                            #print(Fore.CYAN + "TODAY: pred: " + self.finalResult + Style.RESET_ALL)
                            file.close()
                            self.isFileSaved = True
                        else:
                            with open("localAsrPrediction.txt", "a") as file:
                                file.write(str(self.latestFile) + ", " + str(self.finalResult) + "\n")
                                #print(Fore.CYAN + "TODAY: file name: " + self.latestFile + Style.RESET_ALL)
                                #print(Fore.CYAN + "TODAY: pred: " + self.finalResult + Style.RESET_ALL)
                                file.close()
                                self.isFileSaved = True
                        # revoke percentage
                        totalIUs = len(self.finalResult.split(" ")) + self.revoke_count
                        revoke_percentage = self.revoke_count/totalIUs
                        self.revoke_count = 0
                        print("revoke_percentagef: " + str(revoke_percentage))

                        if not path.exists("localAsrRevoke.txt"):
                            file = open("localAsrRevoke.txt", "w+")
                            file.write(str(revoke_percentage) + "\n")
                            file.close()
                        else:
                            with open("localAsrRevoke.txt", "a") as file:
                                file.write(str(revoke_percentage) + "\n")
                                file.close()
                        print(Fore.RED + "SAVED" + Style.RESET_ALL)
                    print(Fore.GREEN + "Commit: " + str(self.finalResult) + Style.RESET_ALL)
                    avgTime = self.sentence_prediction_total_time_final / len(self.finalResult.split(" "))
                    predition_iu = SpeechRecognitionIU(DebugModule)
                    self.predictions.append(self.finalResult)
                    predition_iu.set_asr_results(self.predictions, self.finalResult, 70.0, 70.0, True)
                    predition_update = abstract.UpdateMessage.from_iu(predition_iu, "add")
                    self.append(predition_update)
                    print("Average prediction time per word: " + str(avgTime) + "s")
                    #print(Fore.BLUE + "file name: " + str(self.latestFile) + Style.RESET_ALL)
                    self.finalResult = ""
                    self.sentence_prediction_total_time_final = 0
                # else:
                    # print(Fore.GREEN + "prediction: " + str(self.result) + Style.RESET_ALL)
            except:
                print("Exceptions happened")
                traceback.print_exc()