
# Filename: /mycelium_core/audio_feature_extractor.py
import librosa
import numpy as np

def extract_features(audio_file):
    y, sr = librosa.load(audio_file, sr=None)

    # Extract features
    rms = librosa.feature.rms(y=y).mean()
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y).mean()
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1)

    features = {
        "rms": rms,
        "spectral_centroid": spectral_centroid,
        "zero_crossing_rate": zero_crossing_rate,
        "mfccs": mfccs.tolist()
    }

    return features
