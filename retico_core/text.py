"""
Text Module
===========

This file defines general incremental units and incremental modules that deal with text.
This may be a transcription that is generated from an ASR module, a text IU containing
words to be synthesized by a TTS module or other general purpose text.
"""

import retico_core


def get_text_increment(module, new_text):
    """Compares the full text given by the asr with the IUs that are already
    produced (current_output) and returns only the increment from the last update. It
    revokes all previously produced IUs that do not match.

    For example, if the ``current_output`` of the module consists of the follwing IUs:
        [The] [quick] [bright]
    and the ``new_text`` is:
        "The quick brown fox"
    The function would return a new UpdateMessage
        UpdateMessage([bright], REVOKE)
    and the follwing new tokens:
        ["brown", "fox"]

    This function does not create UPDATE messages (e.g., updating [bright] to [brown] in
    the example above), but rather REVOKEs all unfitting IUs.

    Args:
        module (IncrementalModule): The incremental module that produces ``TextIU`` s
        new_text (str): The full new text that should be incrementalized

    Returns:
        UpdateMessage, list: Returns an update message containing the IUs that were
            revoked (with the REVOKE update type) and a list of new tokens (strings) for
            which new IUs should be created.
    """
    um = retico_core.UpdateMessage()
    tokens = new_text.strip().split(" ")
    if tokens == [""]:
        return um, []

    new_tokens = []
    iu_idx = 0
    token_idx = 0
    while token_idx < len(tokens):
        if iu_idx >= len(module.current_output):
            new_tokens.append(tokens[token_idx])
            token_idx += 1
        else:
            current_iu = module.current_output[iu_idx]
            iu_idx += 1
            if tokens[token_idx] == current_iu.text:
                token_idx += 1
            else:
                current_iu.revoked = True
                um.add_iu(current_iu, retico_core.UpdateType.REVOKE)
    module.current_output = [iu for iu in module.current_output if not iu.revoked]

    return um, new_tokens


class TextIU(retico_core.IncrementalUnit):
    """An IU that contains text."""

    @staticmethod
    def type():
        return "Text IU"

    def get_text(self):
        """Return the text contained in the IU.

        Returns:
            str: The text contained in the IU.
        """
        return self.payload

    def set_text(self, text):
        """Sets the text contained in the IU.

        Args:
            text (str): The new text of the IU
        """
        self.payload = text

    text = property(get_text, set_text)


class GeneratedTextIU(TextIU):
    """An IU that contains generated text.

    This includes information about whether the text should be dispatched once
    it has been transformed into speech."""

    @staticmethod
    def type():
        return "Generated Text IU"

    def __init__(self, dispatch=False, **kwargs):
        super().__init__(**kwargs)
        self.dispatch = dispatch


class SpeechRecognitionIU(TextIU):
    """An IU that contains information about recognized speech."""

    @staticmethod
    def type():
        return "Speech Recgonition IU"

    def __init__(
        self, creator, iuid=0, previous_iu=None, grounded_in=None, payload=None
    ):
        super().__init__(
            creator,
            iuid=iuid,
            previous_iu=previous_iu,
            grounded_in=grounded_in,
            payload=payload,
        )
        self.predictions = None
        self.stability = None
        self.confidence = None
        self.payload = payload
        self.text = None
        self.final = False

    def set_asr_results(self, predictions, text, stability, confidence, final):
        """Set the asr results for the SpeechRecognitionIU.

        Args:
            predictions (list): A list of predictions. This will also set the
                payload. The last prediction in this list should be the latest
                and best prediction.
            text (str): The text of the latest prediction
            stability (float): The stability of the latest prediction
            confidence (float): The confidence in the latest prediction
            final (boolean): Whether the prediction is final
        """
        self.predictions = predictions
        self.payload = predictions
        self.text = text
        self.stability = stability
        self.confidence = confidence
        self.final = final

    def get_text(self):
        return self.text


class TextRecorderModule(retico_core.AbstractConsumingModule):
    """A module that writes the received text into a file."""

    @staticmethod
    def name():
        return "Text Recorder Module"

    @staticmethod
    def description():
        return "A module that writes received TextIUs to file"

    @staticmethod
    def input_ius():
        return [TextIU, GeneratedTextIU, SpeechRecognitionIU]

    def __init__(self, filename, separator="\t", **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.separator = separator
        self.txt_file = None

    def setup(self):
        self.txt_file = open(self.filename, "w")

    def shutdown(self):
        if self.txt_file:
            self.txt_file.close()
            self.txt_file = None

    def process_update(self, update_message):
        for iu, ut in update_message:
            if ut != retico_core.UpdateType.ADD:
                continue
            if self.txt_file:
                self.txt_file.write(str(iu.grounded_in.creator))
                self.txt_file.write(self.separator)
                self.txt_file.write(str(iu.created_at))
                self.txt_file.write(self.separator)
                self.txt_file.write(iu.get_text())
                if isinstance(iu, GeneratedTextIU):
                    self.txt_file.write(self.separator)
                    self.txt_file.write(str(iu.dispatch))
                if isinstance(iu, SpeechRecognitionIU):
                    self.txt_file.write(self.separator)
                    self.txt_file.write(str(iu.predictions))
                    self.txt_file.write(self.separator)
                    self.txt_file.write(str(iu.stability))
                    self.txt_file.write(self.separator)
                    self.txt_file.write(str(iu.confidence))
                    self.txt_file.write(self.separator)
                    self.txt_file.write(str(iu.final))
                self.txt_file.write("\n")


class TextTriggerModule(retico_core.AbstractTriggerModule):
    """A trigger module that creates a TextIU once its trigger function is called."""

    @staticmethod
    def name():
        return "Text Trigger Module"

    @staticmethod
    def description():
        return "A trigger module that creates a TextIU once its triggered"

    @staticmethod
    def output_iu():
        return GeneratedTextIU

    def __init__(self, dispatch=True, **kwargs):
        super().__init__(**kwargs)
        self.dispatch = dispatch

    def trigger(self, data={}, update_type=retico_core.UpdateType.ADD):
        text = data.get("text", "This is a trigger test")
        output_iu = self.create_iu()
        output_iu.payload = text
        output_iu.dispatch = self.dispatch
        self.append(retico_core.UpdateMessage.from_iu(output_iu, update_type))


class TextDispatcherModule(retico_core.AbstractModule):
    """
    A Moduel that turns SpeechRecognitionIUs or TextIUs into GeneratedTextIUs
    that have the dispatch-flag set.
    """

    @staticmethod
    def name():
        return "ASR to TTS Module"

    @staticmethod
    def description():
        return "A module that uses SpeechRecognition IUs and outputs dispatchable IUs"

    @staticmethod
    def input_ius():
        return [SpeechRecognitionIU, TextIU]

    @staticmethod
    def output_iu():
        return GeneratedTextIU

    def __init__(self, dispatch_final=True, **kwargs):
        super().__init__(**kwargs)
        self.dispatch_final = dispatch_final

    def process_update(self, update_message):
        um = retico_core.UpdateMessage()
        for iu, ut in update_message:
            output_iu = self.create_iu(iu)
            output_iu.payload = iu.get_text()
            output_iu.dispatch = True
            if isinstance(iu, SpeechRecognitionIU) and self.dispatch_final:
                output_iu.dispatch = iu.final
            output_iu.committed = iu.committed
            um.add_iu(output_iu, ut)
        return um


class IncrementalizeASRModule(retico_core.AbstractModule):
    """A module that takes the output of a non-incremental ASR module, where each IU
    contains the full text of the speech recognition and produces increments based on
    the difference to the last output.
    """

    @staticmethod
    def name():
        return "Incrementalize ASR Module"

    @staticmethod
    def description():
        return (
            "A module that takes SpeechRecognitionIUs and emits only the "
            + "increments from the previous iu"
        )

    @staticmethod
    def input_ius():
        return [SpeechRecognitionIU]

    @staticmethod
    def output_iu():
        return SpeechRecognitionIU

    def __init__(self, threshold=0.8, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def process_update(self, update_message):
        um = retico_core.UpdateMessage()
        for iu, ut in update_message:
            if ut != retico_core.UpdateType.ADD:
                continue
            if iu.stability < self.threshold and iu.confidence == 0.0:
                continue
            current_text = iu.get_text()
            if self.current_input:
                um, current_text = retico_core.text.get_text_increment(
                    self, current_text
                )
            if len(current_text) == 0:
                continue

            output_iu = self.create_iu(iu)

            # Just copy the input IU
            output_iu.set_asr_results(
                iu.predictions,
                current_text,
                iu.stability,
                iu.confidence,
                iu.final,
            )
            self.current_input.append(output_iu)

            if output_iu.final:
                self.current_input = []
                output_iu.committed = True

            um.add_iu(output_iu, retico_core.UpdateType.ADD)

        return um


class EndOfUtteranceModule(retico_core.AbstractModule):
    """A module that looks for the "final" flag of a SpeechRecognitionIU and forwards
    an EndOfTurnIU when the SpeechRecognition detected that the utterance is finished.
    """

    @staticmethod
    def name():
        return "End of Utterance Module"

    @staticmethod
    def description():
        return "A module that forwards the end of utterance from the ASR output"

    @staticmethod
    def input_ius():
        return [SpeechRecognitionIU]

    @staticmethod
    def output_iu():
        return retico_core.dialogue.EndOfTurnIU

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_update(self, update_message):
        um = retico_core.UpdateMessage()
        for iu, ut in update_message:
            if ut == retico_core.UpdateType.ADD:
                if iu.final:
                    outiu = self.create_iu(iu)
                    outiu.set_eot(1.0, False)
                    um.add_iu(outiu, retico_core.UpdateType.ADD)
        return um
