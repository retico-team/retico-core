import unittest
from retico_core.core import abstract
from mock_classes import MockAbstract
from mock_classes import MockGrounded
from mock_classes import MockIncrementalUnit
from mock_classes import MockUpdateMessage
from mock_classes import MockBuffer
from mock import patch

'''
test format:
def test_X(self):
    #Arrange

        #Act

        #Assert
'''

# Test cases
class TestAbstractModule(unittest.TestCase):

    def test_iq_init(self):
        #Arrange
        mock_provider = "Provider"
        mock_consumer = "Consumer"

        #Act
        iq = abstract.IncrementalQueue(provider=mock_provider, consumer=mock_consumer)

        #Assert
        self.assertEqual(iq.provider, mock_provider)
        self.assertEqual(iq.consumer, mock_consumer)
    
    @patch('retico_core.core.abstract.IncrementalUnit._remove_old_links')
    def test_iu_init(self, old_mock):
        #Arrange
        old_mock.return_value = True
        mock_creator="test_creator"
        mock_iuid="test_iuid"
        mock_previous_iu="test_previous"
        mock_grounded_in=MockGrounded()
        mock_payload="test_payload"

        #Act
        iu = abstract.IncrementalUnit(creator=mock_creator,
        iuid=mock_iuid,
        previous_iu=mock_previous_iu,
        grounded_in=mock_grounded_in,
        payload=mock_payload)

        #Assert
        self.assertEqual(iu.iuid,mock_iuid)
        self.assertEqual(iu.creator,mock_creator)
        self.assertEqual(iu.previous_iu,mock_previous_iu)
        self.assertEqual(iu.grounded_in,mock_grounded_in)
        self.assertEqual(iu.payload,mock_payload)


    def test_iu_remove_old_links(self):
        #Arrange
        mock_IU = MockIncrementalUnit()

        #Act
        abstract.IncrementalUnit._remove_old_links(mock_IU)

        #Assert
        self.assertEqual(mock_IU.grounded_in.grounded_in, None)
        self.assertEqual(mock_IU.previous_iu.previous_iu, None)

    @patch('time.time')
    def test_iu_age(self, mock_time):
        #Arrange
        mock_time.return_value = 50
        mock_IU = MockIncrementalUnit()

        #Act
        result = abstract.IncrementalUnit.age(mock_IU)

        #Assert
        self.assertEqual(result, mock_time.return_value - mock_IU.created_at)
    
    @patch('retico_core.core.abstract.IncrementalUnit._remove_old_links')
    @patch('retico_core.core.abstract.IncrementalUnit.age')
    def test_iu_older_than(self, mock_age, mock_old):
        #Arrange
        mock_age.return_value = 4
        mock_old.return_value = True
        mock_creator="test_creator"
        mock_iuid="test_iuid"
        mock_previous_iu="test_previous"
        mock_grounded_in=MockGrounded()
        mock_payload="test_payload"
        mock_IU = abstract.IncrementalUnit(reator=mock_creator,
            iuid=mock_iuid,
            previous_iu=mock_previous_iu,
            grounded_in=mock_grounded_in,
            payload=mock_payload,)

        #Act
        result_false = mock_IU.older_than(5)
        result_true = mock_IU.older_than(3)

        #Assert
        self.assertEqual(result_false, False)
        self.assertEqual(result_true, True)
    
    def test_iu_processed_list(self):
        #Arrange
        mock_IU = MockIncrementalUnit()

        #Act
        result = abstract.IncrementalUnit.processed_list(mock_IU)

        #Assert
        self.assertEqual(result, list(mock_IU._processed_list))

    def test_iu_set_processed_fail(self):
        #Arrange
        mock_IU = MockIncrementalUnit()

        #Act
        #Assert
        self.assertRaises(TypeError, abstract.IncrementalUnit.set_processed, mock_IU, 5)
    
    def test_iu_set_processed_pass(self):
        #Arrange
        mock_IU = MockIncrementalUnit()
        mock_abstract = MockAbstract()
        expected = mock_IU._processed_list
        expected.append(mock_abstract)

        #Act
        abstract.IncrementalUnit.set_processed(mock_IU, mock_abstract)

        #Assert
        self.assertEqual(mock_IU._processed_list, expected)

    def test_iu_is_processed_by(self):
        #Arrange
        mock_IU = MockIncrementalUnit()

        #Act
        result_false = abstract.IncrementalUnit.is_processed_by(mock_IU, 41)
        result_true= abstract.IncrementalUnit.is_processed_by(mock_IU, 4)

        #Assert
        self.assertEqual(result_false, False)
        self.assertEqual(result_true, True)
    
    def test_iu__repr__(self):
        #Arrange
        mock_IU = MockIncrementalUnit()
        expected = "%s - (%s): %s" % (
            mock_IU.type(),
            mock_IU.creator.name(),
            str(mock_IU.payload)[0:10],
        )

        #Act
        result = abstract.IncrementalUnit.__repr__(mock_IU)

        #Assert
        self.assertEqual(result, expected)

    def test_iu_type_fail(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.IncrementalUnit.type)

    def test_update_init(self):
        #Arrange
        expected_msgs = []
        expected_counter = -1
        #Act
        result = abstract.UpdateMessage()

        #Assert
        self.assertEqual(result._msgs, expected_msgs)
        self.assertEqual(result._counter, expected_counter)

    def test_update_len(self):
        #Arrange
        mock_update = MockUpdateMessage()

        #Act
        result = abstract.UpdateMessage.__len__(mock_update)

        #Assert
        self.assertEqual(result, len(mock_update._msgs))

    @patch('retico_core.core.abstract.UpdateMessage.add_iu')
    def test_update_from_iu(self, mock_add):
        #Arrange
        mock_IU = MockIncrementalUnit()
        mock_add.return_value = True
        expected_msgs = []
        expected_counter = -1

        #Act
        result = abstract.UpdateMessage.from_iu(mock_IU, "mock_type")

        #Assert
        self.assertEqual(result._msgs, expected_msgs)
        self.assertEqual(result._counter, expected_counter)

    @patch('retico_core.core.abstract.UpdateMessage.add_ius')
    def test_update_from_iu_list(self, mock_add):
        #Arrange
        mock_IU = MockIncrementalUnit()
        mock_add.return_value = True
        expected_msgs = []
        expected_counter = -1

        #Act
        result = abstract.UpdateMessage.from_iu_list(mock_IU, "mock_type")

        #Assert
        self.assertEqual(result._msgs, expected_msgs)
        self.assertEqual(result._counter, expected_counter)

    def test_update_iter_(self):
        #Arrange
        mock_update = MockUpdateMessage()

        #Act
        result = abstract.UpdateMessage.__iter__(mock_update)

        #Assert
        self.assertEqual(result, mock_update)

    def test_update_next_raise_error(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_update._counter = 1
        mock_update._msgs = [1, 2]

        #Act
        #Assert
        self.assertRaises(StopIteration, abstract.UpdateMessage.__next__, mock_update)
    
    def test_update_next_success(self):
        #Arrange
        mock_update = MockUpdateMessage()
        expected_result = mock_update._msgs[(mock_update._counter + 1)]

        #Act
        result = abstract.UpdateMessage.__next__(mock_update)

        #Assert
        self.assertEqual(result, expected_result)

    def test_update_add_iu_fail(self):
        #Arrange
        mock_update = MockUpdateMessage()

        #Act
        #Assert
        self.assertRaises(TypeError, abstract.UpdateMessage.add_iu, mock_update, 1, 2)
    
    def test_update_add_iu_strict(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_IU = MockIncrementalUnit()
        expected_result = [1,2,3,4]
        expected_result.append((mock_IU, abstract.UpdateType("add")))

        #Act
        abstract.UpdateMessage.add_iu(mock_update, mock_IU, "add")

        #Assert
        self.assertEqual(mock_update._msgs, expected_result)
    
    def test_update_add_iu_not_strict(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_IU = MockIncrementalUnit()
        expected_result = [1,2,3,4, (mock_IU, "add")]

        #Act
        abstract.UpdateMessage.add_iu(mock_update, mock_IU, "add", False)

        #Assert
        self.assertEqual(mock_update._msgs, expected_result)

    def test_update_add_ius_fail(self):
        #Arrange
        mock_update = MockUpdateMessage()

        #Act
        #Assert
        self.assertRaises(TypeError, abstract.UpdateMessage.add_ius, mock_update, [(1, 2)], 2)

    def test_update_add_ius_pass_strict(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_IU = MockIncrementalUnit()
        expected_result = [1,2,3,4]
        expected_result.append((mock_IU, abstract.UpdateType("add")))
        expected_result.append((mock_IU, abstract.UpdateType("revoke")))
        mock_ius = [("add", mock_IU), ("revoke", mock_IU)]

        #Act
        abstract.UpdateMessage.add_ius(mock_update, mock_ius)

        #Assert
        self.assertEqual(mock_update._msgs, expected_result)

    def test_update_add_ius_pass_not_strict(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_IU = MockIncrementalUnit()
        expected_result = [1,2,3,4]
        expected_result.append((mock_IU, "add"))
        expected_result.append((mock_IU, "revoke"))
        mock_ius = [("add", mock_IU), ("revoke", mock_IU)]

        #Act
        abstract.UpdateMessage.add_ius(mock_update, mock_ius, False)

        #Assert
        self.assertEqual(mock_update._msgs, expected_result)

    def test_update_has_valid_ius_empty(self):
        #Arrange
        mock_update = MockUpdateMessage()
        expected_result = False

        #Act
        result = abstract.UpdateMessage.has_valid_ius(mock_update, None)

        #Assert
        self.assertEqual(result, expected_result)

    def test_update_has_valid_ius_fail(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_classes = float
        expected_result = False

        #Act
        result = abstract.UpdateMessage.has_valid_ius(mock_update, mock_classes)

        #Assert
        self.assertEqual(result, expected_result)

    def test_update_has_valid_ius_pass(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_classes = [int, str]
        expected_result = True

        #Act
        result = abstract.UpdateMessage.has_valid_ius(mock_update, mock_classes)

        #Assert
        self.assertEqual(result, expected_result)

    def test_update_update_types(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_update._msgs = [("IU1", "update1"), ("IU2", "update2")]
        expected_result = ["update1", "update2"]

        #Act
        result = abstract.UpdateMessage.update_types(mock_update)

        #Assert
        for x in result:
            self.assertTrue(x in expected_result)

    def test_update_incremental_units(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_update._msgs = [("IU1", "update1"), ("IU2", "update2")]
        expected_result = ["IU1", "IU2"]

        #Act
        result = abstract.UpdateMessage.incremental_units(mock_update)

        #Assert
        for x in result:
            self.assertTrue(x in expected_result)

    def test_update_set_processed(self):
        #Arrange
        mock_update = MockUpdateMessage()
        mock_IU_1 = MockIncrementalUnit()
        mock_IU_1._processed_list = ["test", "Strings"]
        mock_IU_2 = MockIncrementalUnit()
        mock_update.ius = [mock_IU_1, mock_IU_2]
        expected_results = []
        expected_results.append(mock_IU_1._processed_list)
        expected_results.append(mock_IU_2._processed_list)

        #Act
        abstract.UpdateMessage.set_processed(mock_update, 20)

        #Assert
        for x in range(0, len(mock_update.ius)):
            self.assertEqual(mock_update.ius[x]._processed_list, expected_results[x])

    def test_abstract_name(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractModule.name)

    def test_description(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractModule.description)

    def test_abstract_input_ius(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractModule.input_ius)
    
    def test_abstract_output_iu(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractModule.output_iu)

    def test_abstract_get_init_arguments(self):
        #Arrange
        mock_abstract = MockAbstract()

        #Act
        result = abstract.AbstractModule.get_init_arguments(mock_abstract)

        #Assert
        self.assertEqual(result, mock_abstract.__dict__)

    def test_abstract_init(self):
        #Arrange
        mock_meta = {"test": "meta"}
        expected_lists = []
        expected_running = False
        expected_prev = None
        expected_events = {}
        expected_metadata = mock_meta
        expected_class = abstract.IncrementalQueue
        expected_counter = 0


        #Act
        test_abstract = abstract.AbstractModule(meta_data=mock_meta)

        #Assert
        self.assertEqual(test_abstract._right_buffers, expected_lists)
        self.assertEqual(test_abstract._is_running, expected_running)
        self.assertEqual(test_abstract._previous_iu, expected_prev)
        self.assertEqual(test_abstract._left_buffers, expected_lists)
        self.assertEqual(test_abstract.events, expected_events)
        self.assertEqual(test_abstract.current_input, expected_lists)
        self.assertEqual(test_abstract.current_output, expected_lists)
        self.assertEqual(test_abstract.meta_data, expected_metadata)
        self.assertEqual(test_abstract.queue_class, expected_class)
        self.assertEqual(test_abstract.iu_counter, expected_counter)


    def test_abstract_revoke(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_IU_1 = MockIncrementalUnit()
        mock_IU_1.payload = 1
        mock_IU_2 = MockIncrementalUnit()
        mock_IU_2.payload = 2
        mock_IU_3 = MockIncrementalUnit()
        mock_IU_3.payload = 3
        mock_IU_4 = MockIncrementalUnit()
        mock_IU_4.payload = 4
        mock_abstract.current_input = [mock_IU_1, mock_IU_2, mock_IU_3, mock_IU_4]
        mock_abstract.current_output = [mock_IU_1, mock_IU_2, mock_IU_3, mock_IU_4]

        #Act
        abstract.AbstractModule.revoke(mock_abstract, mock_IU_1)

        #Assert
        self.assertEqual(mock_abstract.current_input, [mock_IU_2, mock_IU_3, mock_IU_4])
        self.assertEqual(mock_abstract.current_output, [mock_IU_2, mock_IU_3, mock_IU_4])
        
    def test_abstract_input_committed_false(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_IU_1 = MockIncrementalUnit()
        mock_IU_1.committed = True
        mock_IU_2 = MockIncrementalUnit()
        mock_IU_2.committed = False
        mock_abstract.current_input = [mock_IU_1, mock_IU_2]

        #Act
        result = abstract.AbstractModule.input_committed(mock_abstract)

        #Assert
        self.assertEqual(result, False)

    def test_abstract_input_committed_true(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_IU_1 = MockIncrementalUnit()
        mock_IU_1.committed = True
        mock_IU_2 = MockIncrementalUnit()
        mock_IU_2.committed = True
        mock_abstract.current_input = [mock_IU_1, mock_IU_2]

        #Act
        result = abstract.AbstractModule.input_committed(mock_abstract)

        #Assert
        self.assertEqual(result, True)

    def test_abstract_remove(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_abstract._is_running = True
        mock_abstract.lbs = [MockBuffer(), MockBuffer(), MockBuffer()]
        mock_abstract.rbs = [MockBuffer(), MockBuffer(), MockBuffer(), MockBuffer()]

        #Act
        abstract.AbstractModule.remove(mock_abstract)

        #Assert
        for lb in mock_abstract.left_buffers():
            self.assertEqual(lb.buffer_present, False)
        for rb in mock_abstract.right_buffers():
            self.assertEqual(rb.buffer_present, False)

    def test_abstract_process_update(self):
        #Arrange
        mock_abstract = MockAbstract()
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractModule.process_update, mock_abstract, "test")


    def test_is_valid_input_iu_fail(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_IU = "IU"

        #Act
        #Assert
        self.assertRaises(TypeError, abstract.AbstractModule.is_valid_input_iu, mock_abstract, mock_IU)

    def test_is_valid_input_iu_false(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_IU = MockIncrementalUnit()
        mock_abstract.ius = [str]

        #Act
        result = abstract.AbstractModule.is_valid_input_iu(mock_abstract, mock_IU)

        #Assert
        self.assertEqual(result, False)

    def test_abstract_is_valid_input_iu_true(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_IU = MockIncrementalUnit()
        mock_abstract.ius = [abstract.IncrementalUnit]

        #Act
        result = abstract.AbstractModule.is_valid_input_iu(mock_abstract, mock_IU)

        #Assert
        self.assertEqual(result, True)

    def test_abstract_setup(self):
        #Arrange
        mock_abstract = MockAbstract()

        #Act
        result = abstract.AbstractModule.setup(mock_abstract)

        #Assert
        self.assertEqual(result, None)
    
    def test_abstract_prepare_run(self):
        #Arrange
        mock_abstract = MockAbstract()

        #Act
        result = abstract.AbstractModule.prepare_run(mock_abstract)

        #Assert
        self.assertEqual(result, None)

    def test_abstract_shutdown(self):
        #Arrange
        mock_abstract = MockAbstract()

        #Act
        result = abstract.AbstractModule.shutdown(mock_abstract)

        #Assert
        self.assertEqual(result, None)

    def test_abstract_stop(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_abstract.EVENT_STOP = "test_abstract_stop"
        mock_abstract.rbs = [MockBuffer(), MockBuffer()]

        #Act
        abstract.AbstractModule.stop(mock_abstract)

        #Assert
        self.assertEqual(mock_abstract.called, mock_abstract.EVENT_STOP)

    def test_abstract_create_iu(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_abstract.iu_counter = 1
        mock_abstract._previous_iu = "prev"
        expected_iuid = f"{hash(mock_abstract)}:{mock_abstract.iu_counter}"
        expected_creator = mock_abstract
        expected_prev = mock_abstract._previous_iu
        expected_grounded_in = None

        #Act
        result = abstract.AbstractModule.create_iu(mock_abstract)

        #Assert
        self.assertEqual(result.creator, expected_creator)
        self.assertEqual(result.iuid, expected_iuid)
        self.assertEqual(result.previous_iu, expected_prev)
        self.assertEqual(result.grounded_in, expected_grounded_in)
    
    def test_abstract_latest_iu(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_abstract._previous_iu = "prev"

        #Act
        result = abstract.AbstractModule.latest_iu(mock_abstract)

        #Assert
        self.assertEqual(result, mock_abstract._previous_iu)

    def test_abstract_repr(self):
        #Arrange
        mock_abstract = MockAbstract()

        #Act
        result = abstract.AbstractModule.__repr__(mock_abstract)

        #Assert
        self.assertEqual(result, mock_abstract.name())

    def test_abstract_event_subscribe(self):
        #Arrange
        mock_abstract = MockAbstract()
        mock_abstract.events = {"test_event": 1}
        expected_result = {"test_event": 1, "runtime": ["success"]}

        #Act
        abstract.AbstractModule.event_subscribe(mock_abstract, "runtime", "success")

        #Assert
        self.assertEqual(mock_abstract.events, expected_result)

    def test_abstract_consuming_module_name(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractConsumingModule.name)
    
    def test_abstract_consuming_module_description(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractConsumingModule.description)
    
    def test_abstract_consuming_module_output_iu(self):
        #Arrange
        expected_result = None

        #Act
        result = abstract.AbstractConsumingModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_abstract_consuming_module_input_ius(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractConsumingModule.input_ius)

    def test_abstract_consuming_module_subscribe(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(ValueError, abstract.AbstractConsumingModule.subscribe, 1, 2)

    def test_abstract_consuming__module_process_update(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractConsumingModule.process_update, 1, 2)
    
    def test_abstract_trigger_module_name(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractTriggerModule.name)
    
    def test_abstract_trigger_module_description(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractTriggerModule.description)
    
    def test_abstract_trigger_module_input_ius(self):
        #Arrange
        expected_result = []

        #Act
        result = abstract.AbstractTriggerModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_abstract_trigger_module_output_iu(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractTriggerModule.output_iu)

    def test_abstract_trigger_module_process_update(self):
        #Arrange
        expected_result = None
        mock_abstract = MockAbstract()

        #Act
        result = abstract.AbstractTriggerModule.process_update(mock_abstract, "test")

        #Assert
        self.assertEqual(result, expected_result)

    def test_abstract_trigger_module_output_trigger(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractTriggerModule.trigger, 1, 2)
    
    def test_abstract_producing_module_name(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractProducingModule.name)

    def test_abstract_producing_module_description(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractProducingModule.description)

    def test_abstract_producing_module_input_ius(self):
        #Arrange
        expected_result = []

        #Act
        result = abstract.AbstractProducingModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_abstract_producing_module_output_iu(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractProducingModule.output_iu)

    def test_abstract_producing_module_process_update(self):
        #Arrange
        #Act
        #Assert
        self.assertRaises(NotImplementedError, abstract.AbstractProducingModule.process_update, 1, 2)


if __name__ == '__main__':
    unittest.main()