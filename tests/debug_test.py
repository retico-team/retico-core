import unittest
from retico_core import abstract, text, debug
from retico_core import UpdateType
from mock_classes import MockDebug
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
class TestDebugModule(unittest.TestCase):

    def test_debug_module_name(self):
        #Arrange
        expected_result = "Debug Module"

        #Act
        result = debug.DebugModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_debug_module_description(self):
        #Arrange
        expected_result = "A consuming module that displays IU infos in the console."

        #Act
        result = debug.DebugModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_debug_module_input_ius(self):
        #Arrange
        expected_result = [abstract.IncrementalUnit]

        #Act
        result = debug.DebugModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_debug_module_init(self):
        #Arrange
        mock_print = True

        #Act
        result = debug.DebugModule(print_payload_only=mock_print)

        #Assert
        self.assertEqual(result.print_payload_only, mock_print)

    def test_debug_module_process_update_payload(self):
        #Arrange
        capturedOutput = io.StringIO() 
        sys.stdout = capturedOutput 
        mock_debug = MockDebug()
        mock_debug.print_payload_only = True
        mock_update = [(mock_debug,UpdateType.ADD), (mock_debug, UpdateType.REVOKE), (mock_debug, UpdateType.COMMIT)]
        expected_len = 63

        #Act
        debug.DebugModule.process_update(mock_debug, mock_update)
        sys.stdout = sys.__stdout__ 

        #Assert
        self.assertEqual(len(capturedOutput.getvalue()), expected_len)

    def test_debug_module_process_update_all(self):
        #Arrange
        capturedOutput = io.StringIO() 
        sys.stdout = capturedOutput 
        mock_debug = MockDebug()
        mock_debug.print_payload_only = False
        mock_update = [(mock_debug,UpdateType.ADD), (mock_debug, UpdateType.REVOKE), (mock_debug, UpdateType.COMMIT)]
        expected_len = 452

        #Act
        debug.DebugModule.process_update(mock_debug, mock_update)
        sys.stdout = sys.__stdout__ 

        #Assert
        self.assertEqual(len(capturedOutput.getvalue()), expected_len)

    def test_callback_module_name(self):
        #Arrange
        expected_result = "Callback Debug Module"

        #Act
        result = debug.CallbackModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_callback_module_description(self):
        #Arrange
        expected_result = (
            "A consuming module that calls a callback function whenever an"
            "update message arrives."
        )

        #Act
        result = debug.CallbackModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_callback_module_input_ius(self):
        #Arrange
        expected_result = [abstract.IncrementalUnit]

        #Act
        result = debug.CallbackModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_callback_module_init(self):
        #Arrange
        mock_callback = "calling"

        #Act
        result = debug.CallbackModule(callback=mock_callback)

        #Assert
        self.assertEqual(result.callback, mock_callback)

    def test_callback_module_process_update(self):
        #Arrange
        mock_debug = MockDebug()
        expected_result = True

        #Act
        debug.CallbackModule.process_update(mock_debug, 1)

        #Assert
        self.assertEqual(mock_debug.called, expected_result)

    def test_text_printer_module_name(self):
        #Arrange
        expected_result = "Text Printer Module"

        #Act
        result = debug.TextPrinterModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_printer_module_description(self):
        #Arrange
        expected_result = "A module that prints out and updates text."

        #Act
        result = debug.TextPrinterModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_printer_module_input_ius(self):
        #Arrange
        expected_result = [text.TextIU]

        #Act
        result = debug.TextPrinterModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_text_printer_module_init(self):
        #Arrange
        expected_result = ""

        #Act
        result = debug.TextPrinterModule()

        #Assert
        self.assertEqual(result._old_text, expected_result)

    def test_text_printer_module_process_update(self):
        #Arrange
        mock_debug = MockDebug()
        mock_debug.text = "test_text"
        mock_debug._old_text = "old"
        mock_debug.current_input = [mock_debug]
        mock_update = [(mock_debug,UpdateType.ADD), 
                       (mock_debug, UpdateType.REVOKE),
                        (mock_debug, UpdateType.COMMIT),
                        (mock_debug,UpdateType.ADD)]
        expected_result = "test_text test_text test_text"

        #Act
        debug.TextPrinterModule.process_update(mock_debug, mock_update)

        #Assert
        self.assertEqual(mock_debug._old_text, expected_result)
        


        
        

if __name__ == '__main__':
    unittest.main()