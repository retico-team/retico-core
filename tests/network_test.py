import unittest
from retico_core import network
from retico_core import UpdateType
from mock_classes import MockNetwork, MockBuffer
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
class TestNetworkModule(unittest.TestCase):

    @patch('pickle.load')
    @patch('builtins.open')
    def test_network_load(self, mock_open, mock_pickle):
        #Arrange
        mock_open.return_value = True
        mock_pickle.return_value = [[{'retico_class': MockNetwork.open_network, 
                                      'args': {'arg1': 'one'}, 
                                      'id': 'test_iba'},
                                      {'retico_class': MockNetwork.open_network, 
                                      'args': {'arg1': 'one'}, 
                                      'id': 'test_ibd'}],
                                      [("test_ibd", "test_iba")]
                                    ]
        expected_result = 2

        #Act
        result = network.load("test")

        #Assert
        self.assertEqual(len(result), expected_result)

    @patch('retico_core.network.load')
    @patch('builtins.input')
    def test_network_load_and_execute(self, mock_input, mock_load):
        #Arrange
        mock_network = MockNetwork()
        mock_input.return_value = True
        mock_load.return_value = ([mock_network], "testing")
        expected_result = True

        #Act
        network.load_and_execute("test")

        #Assert
        self.assertEqual(mock_network.ran, expected_result)
        self.assertEqual(mock_network.set, expected_result)
        self.assertEqual(mock_network.stopped, expected_result)

    def test_network_discover_modules(self):
        #Arrange
        mock_network = MockNetwork()
        expected_result = ({'mock_provide'}, {'mock_consume'})

        #Act
        result = network._discover_modules(mock_network)

        #Assert
        self.assertEqual(result, expected_result)

    @patch('retico_core.network.discover')
    def test_network_run(self,mock_discover):
        #Arrange
        mock_network = MockNetwork()
        mock_discover.return_value = ([mock_network], "testing")
        expected_result = True

        #Act
        network.run("test")

        #Assert
        self.assertEqual(mock_network.ran, expected_result)
        self.assertEqual(mock_network.set, expected_result)

    @patch('retico_core.network.discover')
    def test_network_stop(self,mock_discover):
        #Arrange
        mock_network = MockNetwork()
        mock_discover.return_value = ([mock_network], "testing")
        expected_result = True

        #Act
        network.stop("test")

        #Assert
        self.assertEqual(mock_network.stopped, expected_result)

    @patch('retico_core.network._discover_modules')
    def test_network_discover(self, mock_load):
        #Arrange
        mock_network = MockNetwork()
        mock_load.return_value = ([MockBuffer()], [MockBuffer()])
        expected_result1 = 3
        expected_result2 = [('mock_consume', 'mock_provide'), ('mock_consume', 'mock_provide')]

        #Act
        result1, result2 = network.discover(mock_network)

        #Assert
        self.assertEqual(len(result1), expected_result1)
        self.assertEqual(result2, expected_result2)

    @patch('pickle.dump')
    @patch('retico_core.network._discover_modules')
    def test_network_save(self, mock_load, mock_pickle):
        #Arrange
        mock_network = MockNetwork()
        mock_pickle.return_value = True
        mock_load.return_value = ([MockBuffer()], [MockBuffer()])

        #Act
        #Assert
        try:
            network.save(mock_network, "test")
        except Exception as e:
            self.assertEqual("Failed", e)

        

if __name__ == '__main__':
    unittest.main()