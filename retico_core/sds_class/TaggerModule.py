from retico_core.core import abstract
from sds_class_iu import SimpleTextIU
import nltk


class TaggerModule(abstract.AbstractModule):

    @staticmethod
    def name():
        return "TaggerModule"

    @staticmethod
    def description():
        return "A Module that produces parts of speech"

    @staticmethod
    def input_ius():
        return [SimpleTextIU]

    @staticmethod
    def output_iu():
        return SimpleTextIU

    def __init__(self, **kwargs):
        """Initializes the OpenDialModule.

        Args:
            domain_dir (str): The path to the directory of the domain model (XML) for OpenDial
        """
        super().__init__(**kwargs)
        self.prefix = []

    def process_update(self, update_message):
        for iu,um in update_message:
            if um == abstract.UpdateType.ADD:
                update = self.process_iu(iu)
            elif um == abstract.UpdateType.REVOKE:
                update = self.revoke(iu)
        return update


    def process_iu(self, input_iu):
        print(input_iu)
        self.prefix.append(input_iu.get_word())
        pos = nltk.pos_tag(self.prefix)
        print(pos)
        new_iu = self.create_iu(input_iu)
        new_iu.payload = pos[-1][1]
        new_update = abstract.UpdateMessage.from_iu(new_iu, "add")
        return new_update

    def revoke(self, input_iu):
        print(input_iu)
        self.prefix.pop()

    def start(self):
        print('TaggerModule started!')