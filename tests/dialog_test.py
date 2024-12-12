import unittest
from retico_core.core import dialogue
from retico_core.core import UpdateType
from mock_classes import MockGrounded, MockDialog, MockTextFile
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
class TestDialogueModule(unittest.TestCase):

    def test_dialogue_act_iu_type(self):
        #Arrange
        expected_result = "Dialogue Act Incremental Unit"

        #Act
        result = dialogue.DialogueActIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    @patch('retico_core.core.abstract.IncrementalUnit._remove_old_links')
    def test_dialogue_act_iu_init(self, old_mock):
        #Arrange
        old_mock.return_value = True
        mock_creator="creator"
        mock_iuid="id"
        mock_previous_iu="prev"
        mock_grounded_in=MockGrounded()
        mock_payload="pay"
        mock_act="actor"
        mock_concepts="history"
        expected_confidence = 0.0

        #Act
        result = dialogue.DialogueActIU(creator=mock_creator,
                                        iuid=mock_iuid,
                                        previous_iu=mock_previous_iu,
                                        grounded_in=mock_grounded_in,
                                        payload=mock_payload,
                                        act=mock_act,
                                        concepts=mock_concepts)

        #Assert
        self.assertEqual(result.creator, mock_creator)
        self.assertEqual(result.iuid, mock_iuid)
        self.assertEqual(result.previous_iu, mock_previous_iu)
        self.assertEqual(result.grounded_in, mock_grounded_in)
        self.assertEqual(result.payload, mock_payload)
        self.assertEqual(result.act, mock_act)
        self.assertEqual(result.concepts, mock_concepts)
        self.assertEqual(result.confidence, expected_confidence)

    def test_dialogue_act_iu_set_act(self):
        #Arrange
        mock_dialogue_IU = MockDialog()
        mock_act = "act"
        mock_concepts = "concepts"
        mock_confidence = 5.6

        #Act
        dialogue.DialogueActIU.set_act(mock_dialogue_IU, 
                                       act=mock_act, 
                                       concepts=mock_concepts, 
                                       confidence=mock_confidence)

        #Assert
        self.assertEqual(mock_dialogue_IU.act, mock_act)
        self.assertEqual(mock_dialogue_IU.concepts, mock_concepts)
        self.assertEqual(mock_dialogue_IU.confidence, mock_confidence)
        self.assertEqual(mock_dialogue_IU.payload, (mock_act, mock_concepts))

    def test_dispatchable_act_init(self):
        #Arrange
        mock_dispatch = True

        #Act
        result = dialogue.DispatchableActIU(dispatch=mock_dispatch)

        #Assert
        self.assertEqual(result.dispatch, mock_dispatch)

    def test_end_of_turn_type(self):
        #Arrange
        expected_result = "End-of-Turn Incremental Unit"

        #Act
        result = dialogue.EndOfTurnIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_end_of_turn_init(self):
        #Arrange
        mock_iuid="id"
        expected_probability = 0.0
        expected_is_speaking = False

        #Act
        result = dialogue.EndOfTurnIU(iuid=mock_iuid)

        #Assert
        self.assertEqual(result.probability, expected_probability)
        self.assertEqual(result.is_speaking, expected_is_speaking)

    def test_end_of_turn_set_eot(self):
        #Arrange
        mock_dialogue_IU = MockDialog()
        mock_probability=18.58
        mock_is_speaking=True

        #Act
        dialogue.EndOfTurnIU.set_eot(mock_dialogue_IU, 
                                              probability=mock_probability, 
                                              is_speaking=mock_is_speaking)

        #Assert
        self.assertEqual(mock_dialogue_IU.probability, mock_probability)
        self.assertEqual(mock_dialogue_IU.is_speaking, mock_is_speaking)

    def test_dialogue_act_recorder_module_name(self):
        #Arrange
        expected_result = "Dialogue Act Recorder Module"

        #Act
        result = dialogue.DialogueActRecorderModule.name()

        #Assert
        self.assertEqual(result, expected_result)
    
    def test_dialogue_act_recorder_module_description(self):
        #Arrange
        expected_result = "A module that writes dialogue acts into a file."

        #Act
        result = dialogue.DialogueActRecorderModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_dialogue_act_recorder_module_input_ius(self):
        #Arrange
        expected_result = [dialogue.DialogueActIU, dialogue.DispatchableActIU]

        #Act
        result = dialogue.DialogueActRecorderModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_dialogue_act_recorder_module_init(self):
        #Arrange
        mock_iuid="id"
        mock_filename = "mock_file"
        mock_separator="\n"
        expected_txt_file = None

        #Act
        result = dialogue.DialogueActRecorderModule(filename=mock_filename, 
                                                    separator=mock_separator, 
                                                    iuid=mock_iuid)

        #Assert
        self.assertEqual(result.filename, mock_filename)
        self.assertEqual(result.separator, mock_separator)
        self.assertEqual(result.txt_file, expected_txt_file)

    @patch('time.time')
    def test_dialogue_act_recorder_module_prepare_run(self, mock_time):
        #Arrange
        mock_time.return_value = 50
        mock_dialog = MockDialog()
        
        #Act
        dialogue.DialogueActRecorderModule.prepare_run(mock_dialog)

        #Assert
        self.assertEqual(mock_dialog.start_time, 50)

    def test_dialogue_act_recorder_module_shutdown(self):
        #Arrange
        mock_dialog = MockDialog()
        mock_dialog.txt_file = MockTextFile()
        mock_dialog.separator = "\n"
        mock_dialog.start_time = 10
        mock_dialog.created_at = 5
        mock_update_message = [(mock_dialog,UpdateType.ADD), (mock_dialog, UpdateType.REVOKE)]
        expected_result = 10
        
        #Act
        dialogue.DialogueActRecorderModule.process_update(mock_dialog, mock_update_message)

        #Assert
        self.assertEqual(mock_dialog.txt_file.writes, expected_result)

    def test_dialogue_act_trigger_module_name(self):
        #Arrange
        expected_result = "Dialogue Act Trigger Module"

        #Act
        result = dialogue.DialogueActTriggerModule.name()

        #Assert
        self.assertEqual(result, expected_result)
    
    def test_dialogue_act_trigger_module_description(self):
        #Arrange
        expected_result = "A trigger module that emits a dialogue act when triggered."

        #Act
        result = dialogue.DialogueActTriggerModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_dialogue_act_trigger_module_output_iu(self):
        #Arrange
        expected_result = dialogue.DispatchableActIU

        #Act
        result = dialogue.DialogueActTriggerModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_dialogue_act_trigger_module_output_init(self):
        #Arrange
        mock_iuid = "id"
        expected_result = True

        #Act
        result = dialogue.DialogueActTriggerModule(iuid=mock_iuid)

        #Assert
        self.assertEqual(result.dispatch, expected_result)

    @patch('retico_core.core.UpdateMessage.from_iu')
    def test_dialogue_act_trigger_module_output_trigger(self, mock_iu):
        #Arrange
        mock_iu.return_value = 5
        mock_dialog = MockDialog()
        mock_dialog.dispatch = "dispatched"
        expected_result = [5]

        #Act
        dialogue.DialogueActTriggerModule.trigger(mock_dialog)

        #Assert
        self.assertEqual(mock_dialog.dialogue, expected_result)

        

if __name__ == '__main__':
    unittest.main()