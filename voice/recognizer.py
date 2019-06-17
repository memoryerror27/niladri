import audioop
import pyaudio
import wave


class Recorder:
    """Record audio from microphone."""

    def __init__(self):
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.output_file = "output.wav"
        self.recorder = pyaudio.PyAudio()

        self.seconds_per_frame = self.chunk_size / self.rate
        self.silence_limit_seconds = 2
        self.silence_frame_count = 0
        self.min_energy_limit = 300

    def _get_frame_energy(self, frame):
        energy = audioop.rms(frame, self.recorder.get_sample_size(self.format))
        return energy

    def calibrate_energy_threshold(self, audio_stream, seconds=2):
        energy_levels = []
        for i in range(0, self.rate // self.chunk_size * seconds):
            frame = audio_stream.read(self.chunk_size)
            energy = self._get_frame_energy(frame)
            energy_levels.append(energy)

        avg_energy = sum(energy_levels) // len(energy_levels)

        # Increase limit by 20% to distinguish speech from noise better.
        self.min_energy_limit = avg_energy + avg_energy / 5
        print(avg_energy)

    def record(self, timeout=5):
        audio_frames = []
        audio_stream = self.recorder.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            frames_per_buffer=self.chunk_size,
            input=True,
        )
        self.calibrate_energy_threshold(audio_stream)
        print('Recording')
        # Record audio from audio_stream.
        while True:
            frame = audio_stream.read(self.chunk_size)
            energy = self._get_frame_energy(frame)
            print(energy)
            silence_duration_seconds = self.silence_frame_count * self.seconds_per_frame
            # Check if user is silent for more than the limit.
            if energy < self.min_energy_limit:
                if silence_duration_seconds < self.silence_limit_seconds:
                    self.silence_frame_count += 1
                    continue
                else:
                    break
            else:
                audio_frames.append(frame)
                self.silence_frame_count = 0

        audio_stream.stop_stream()
        audio_stream.close()

        return audio_frames

    def export(self, filename, audio_frames):
        """Write audio frames to WAV file."""
        # Combine frames to pass to the writeframes method.
        raw_frame_data = b"".join(audio_frames)

        output_wave_file = wave.open(filename, "wb")
        output_wave_file.setnchannels(self.channels)
        output_wave_file.setsampwidth(self.recorder.get_sample_size(self.format))
        output_wave_file.setframerate(self.rate)
        output_wave_file.writeframes(raw_frame_data)

        output_wave_file.close()

    def stop(self):
        self.recorder.terminate()

