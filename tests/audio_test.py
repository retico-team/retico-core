import unittest
from retico_core import audio
from retico_core import UpdateType
from mock_classes import MockAudioBuffer, MockAudioIU, MockGrounded, MockMutex, MockStream, MockWav
from mock import patch
import pyaudio



'''
test format:
def test_X(self):
    #Arrange

        #Act

        #Assert
'''

# Test cases
class TestAudioModule(unittest.TestCase):

    @patch('retico_core.audio.pyaudio.PyAudio.get_host_api_info_by_index')
    @patch('retico_core.audio.pyaudio.PyAudio.get_device_info_by_host_api_device_index')
    def test_show_audio_devices(self, mock_device, mock_host):
        #Arrange
        mock_host.return_value = {"deviceCount": 2}
        mock_device.return_value = {"maxInputChannels": 1, "maxOutputChannels": 1, "name": "mock_device", "index": 1}

        #Act
        result = audio.show_audio_devices()

        #Assert
        self.assertEqual(result, None)


    def test_audio_iu_type(self):
        #Arrange
        expected_result = "Audio IU"

        #Act
        result = audio.AudioIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    @patch('retico_core.abstract.IncrementalUnit._remove_old_links')
    def test_audio_iu_init(self, old_mock):
        #Arrange
        old_mock.return_value = True
        mock_creator="creator"
        mock_iuid=3
        mock_previous_iu="prev"
        mock_grounded_in=MockGrounded()
        mock_rate="rate"
        mock_nframes=["frame1", "frame2"]
        mock_sample_width=45
        mock_raw_audio="sound"

        #Act
        result = audio.AudioIU(creator=mock_creator, 
                               iuid=mock_iuid, 
                               previous_iu=mock_previous_iu, 
                               grounded_in=mock_grounded_in,
                               rate=mock_rate,
                               nframes=mock_nframes,
                               sample_width=mock_sample_width,
                               raw_audio=mock_raw_audio)

        #Assert
        self.assertEqual(result.creator, mock_creator)
        self.assertEqual(result.iuid, mock_iuid)
        self.assertEqual(result.previous_iu, mock_previous_iu)
        self.assertEqual(result.grounded_in, mock_grounded_in)
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.nframes, mock_nframes)
        self.assertEqual(result.sample_width, mock_sample_width)
        self.assertEqual(result.raw_audio, mock_raw_audio)

    def test_audio_iu_set_audio(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_raw_audio = "new_sound"
        mock_nframes = "5"
        mock_rate = "7"
        mock_sample_width = "10"

        #Act
        audio.AudioIU.set_audio(mock_audio_IU, 
                                raw_audio=mock_raw_audio,
                                nframes=mock_nframes,
                                rate=mock_rate,
                                sample_width=mock_sample_width)
        
        #Assert
        self.assertEqual(mock_audio_IU.raw_audio, mock_raw_audio)
        self.assertEqual(mock_audio_IU.payload, mock_raw_audio)
        self.assertEqual(mock_audio_IU.nframes, int(mock_nframes))
        self.assertEqual(mock_audio_IU.rate, int(mock_rate))
        self.assertEqual(mock_audio_IU.sample_width, int(mock_sample_width))

    def test_audio_iu_audio_length(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.nframes = "5.5"
        mock_audio_IU.rate = ".01"
        expected_result = float(mock_audio_IU.nframes) / float(mock_audio_IU.rate)

        #Act
        result = audio.AudioIU.audio_length(mock_audio_IU)

        #Assert
        self.assertEqual(result, expected_result)

    def test_speech_iu_type(self):
        #Arrange
        expected_result = "Speech IU"

        #Act
        result = audio.SpeechIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_speech_iu_init(self):
        #Arrange
        expected_result = False

        #Act
        result = audio.SpeechIU()

        #Assert
        self.assertEqual(result.dispatch, expected_result)

    def test_dispatched_audio_iu_type(self):
        #Arrange
        expected_result = "Dispatched Audio IU"

        #Act
        result = audio.DispatchedAudioIU.type()

        #Assert
        self.assertEqual(result, expected_result)

    def test_dispatched_audio_iu_init(self):
        #Arrange
        expected_dispatch = False
        expected_completion = 0.0

        #Act
        result = audio.DispatchedAudioIU()

        #Assert
        self.assertEqual(result.is_dispatching, expected_dispatch)
        self.assertEqual(result.completion, expected_completion)

    def test_dispatched_audio_iu_set_dispatching(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_completion = "comp"
        mock_is_dispatching = True

        #Act
        audio.DispatchedAudioIU.set_dispatching(mock_audio_IU, mock_completion, mock_is_dispatching)

        #Assert
        self.assertEqual(mock_audio_IU.completion, mock_completion)
        self.assertEqual(mock_audio_IU.is_dispatching, mock_is_dispatching)

    def test_microphone_module_name(self):
        #Arrange
        expected_result = "Microphone Module"

        #Act
        result = audio.MicrophoneModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_microphone_module_description(self):
        #Arrange
        expected_result = "A prodicing module that records audio from microphone."

        #Act
        result = audio.MicrophoneModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_microphone_module_output_iu(self):
        #Arrange
        expected_result = audio.AudioIU

        #Act
        result = audio.MicrophoneModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_microphone_module_callback(self):
        #Arrange
        mock_audio_iu = MockAudioIU()
        mock_audio_iu.audio_buffer = MockAudioBuffer()
        mock_data = "data"
        expected_result = (mock_data, pyaudio.paContinue)


        #Act
        result = audio.MicrophoneModule.callback(mock_audio_iu, mock_data, 1,2,3)

        #Assert
        self.assertEqual(result, expected_result)
        self.assertEqual(mock_audio_iu.audio_buffer.in_data, mock_data)

    def test_microphone_module_init(self):
        #Arrange
        mock_frame_length = 50.0
        mock_rate = 32.4
        mock_width = 53.2
        expected_stream = None
        expected_chunch = round(mock_rate * mock_frame_length)

        #Act
        result = audio.MicrophoneModule(frame_length=mock_frame_length,
                                        rate=mock_rate,
                                        sample_width=mock_width)

        #Assert
        self.assertEqual(result.frame_length, mock_frame_length)
        self.assertEqual(result.chunk_size, expected_chunch)
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.sample_width, mock_width)
        self.assertEqual(result.stream, expected_stream)

    def test_microphone_module_process_update_no_bufffer(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = None
        expected_result = None

        #Act
        result = audio.MicrophoneModule.process_update(mock_audio_IU, 1)

        #Assert
        self.assertEqual(result, expected_result)

    def test_microphone_module_process_update_fail(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = MockAudioBuffer()
        mock_audio_IU.audio_buffer.fail = True
        expected_result = None

        #Act
        result = audio.MicrophoneModule.process_update(mock_audio_IU, 1)

        #Assert
        self.assertEqual(result, expected_result)

    @patch('retico_core.UpdateMessage.from_iu')
    def test_microphone_module_process_update_pass(self, mock_update):
        #Arrange
        mock_update.return_value = True
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = MockAudioBuffer()
        mock_audio_IU.audio_buffer.fail = False
        mock_audio_IU.chunk_size = 0
        mock_audio_IU.rate = 0
        mock_audio_IU.sample_width = 0
        expected_result = True

        #Act
        result = audio.MicrophoneModule.process_update(mock_audio_IU, 1)

        #Assert
        self.assertEqual(result, expected_result)

    def test_microphone_module_process_setup(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU._p = MockAudioIU()
        mock_audio_IU.chunk_size = 0
        mock_audio_IU.rate = 0
        mock_audio_IU.sample_width = 0
        mock_audio_IU.callback = False
        expected_output = "opened!"

        #Act
        audio.MicrophoneModule.setup(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.stream, expected_output)

    def test_microphone_module_prepare_run(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.stream = MockStream()
        expected_output = True

        #Act
        audio.MicrophoneModule.prepare_run(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.stream.started, expected_output)

    def test_microphone_module_shutdown(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.stream = MockStream()
        expected_output = None

        #Act
        audio.MicrophoneModule.shutdown(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.stream, expected_output)

    def test_speaker_module_name(self):
        #Arrange
        expected_result = "Speaker Module"

        #Act
        result = audio.SpeakerModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_speaker_module_description(self):
        #Arrange
        expected_result = "A consuming module that plays audio from speakers."

        #Act
        result = audio.SpeakerModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_speaker_module_input_ius(self):
        #Arrange
        expected_result = [audio.AudioIU]

        #Act
        result = audio.SpeakerModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_speaker_module_output_iu(self):
        #Arrange
        expected_result = None

        #Act
        result = audio.SpeakerModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    @patch('retico_core.audio.pyaudio.PyAudio.get_default_output_device_info')
    def test_speaker_module_init(self, mock_default):
        #Arrange
        mock_default.return_value = {"index": "mock_index"}
        mock_rate = 50
        mock_sample_width = 5
        mock_use_speaker = "NO!"

        #Act
        result = audio.SpeakerModule(rate=mock_rate,
                                    sample_width=mock_sample_width,
                                    use_speaker=mock_use_speaker)

        #Assert
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.sample_width, mock_sample_width)
        self.assertEqual(result.use_speaker, mock_use_speaker)
        self.assertEqual(result.device_index, "mock_index")

    def test_speaker_module_process_update_none(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        expected_result = None

        #Act
        result = audio.SpeakerModule.process_update(mock_audio_IU, [(1,"update")])

        #Assert
        self.assertEqual(result, expected_result)

    def test_speaker_module_process_update_queue(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.raw_audio = bytes(mock_audio_IU.raw_audio, encoding='utf8')
        mock_audio_IU.stream = MockStream()
        mock_update_message = [(mock_audio_IU,UpdateType.ADD), (mock_audio_IU, UpdateType.ADD)]
        expected_result = [b'sound_file', b'sound_file']

        #Act
        audio.SpeakerModule.process_update(mock_audio_IU, mock_update_message)

        #Assert
        self.assertEqual(mock_audio_IU.stream.raw, expected_result)

    @patch('retico_core.audio.platform.system')
    def test_speaker_module_setup(self, mock_system):
        #Arrange
        mock_system.return_value = "None"
        mock_audio_IU = MockAudioIU()
        mock_audio_IU._p = MockAudioIU()
        expected_result = True

        #Act
        audio.SpeakerModule.setup(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU._p.opened, expected_result)

    def test_speaker_module_shutdown(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.stream = MockStream()
        expected_result = None

        #Act
        audio.SpeakerModule.shutdown(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.stream, expected_result)

    def test_streaming_speaker_module_name(self):
        #Arrange
        expected_result = "Streaming Speaker Module"

        #Act
        result = audio.StreamingSpeakerModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_streaming_speaker_module_description(self):
        #Arrange
        expected_result = "A consuming module that plays audio from speakers."

        #Act
        result = audio.StreamingSpeakerModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_streaming_speaker_module_input_ius(self):
        #Arrange
        expected_result = [audio.AudioIU]

        #Act
        result = audio.StreamingSpeakerModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_streaming_speaker_module_output_iu(self):
        #Arrange
        expected_result = None

        #Act
        result = audio.StreamingSpeakerModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)  
    
    def test_streaming_speaker_module_callback_queue(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = MockAudioBuffer()
        mock_audio_IU.audio_buffer.fail = False
        mock_frame_count = 5
        expected_result = (True, 0)

        #Act
        result = audio.StreamingSpeakerModule.callback(mock_audio_IU, 0, mock_frame_count, 0, 0)

        #Assert
        self.assertEqual(result, expected_result)

    def test_streaming_speaker_module_callback_queue_empty(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = MockAudioBuffer()
        mock_audio_IU.audio_buffer.fail = True
        mock_audio_IU.sample_width = 5
        mock_frame_count = 5
        expected_result = (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 0)

        #Act
        result = audio.StreamingSpeakerModule.callback(mock_audio_IU, 0, mock_frame_count, 0, 0)

        #Assert
        self.assertEqual(result, expected_result)

    def test_streaming_speaker_module_callback_no_audio_buffer(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = None
        mock_audio_IU.sample_width = 5
        mock_frame_count = 5
        expected_result = (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 0)

        #Act
        result = audio.StreamingSpeakerModule.callback(mock_audio_IU, 0, mock_frame_count, 0, 0)

        #Assert
        self.assertEqual(result, expected_result)
    
    def test_streaming_speaker_module_prepare_run(self):
            #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.stream = MockStream()
        expected_result = True

        #Act
        audio.StreamingSpeakerModule.prepare_run(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.stream.started, expected_result)

    def test_streaming_speaker_module_init(self):
        #Arrange
        #frame_length=0.02, rate=44100, sample_width=2
        mock_frame_length = 1
        mock_rate = 2
        mock_width = 3

        #Act
        result = audio.StreamingSpeakerModule(frame_length=mock_frame_length,
                                     rate=mock_rate,
                                     sample_width=mock_width)

        #Assert
        self.assertEqual(result.frame_length, mock_frame_length)
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.sample_width, mock_width)
        self.assertEqual(result.chunk_size, round(mock_frame_length * mock_rate))

    def test_streaming_sspeaker_module_process_update_none(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        expected_result = None

        #Act
        result = audio.StreamingSpeakerModule.process_update(mock_audio_IU, [(1,"update")])

        #Assert
        self.assertEqual(result, expected_result)

    def test_streaming_sspeaker_module_process_update_buffer(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.audio_buffer = MockAudioBuffer()
        mock_update_message = [(mock_audio_IU,UpdateType.ADD), (mock_audio_IU, UpdateType.ADD)]
        expected_result = ['sound_file', 'sound_file']

        #Act
        audio.StreamingSpeakerModule.process_update(mock_audio_IU, mock_update_message)

        #Assert
        self.assertEqual(mock_audio_IU.audio_buffer.buf, expected_result)

    def test_streaming_speaker_module_setup(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU._p = MockAudioIU()
        expected_result = True

        #Act
        audio.StreamingSpeakerModule.setup(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU._p.opened, expected_result)
  
    def test_streaming_speaker_module_prepare_run(self):
            #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.stream = MockStream()
        expected_result = True

        #Act
        audio.StreamingSpeakerModule.prepare_run(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.stream.started, expected_result)
        
    def test_streaming_speaker_module_shutdown(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.stream = MockStream()

        #Act
        audio.StreamingSpeakerModule.shutdown(mock_audio_IU)

        #Assert
        self.assertAlmostEqual(mock_audio_IU.stream, None)

    def test_audio_dispatcher_module_name(self):
        #Arrange
        expected_result = "Audio Dispatching Module"

        #Act
        result = audio.AudioDispatcherModule.name()

        #Assert
        self.assertEqual(result, expected_result)
    
    def test_audio_dispatcher_module_description(self):
        #Arrange
        expected_result = (
            "A module that transmits audio by splitting it up into" "streamable pakets."
        )

        #Act
        result = audio.AudioDispatcherModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_audio_dispatcher_module_input_ius(self):
        #Arrange
        expected_result = [audio.SpeechIU]

        #Act
        result = audio.AudioDispatcherModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_audio_dispatcher_module_output_iu(self):
        #Arrange
        expected_result = audio.DispatchedAudioIU

        #Act
        result = audio.AudioDispatcherModule.output_iu()

        #Assert
        self.assertEqual(result, expected_result)

    def test_audio_dispatcher_module_init(self):
        #Arrange
        mock_target_frame_length=1.02
        mock_rate=44
        mock_sample_width=90
        mock_speed=5.0
        mock_continuous=False
        mock_silence="quiet"
        mock_interrupt=False

        #Act
        result = audio.AudioDispatcherModule(target_frame_length=mock_target_frame_length,
                                             rate=mock_rate,
                                             sample_width=mock_sample_width,
                                             speed=mock_speed,
                                             continuous=mock_continuous,
                                             silence=mock_silence,
                                             interrupt=mock_interrupt)

        #Assert
        self.assertEqual(result.target_chunk_size, round(mock_target_frame_length * mock_rate))
        self.assertEqual(result.target_frame_length, mock_target_frame_length)
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.sample_width, mock_sample_width)
        self.assertEqual(result.speed, mock_speed)
        self.assertEqual(result.continuous, mock_continuous)
        self.assertEqual(result.silence, mock_silence)
        self.assertEqual(result.interrupt, mock_interrupt)

    def test_audio_dispatcher_module_is_dispatching(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.dispatching_mutex = MockMutex()
        mock_audio_IU._is_dispatching = "dispatch"

        #Act
        result = audio.AudioDispatcherModule.is_dispatching(mock_audio_IU)

        #Assert
        self.assertEqual(result, mock_audio_IU._is_dispatching)

    def test_audio_dispatcher_module_set_dispatching(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.dispatching_mutex = MockMutex()
        mock_value = "new_dispatch"

        #Act
        audio.AudioDispatcherModule.set_dispatching(mock_audio_IU, mock_value)

        #Assert
        self.assertEqual(mock_audio_IU._is_dispatching, mock_value)

    def test_audio_dispatcher_module_process_update(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.interrupt = True
        mock_audio_IU.dispatch = True
        mock_audio_IU.nframes = 10
        mock_audio_IU.target_chunk_size = 5
        mock_audio_IU.raw_audio = b"sound_file"
        mock_update = [(mock_audio_IU,UpdateType.ADD), ("fake", UpdateType.REVOKE), (mock_audio_IU, UpdateType.ADD)]
        expected_result = None

        #Act
        result = audio.AudioDispatcherModule.process_update(mock_audio_IU, mock_update)

        #Assert
        self.assertEqual(len(mock_audio_IU.audio_buffer), 2)
        self.assertEqual(result, expected_result)

    def test_audio_dispatcher_module_shutdown(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        expected_run = False
        expected_buffer = []

        #Act
        audio.AudioDispatcherModule.shutdown(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.run_loop, expected_run)
        self.assertEqual(mock_audio_IU.audio_buffer, expected_buffer)

    def test_audio_recorder_module_name(self):
        #Arrange
        expected_result = "Audio Recorder Module"

        #Act
        result = audio.AudioRecorderModule.name()

        #Assert
        self.assertEqual(result, expected_result)

    def test_audio_recorder_module_description(self):
        #Arrange
        expected_result = "A Module that saves incoming audio to disk."

        #Act
        result = audio.AudioRecorderModule.description()

        #Assert
        self.assertEqual(result, expected_result)

    def test_audio_recorder_module_input_ius(self):
        #Arrange
        expected_result = [audio.AudioIU]

        #Act
        result = audio.AudioRecorderModule.input_ius()

        #Assert
        self.assertEqual(result, expected_result)

    def test_audio_recorder_module_init(self):
        #Arrange
        mock_filename = "mock_file"
        mock_rate = 45
        mock_width = 56
        expected_wavfile = None

        #Act
        result = audio.AudioRecorderModule(filename=mock_filename,
                                           rate=mock_rate,
                                           sample_width=mock_width)

        #Assert
        self.assertEqual(result.filename, mock_filename)
        self.assertEqual(result.rate, mock_rate)
        self.assertEqual(result.sample_width, mock_width)
        self.assertEqual(result.wavfile, expected_wavfile)

    def test_audio_recorder_module_process_update(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.wavfile = MockWav()
        mock_update = [(mock_audio_IU,UpdateType.ADD), (mock_audio_IU, UpdateType.ADD)]
        expected_result = True

        #Act
        audio.AudioRecorderModule.process_update(mock_audio_IU, mock_update)

        #Assert
        self.assertEqual(mock_audio_IU.wavfile.write_state, expected_result)

    @patch('retico_core.audio.wave.open')
    def test_audio_recorder_module_setup(self, mock_wave):
        #Arrange
        mock_wave.return_value = MockWav()
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.filename = "fake_file"
        expected_result = True

        #Act
        audio.AudioRecorderModule.setup(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.wavfile.framed, expected_result)
        self.assertEqual(mock_audio_IU.wavfile.chaneled, expected_result)
        self.assertEqual(mock_audio_IU.wavfile.wide, expected_result)

    def test_audio_recorder_module_shutdown(self):
        #Arrange
        mock_audio_IU = MockAudioIU()
        mock_audio_IU.wavfile = MockWav()
        expected_result = True

        #Act
        audio.AudioRecorderModule.shutdown(mock_audio_IU)

        #Assert
        self.assertEqual(mock_audio_IU.wavfile.closed, expected_result)

        
        

if __name__ == '__main__':
    unittest.main()