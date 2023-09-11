from retico_core import abstract, text
import queue

class MockGrounded:
    def __init__(self):
        self.meta_data = {"test": "metadata"}
        self.grounded_in = "ground_mock"
        self.creator = "creator"

class MockAudioBuffer:
    def __init__(self):
        self.buf = []
    def put(self, in_data):
        self.buf.append(in_data)
        self.in_data = in_data
    def get(self, timeout):
        if self.fail == True:
            raise queue.Empty
        else:
            return True

class MockUpdateMessage:
    def __init__(self, valid_ius=True):
        self._msgs = [1,2,3,4]
        self._counter = -1
        self.ius = [1, "revoke"]
        self.valid_ius = valid_ius
    def incremental_units(self):
        return self.ius
    def has_valid_ius(self, ius):
        return self.valid_ius
    def set_processed(self, iu):
        return True
    def process_update(self, iu):
        return self.output_message
    def add_iu(self, iu, ut):
        self.ius.append((iu, ut))
    
class MockTextFile(abstract.IncrementalUnit):
    def __init__(self):
        self.writes = 0
        self.text = "testing"
        self.revoked = False
    def close(self):
        self.closed = True
    def write(self, *kwargs):
        self.writes += 1
    def open(self, *kwargs):
        self.opened = True

class MockText(text.SpeechRecognitionIU):
    def __init__(self):
        self.text = "testing"
        self.current_output = [MockTextFile(), MockTextFile()]
        self.payload = "payload_test"
        self.filename = "file"
        self.grounded_in = MockGrounded()
        self.separator = "\n"
        self.created_at = "now"
        self.predictions = "pred"
        self.stability = 10.0
        self.confidence = "total"
        self.final = "fin"
        self.dispatch = False
        self.messages = []
        self.creator = MockNetwork()
    def create_iu(self, *kwargs):
        return MockText()
    def append(self, message):
        self.messages.append(message)
    def get_text(self):
        return self.text
    def set_eot(self, *kwargs):
        return True

class MockTextGen(text.GeneratedTextIU):
    def __init__(self):
        self.text = "testing"
        self.current_output = [MockTextFile(), MockTextFile()]
        self.payload = "payload_test"
        self.filename = "file"
        self.grounded_in = MockGrounded()
        self.created_at = "now"
        self.predictions = "pred"
        self.stability = "stable"
        self.confidence = "total"
        self.final = "fin"
        self.dispatch = "dispatched"
      
class MockStream:
    def __init__(self):
        self.raw = []
    def start_stream(self):
        self.started = True
        return True
    def stop_stream(self):
        self.stopped = True
        return True
    def close(self):
        self.closed = True
        return True
    def write(self, raw):
        self.raw.append(raw)
        return True
    
class MockWav:
    def writeframes(self, *kwargs):
        self.write_state = True
        return True
    def setframerate(self, *kwargs):
        self.framed = True
        return True
    def setnchannels(self, *kwargs):
        self.chaneled = True
        return True
    def setsampwidth(self, *kwargs):
        self.wide = True
        return True
    def close(self):
        self.closed = True
        return True

class MockAudioIU:
    def __init__(self):
        self.raw_audio = "sound_file"
        self.opened = False
        self.sample_width = 10
        self.rate = 3
        self.device_index = 5
        self.callback = "callback"
        self.chunk_size = 50
    def create_iu(self, *kwargs):
        return MockAudioIU()
    def set_audio(self, *kwargs):
        self.set_audio_value = True
        return True
    def open(self, **kwargs):
        self.opened = True
        return "opened!"
    def get_format_from_width(self, *kwargs):
        return "formatted!"
    def set_dispatching(self, *kwargs):
        return True
    
class MockNetwork:
    def __init__(self):
        self.args = "arg"
        self.meta_data = "meta_data"
    def subscribe(self, *kwargs):
        return True
    def open_network(**kwargs):
        return MockNetwork()
    def setup(self, *kwargs):
        self.set = True
        return True
    def run(self, **kwargs):
        self.ran = True
        return True
    def stop(self, *kwargs):
        self.stopped = True
        return True
    def left_buffers(self):
        return [MockBuffer(), MockBuffer()]
    def right_buffers(self):
        return [MockBuffer(), MockBuffer()]
    def name(self):
        return "mock_network"
    def get_init_arguments(self):
        return self.args
    
class MockDialog:
    def __init__(self):
        self.creator="creator"
        self.iuid="id"
        self.previous_iu="prev"
        self.grounded_in=MockGrounded()
        self.payload="pay"
        self.act="actor"
        self.concepts={"history": "1776"}
        self.confidence = 0.0
        self.dialogue = []
    def create_iu(self, *kwargs):
        return MockDialog()
    def append(self, message):
        self.dialogue.append(message)
    def set_act(self, *kwargs):
        self.acted = True
        return True
    
class MockDebug:
    def __init__(self):
        self.payload = "pay"
        self.previous_iu = "prev"
        self.grounded_in = "ground"
        self.commited_input = True
    def age(self):
        return 5
    def callback(self, *kwargs):
        self.called = True
        return True
    def revoke(self, *kwargs):
        self.revoked = True
        return True
    def commit(self, *kwargs):
        self.commited = True
        return True
    def input_committed(self):
        return self.commited_input

class MockAbstract(abstract.AbstractModule):
    def __init__(self):
        self.__dict__ = {"String": "test", "Float": 1.4, "Int": 5, "Bool": True, "Dict": {"test": "dict"}}
    def name(self):
        return "mock_abstract"
    def left_buffers(self):
        return self.lbs
    def right_buffers(self):
        return self.rbs
    def stop(self):
        return True
    def input_ius(self):
        return self.ius
    def prepare_run(self):
        return True
    def event_call(self, call):
        self.called = call
        return True
    def output_iu(self, *kwargs):
        return MockIncrementalUnit
    def shutdown(self):
        return True
    def setup(self):
        return True
    def name(self):
        return "mock_name"
    
class MockPreviousIU:
    def __init__(self):
        self.previous_iu = "prev"

class MockMutex:
    def __enter__(self):
        return True
    def __exit__(self, *kwargs):
        return True
    def __repr__(self):
        return "test"
    
class MockIncrementalUnit(abstract.IncrementalUnit):
    def __init__(self, creator=MockAbstract(), 
                 iuid="test_iuid", 
                 previous_iu=MockPreviousIU(),
                 grounded_in=MockGrounded()):
        self.previous_iu = previous_iu
        self.MAX_DEPTH = 0
        self.grounded_in = grounded_in
        self.created_at = 30
        self._processed_list = [1,2,3,4]
        self.mutex = MockMutex()
        self.creator = creator
        self.payload = "payload!!!"
        self.revoked = False
        self.iuid = iuid
    def set_processed(self, module):
        self._processed_list.append(module)
    def type(self):
        return "MOCK IU"
    def index(self, iu):
        return 2
    
class MockBuffer:
    def __init__(self, update_message=None, mutex=None, queue=None):
        self.buffer_present = True
        self.update_message = update_message
        self.mutex = mutex
        self.queue = queue
        self.buffer_empty = False
        self.provider = "mock_provide"
        self.consumer = "mock_consume"
        self.args = "arg"
        self.meta_data = "meta_data"
    def remove(self):
        self.buffer_present = False
    def get(self, timeout=None):
        self.buffer_empty = True
        return self.update_message
    def empty(self):
        return self.buffer_empty
    def left_buffers(self):
        return []
    def right_buffers(self):
        return []
    def name(self):
        return "mock_buffer"
    def get_init_arguments(self):
        return self.args
    
class MockBufferObject:
    def clear(self):
        return True