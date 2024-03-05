from retico_core.core import abstract
from retico_core.core.text import SpeechRecognitionIU
from retico_core.interop.zeromq.io import ZeroMQIU


class PSItoSpeechRecognitionModule(abstract.AbstractModule):

    """A Module for converting ZeroMQIU with PSI ASR to SpeechRecognitionIU

    Attributes:
        
    """
    @staticmethod
    def name():
        return "PSItoSpeechRecognitionModule Module"

    @staticmethod
    def description():
        return "A Module for converting PSI json to a retico SpeechRecognitionIU"

    @staticmethod
    def output_iu():
        return SpeechRecognitionIU 

    @staticmethod
    def input_ius():
        return [ZeroMQIU] 

    def __init__(self, **kwargs):
        """Initializes the ZeroMQReader.

        Args: topic(str): the topic/scope where the information will be read.
            
        """
        super().__init__(**kwargs)
        self.latest_input_iu = None

    def process_update(self, update_message):
        for iu,um in update_message:
            if um == abstract.UpdateType.ADD:
                update = self.process_iu(iu)
            elif um == abstract.UpdateType.REVOKE:
                update = self.process_revoke(iu)
        return update    

    def process_iu(self, input_iu):
        '''
        This assumes that the message is json formatted, then packages it as payload into an IU
        '''
        msg = input_iu.payload['message']
        if "Text" in msg:
           output_iu = self.create_iu()
           p = msg['Alternates']
           t = msg['Text']
           s = 0.0 # Azure doesn't have a stability measure
           c = msg['Confidence']
           f = msg['IsFinal']
           output_iu.set_asr_results(p, t, s, c, f)
           self.latest_input_iu = input_iu
           output_update = abstract.UpdateMessage.from_iu(output_iu, "add")
           
           return output_update


        
    def setup(self):
        pass