from voice.recognizer import Recorder

def test_record():
    recorder = Recorder()
    audio = recorder.record(5)
    assert audio