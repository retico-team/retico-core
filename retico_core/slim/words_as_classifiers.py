"""A module for grounded semantics"""

# retico
from retico_core.core import abstract
from retico_core.core.visual import ObjectFeaturesIU
from retico_core.core.text import SpeechRecognitionIU
from retico_core.slim.wac import WAC
from retico_core.slim.common import GroundedFrameIU

from collections import deque
import numpy as np
import os
import os.path as osp
from tqdm import tqdm
import sys
import threading
import time


class WordsAsClassifiersModule(abstract.AbstractModule):
    """A model of grounded semantics. 

    Attributes:
        model_dir(str): directory where WAC classifiers are saved
    """

    @staticmethod
    def name():
        return "SLIM Group WAC Model"

    @staticmethod
    def description():
        return "WAC Visually-Grounded Model"

    @staticmethod
    def input_ius():
        return [ObjectFeaturesIU,SpeechRecognitionIU]

    @staticmethod
    def output_iu():
        return GroundedFrameIU

    def __init__(self, wac_dir, **kwargs):
        """Loads the WAC models.

        Args:
            model_dir (str): The path to the directory of WAC classifiers saved as pkl files.
        """
        super().__init__(**kwargs)
        self.wac = WAC(wac_dir)
        self.word_buffer = None
        self.itts = 0
        self.train_mode = False
        self.queue = deque(maxlen=1)

    def train_wac(self):
        wac = self.wac.copy()
        print('updating negatives')
        wac.create_negatives()
        print('training')
        wac.train()
        print('persisting')
        wac.persist_model()

    def process_update(self, update_message):
        for iu,um in update_message:
            if um == abstract.UpdateType.ADD:
                self.process_iu(iu)
            elif um == abstract.UpdateType.REVOKE:
                self.process_revoke(iu)


    def process_iu(self, input_iu):
        frame = {}
        # print(input_iu)
        if isinstance(input_iu, SpeechRecognitionIU):
            self.word_buffer = input_iu.get_text().lower().split()[-1]
            if not self.train_mode:
                frame['word_to_find'] = self.word_buffer
        
        # when new objects are observed (i.e., not SpeechRecognitionIUs)
        if isinstance(input_iu, ObjectFeaturesIU):
            objects = input_iu.payload
            if objects is None: return
            # WAC wants a list of intents (objectIDs) and their corresponding features in a tuple
            if len(objects) == 0: return
            intents = objects.keys()
            features = [np.array(objects[obj_id]) for obj_id in objects]
            
            if not self.train_mode:
                word,_ = self.wac.best_word((intents, features))
                frame['best_known_word'] = word
            
            if self.train_mode:
                if self.word_buffer is not None:
                    self.wac.add_positive_observation(self.word_buffer, features[0])
                    self.itts += 1
                    if self.itts % 100 == 0:
                        t = threading.Thread(target=self.train_wac)
                        t.start()

            if self.word_buffer is not None:
                target = self.wac.best_object(self.word_buffer, (intents, features))
                if target is not None: 
                    frame['best_object'] = target[0] 
                    frame['obj_confidence'] = target[1] 

        if len(frame) == 0: return
        output_iu = self.create_iu(input_iu)
        output_iu.set_frame(frame)
        output_update = abstract.UpdateMessage.from_iu(output_iu, "add")
        self.append(output_update)


    def setup(self):
        if not self.train_mode:
            self.wac.load_model()
