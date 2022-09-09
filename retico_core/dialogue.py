"""
Dialogue Module
===============

This module contains basic dialogue functionality, like a :class:`.DialogueActIU` for
a dialogue manager.
"""

import retico_core
import time


class DialogueActIU(retico_core.IncrementalUnit):
    """A Dialog Act Incremental Unit.

    This IU represents a Dialogue Act together with concepts and their
    values. In this implementation only a single act can be expressed with a
    single IU.

    Attributes:
        act (string): A representation of the current act as a string.
        concepts (dict): A dictionary of names of concepts being mapped on to
            their actual values.
    """

    @staticmethod
    def type():
        return "Dialogue Act Incremental Unit"

    def __init__(
        self,
        creator=None,
        iuid=0,
        previous_iu=None,
        grounded_in=None,
        payload=None,
        act=None,
        concepts=None,
        **kwargs
    ):
        """Initialize the DialogueActIU with act and concepts.

        Args:
            act (string): A representation of the act.
            concepts (dict): A representation of the concepts as a dictionary.
        """
        super().__init__(
            creator=creator,
            iuid=iuid,
            previous_iu=previous_iu,
            grounded_in=grounded_in,
            payload=payload,
        )
        self.act = act
        self.concepts = {}
        if concepts:
            self.concepts = concepts
        self.confidence = 0.0

    def set_act(self, act, concepts=None, confidence=1.0):
        """Set the act and concept of the IU.

        Old acts or concepts will be overwritten.

        Args:
            act (string): The act of the IU as a string.
            concepts (dict): A dictionary containing the new concepts.
            confidence (float): Confidence of the act prediction
        """
        self.act = act
        if concepts:
            self.concepts = concepts
        self.confidence = confidence
        self.payload = (act, concepts)


class DispatchableActIU(DialogueActIU):
    """A Dialogue Act Incremental Unit that can has the information if it should
    be dispatched once it has been transformed into speech.

    Attributes:
        dispatch (bool): Whether the speech resulting from this IU should be
            dispatched or not.
    """

    def __init__(self, dispatch=False, **kwargs):
        super().__init__(**kwargs)
        self.dispatch = dispatch


class EndOfTurnIU(retico_core.IncrementalUnit):
    """An incremental unit used for prediction of the end of the turn. This
    information may be used by a dialogue management module to plan next turns
    and enabling realistic turn taking.
    """

    @staticmethod
    def type():
        return "End-of-Turn Incremental Unit"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.probability = 0.0
        self.is_speaking = False

    def set_eot(self, probability=0.0, is_speaking=False):
        """Set the end-of-turn probability and a flag if the interlocutor is
        currently speaking (VAD).

        Args:
            probability (float): The probability that the turn is ending.
            is_speaking (bool): Whether or not the interlocutor is speaking.
        """
        self.is_speaking = is_speaking
        self.probability = probability


class DialogueActRecorderModule(retico_core.AbstractConsumingModule):
    """A module that writes dispatched dialogue acts to file."""

    @staticmethod
    def name():
        return "Dialogue Act Recorder Module"

    @staticmethod
    def description():
        return "A module that writes dialogue acts into a file."

    @staticmethod
    def input_ius():
        return [DialogueActIU, DispatchableActIU]

    def __init__(self, filename, separator="\t", **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.separator = separator
        self.txt_file = None

    def setup(self):
        self.txt_file = open(self.filename, "w")

    def prepare_run(self):
        self.start_time = time.time()

    def shutdown(self):
        if self.txt_file:
            self.txt_file.close()
            self.txt_file = None

    def process_update(self, update_message):
        for iu, ut in update_message:
            if ut != retico_core.UpdateType.ADD:
                continue
            if self.txt_file:
                self.txt_file.write("dialogue_act")
                self.txt_file.write(self.separator)
                self.txt_file.write(str(iu.creator).split(" ")[-1])
                self.txt_file.write(self.separator)
                if iu.created_at < self.start_time:
                    self.start_time = iu.created_at
                self.txt_file.write(str(int((iu.created_at - self.start_time) * 1000)))
                self.txt_file.write(self.separator)
                self.txt_file.write("-1")
                self.txt_file.write(self.separator)
                if iu.concepts.keys():
                    self.txt_file.write(iu.act + ":" + ",".join(iu.concepts.keys()))
                else:
                    self.txt_file.write(iu.act)
                if isinstance(iu, DispatchableActIU):
                    self.txt_file.write(self.separator)
                    self.txt_file.write(str(iu.dispatch))
                self.txt_file.write("\n")


class DialogueActTriggerModule(retico_core.AbstractTriggerModule):
    @staticmethod
    def name():
        return "Dialogue Act Trigger Module"

    @staticmethod
    def description():
        return "A trigger module that emits a dialogue act when triggered."

    @staticmethod
    def output_iu():
        return DispatchableActIU

    def __init__(self, dispatch=True, **kwargs):
        super().__init__(**kwargs)
        self.dispatch = True

    def trigger(self, data={}, update_type=retico_core.UpdateType.ADD):
        output_iu = self.create_iu()
        output_iu.dispatch = self.dispatch
        output_iu.set_act(data.get("act", "greeting"), data.get("concepts", {}))
        self.append(retico_core.UpdateMessage.from_iu(output_iu, update_type))
