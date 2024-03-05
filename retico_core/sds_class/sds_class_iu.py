
from retico_core.core import abstract


class SimpleTextIU(abstract.IncrementalUnit):
    """
    """

    @staticmethod
    def type():
        return "SimpleTextIU"

    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None, word=None,
                 **kwargs):
        super().__init__(creator=creator, iuid=iuid, previous_iu=previous_iu,
                         grounded_in=grounded_in, payload=word)
        self.word = word

    def get_word(self):
        return self.word
    
class SimpleTextUpdate(abstract.UpdateMessage):
    @staticmethod
    def type():
        return "SimpleUpdateMessage"
    
    def __init__(self, creator=None, iuid=0, previous_iu=None, grounded_in=None, word=None,
                 **kwargs):
        super().__init__()
        text_iu = SimpleTextIU(creator, iuid, previous_iu, grounded_in, word)
        self.add_iu(text_iu,"add")