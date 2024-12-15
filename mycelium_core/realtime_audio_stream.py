
# Filename: /mycelium_core/realtime_audio_stream.py
import pyaudio
import numpy as np
from audio_feature_extractor import extract_features

def callback(in_data, frame_count, time_info, status):
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    features = extract_features(audio_data)
    print(f"Features Extracted: {features}")
    return (in_data, pyaudio.paContinue)

def start_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    input=True,
                    stream_callback=callback)
    stream.start_stream()

    try:
        while stream.is_active():
            pass
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()
