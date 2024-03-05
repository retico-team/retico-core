"""A module for processing received asr IUs from psi"""

# retico
from retico_core.core import abstract
from retico_core.core.text import SpeechRecognitionIU
from retico_core.interop.zeromq.io import ZeroMQIU

# psiAsrReceiver
import sys
import os
import json

class psiAsrReceiverModule(abstract.AbstractModule):
    """A module to handle json asr results from psi"""

    @staticmethod
    def name():
        return "psi asr receiver module"

    @staticmethod
    def description():
        return "A Module receiving ASR outputs from psi"

    @staticmethod
    def input_ius():
        return [ZeroMQIU]

    @staticmethod
    def output_iu():
        return SpeechRecognitionIU

    def __init__(self, **kwargs):
        """Initializes the psiReceiverModule.
        """
        super().__init__(**kwargs)
        self.all_ius = []
    
    def process_update(self, update_message):
        for iu,um in update_message:
            if um == abstract.UpdateType.ADD:
                self.process_iu(iu)
            elif um == abstract.UpdateType.REVOKE:
                self.process_revoke(iu)

    def process_iu(self, input_iu):
        originateTime = input_iu.payload['originatingTime']
        message = input_iu.payload['message']
        messageBroken = json.loads(message)
        totalList = messageBroken['TotalList']
        SignalsList = messageBroken['SignalsList']

        output_iu = None

        for i in range(0, len(totalList)):
            output_iu = self.create_iu(input_iu)


            final = False
            if totalList[i]["EditType"] == "Commit":
                final = True
            output_iu.set_asr_results(
            totalList[i]['EditType'],
            totalList[i]['Payload']['Text'],
            totalList[i]['GroundedInIU'],
            totalList[i]['TimeStamp'],
            final,
            )
            self.all_ius.append(output_iu)
            output_update = abstract.UpdateMessage.from_iu(output_iu, "add")
            self.append(output_update)

        return

    def setup(self):
        pass


