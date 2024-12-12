import unittest
from retico_core.core import text, UpdateType, dialogue
from mock_classes import MockText, MockGrounded, MockNetwork, MockTextFile, MockTextGen, MockUpdateMessage
from mock import patch
import io
import sys
import sys



'''
test format:
def test_X(self):
    #Arrange

        #Act

        #Assert
'''

# Test cases
class TestTextModule(unittest.TestCase):

    def test_get_text_increment_no_text(self):
        #Arrange
        mock_text = MockText()
        expected_result = []

        #Act
        _, result = text.get_text_increment(mock_text, "")

        #Assert
        self.assertEqual(result, expected_result)
    
    def test_get_text_increment(self):
        #Arrange
        mock_text = MockText()
        expected_result = ['text', 'file']

        #Act
        _, result = text.get_text_increment(mock_text, "testing text file")

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_iu_type(self):
        #Arrange
        expected_result = "Text IU"

        #Act
        result = text.TextIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_iu_get_text(self):
        #Arrange
        mock_text = MockText()
        expected_result = mock_text.payload

        #Act
        result = text.TextIU.get_text(mock_text)

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_iu_set_text(self):
        #Arrange
        mock_text = MockText()
        new_text = "Text IU"

        #Act
        text.TextIU.set_text(mock_text, new_text)

        #Assert
        self.assertEqual(mock_text.payload, new_text)

    def test_generated_text_iu_type(self):
        #Arrange
        expected_result = "Generated Text IU"

        #Act
        result = text.GeneratedTextIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_generated_text_iu_init(self):
        #Arrange
        mock_dispatch = True

        #Act
        result = text.GeneratedTextIU(dispatch=mock_dispatch, iuid="id")

        #Assert
        self.assertEqual(result.dispatch, mock_dispatch)

    def test_speech_recognition_type(self):
        #Arrange
        expected_result = "Speech Recgonition IU"

        #Act
        result = text.SpeechRecognitionIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    @patch('retico_core.core.abstract.IncrementalUnit._remove_old_links')
    def test_speech_recognition_init(self, old_mock):
        #Arrange
        old_mock.return_value = True
        mock_creator=MockNetwork()
        mock_iuid="id"
        mock_previous_iu="prev"
        mock_grounded_in=MockGrounded()
        mock_payload="pay"

        #Act
        result = text.SpeechRecognitionIU(creator=mock_creator,
                                          iuid=mock_iuid,
                                          previous_iu=mock_previous_iu,
                                          grounded_in=mock_grounded_in,
                                          payload=mock_payload)

        #Assert
        self.assertEqual(result.previous_iu, mock_previous_iu)
        self.assertEqual(result.iuid, mock_iuid)

    def test_speech_recognition_set_asr_results(self):
        #Arrange
        mock_text = MockText()
        mock_predictions = "pred"
        mock_new_text = "new_text"
        mock_stability = "stabil"
        mock_confidence = "completly"
        mock_final = "fin"
        
        #Act
        text.SpeechRecognitionIU.set_asr_results(self=mock_text,
                                                          predictions=mock_predictions,
                                                          text=mock_new_text,
                                                          stability=mock_stability,
                                                          confidence=mock_confidence,
                                                          final=mock_final)

        #Assert
        self.assertEqual(mock_text.predictions, mock_predictions)
        self.assertEqual(mock_text.text, mock_new_text)
        self.assertEqual(mock_text.stability, mock_stability)
        self.assertEqual(mock_text.confidence, mock_confidence)
        self.assertEqual(mock_text.final, mock_final)

    def test_speech_recognition_get_text(self):
        #Arrange
        mock_text = MockText()
        
        #Act
        result = text.SpeechRecognitionIU.get_text(mock_text)

        #Assert
        self.assertEqual(result, mock_text.text)

    def test_text_recorder_module_name(self):
        #Arrange
        expected_result = "Text Recorder Module"

        #Act
        result = text.TextRecorderModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_recorder_module_description(self):
        #Arrange
        expected_result = "A module that writes received TextIUs to file"

        #Act
        result = text.TextRecorderModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_recorder_module_input_ius(self):
        #Arrange
        expected_result = [text.TextIU, text.GeneratedTextIU, text.SpeechRecognitionIU]

        #Act
        result = text.TextRecorderModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_recorder_module_init(self):
        #Arrange
        mock_filename = "mock_file"
        mock_separator="\n"
        expected_txt = None

        #Act
        result = text.TextRecorderModule(filename=mock_filename,
                                         separator=mock_separator)

        #Assert
        self.assertEqual(result.filename, mock_filename)
        self.assertEqual(result.separator, mock_separator)
        self.assertEqual(result.txt_file, expected_txt)

    def test_text_recorder_module_input_shutdown(self):
        #Arrange
        mock_text = MockText()
        mock_text.txt_file = MockTextFile()
        expected_result = None

        #Act
        text.TextRecorderModule.shutdown(mock_text)

        #Assert
        self.assertEqual(mock_text.txt_file, expected_result)

    def test_text_recorder_module_input_process_update(self):
        #Arrange
        mock_text = MockText()
        mock_text_gen = MockTextGen()
        mock_text.txt_file = MockTextFile()
        mock_update_message = [(mock_text,UpdateType.ADD), 
                               (mock_text, UpdateType.REVOKE), 
                               (mock_text_gen,UpdateType.ADD)]
        expected_result = 22

        #Act
        text.TextRecorderModule.process_update(mock_text, mock_update_message)

        #Assert
        self.assertEqual(mock_text.txt_file.writes, expected_result)

    def test_text_trigger_module_name(self):
        #Arrange
        expected_result = "Text Trigger Module"

        #Act
        result = text.TextTriggerModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_trigger_module_description(self):
        #Arrange
        expected_result = "A trigger module that creates a TextIU once its triggered"

        #Act
        result = text.TextTriggerModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_trigger_module_output_iu(self):
        #Arrange
        expected_result = text.GeneratedTextIU

        #Act
        result = text.TextTriggerModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_trigger_module_init(self):
        #Arrange
        mock_dispatch = False
        #Act
        result = text.TextTriggerModule(dispatch=mock_dispatch)

        #Assert
        self.assertEqual(result.dispatch, mock_dispatch)

    @patch('retico_core.core.UpdateMessage.from_iu')
    def test_text_trigger_module_trigger(self, mock_from_iu):
        #Arrange
        iu_return = "new_iu"
        mock_from_iu.return_value = iu_return
        mock_text = MockText()
        expected_result = [iu_return]
        #Act
        text.TextTriggerModule.trigger(mock_text)

        #Assert
        self.assertEqual(mock_text.messages, expected_result)

    def test_text_dispatcher_module_name(self):
        #Arrange
        expected_result = "ASR to TTS Module"

        #Act
        result = text.TextDispatcherModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_dispatcher_module_description(self):
        #Arrange
        expected_result = "A module that uses SpeechRecognition IUs and outputs dispatchable IUs"

        #Act
        result = text.TextDispatcherModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_dispatcher_module_input_ius(self):
        #Arrange
        expected_result = [text.SpeechRecognitionIU, text.TextIU]

        #Act
        result = text.TextDispatcherModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_dispatcher_module_output_iu(self):
        #Arrange
        expected_result = text.GeneratedTextIU

        #Act
        result = text.TextDispatcherModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_dispatcher_module_init(self):
        #Arrange
        mock_dispatch = False
        #Act
        result = text.TextDispatcherModule(dispatch_final=mock_dispatch)

        #Assert
        self.assertEqual(result.dispatch_final, mock_dispatch)

    @patch('retico_core.core.abstract.UpdateMessage')
    def test_text_dispatcher_module_process_update(self, mock_update):
        #Arrange
        mock_update.return_value = MockUpdateMessage()
        mock_text = MockText()
        mock_text.dispatch_final = True
        mock_text.committed = False
        mock_update_message = [(mock_text,UpdateType.ADD), 
                               (mock_text, UpdateType.REVOKE)]
        expected_result = 4

        #Act
        result = text.TextDispatcherModule.process_update(mock_text, mock_update_message)

        #Assert
        self.assertEqual(len(result.ius), expected_result)

    def test_incrementalize_asr_module_name(self):
        #Arrange
        expected_result = "Incrementalize ASR Module"

        #Act
        result = text.IncrementalizeASRModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_incrementalize_asr_module_description(self):
        #Arrange
        expected_result = (
            "A module that takes SpeechRecognitionIUs and emits only the "
            + "increments from the previous iu"
        )

        #Act
        result = text.IncrementalizeASRModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_incrementalize_asr_module_input_ius(self):
        #Arrange
        expected_result = [text.SpeechRecognitionIU]

        #Act
        result = text.IncrementalizeASRModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_incrementalize_asr_module_output_iu(self):
        #Arrange
        expected_result = text.SpeechRecognitionIU

        #Act
        result = text.IncrementalizeASRModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_incrementalize_asr_module_init(self):
        #Arrange
        mock_threshold = 5.5
        #Act
        result = text.IncrementalizeASRModule(threshold=mock_threshold)

        #Assert
        self.assertEqual(result.threshold, mock_threshold)

    @patch('retico_core.core.abstract.UpdateMessage')
    def test_incrementalize_asr_module_process_update(self, mock_update):
        #Arrange
        mock_update.return_value = MockUpdateMessage()
        mock_text = MockText()
        mock_text.dispatch_final = True
        mock_text.committed = False
        mock_text.threshold = 9.0
        mock_text.current_input = []
        mock_update_message = [(mock_text,UpdateType.ADD), 
                               (mock_text, UpdateType.REVOKE)]
        expected_result = 3

        #Act
        result = text.IncrementalizeASRModule.process_update(mock_text, mock_update_message)

        #Assert
        self.assertEqual(len(result.ius), expected_result)

    def test_end_of_utterance_module_name(self):
        #Arrange
        expected_result = "End of Utterance Module"

        #Act
        result = text.EndOfUtteranceModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_end_of_utterance_module_description(self):
        #Arrange
        expected_result = "A module that forwards the end of utterance from the ASR output"

        #Act
        result = text.EndOfUtteranceModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_end_of_utterance_module_input_ius(self):
        #Arrange
        expected_result = [text.SpeechRecognitionIU]

        #Act
        result = text.EndOfUtteranceModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_end_of_utterance_module_output_iu(self):
        #Arrange
        expected_result = dialogue.EndOfTurnIU

        #Act
        result = text.EndOfUtteranceModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_end_of_utterance_module_init(self):
        #Arrange
        #Act
        #Assert
        try:
            text.EndOfUtteranceModule()
        except Exception as e:
            self.assertEqual("Failed", e)

    @patch('retico_core.core.abstract.UpdateMessage')
    def test_end_of_utterance_module_process_update(self, mock_update):
        #Arrange
        mock_update.return_value = MockUpdateMessage()
        mock_text = MockText()
        mock_update_message = [(mock_text,UpdateType.ADD), 
                               (mock_text, UpdateType.REVOKE),
                               (mock_text,UpdateType.ADD),
                               (mock_text,UpdateType.ADD)]
        expected_result = 5

        #Act
        result = text.EndOfUtteranceModule.process_update(mock_text, mock_update_message)

        #Assert
        self.assertEqual(len(result.ius), expected_result)


if __name__ == '__main__':
    unittest.main()