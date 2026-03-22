"""
voice_handler.py
Handles Speech-to-Text transcription using NVIDIA NIM Whisper Large V3
via the Riva gRPC cloud API (grpc.nvcf.nvidia.com).
"""

import io
import wave
import struct
import numpy as np

import riva.client
import riva.client.proto.riva_asr_pb2 as rasr
import riva.client.proto.riva_asr_pb2_grpc as rasr_grpc

from backend.src.config import ModelConfig

# ── NVIDIA Cloud Functions (NVCF) gRPC endpoint ────────────────────────────
RIVA_SERVER = "grpc.nvcf.nvidia.com:443"
WHISPER_NVCF_FUNCTION_ID = "b702f636-f60c-4a3d-a6f4-f3568c13bd7d"
LANGUAGE_CODE = "en-US"
AUDIO_CHANNEL_COUNT = 1
SAMPLE_RATE_HZ = 16000


def _get_auth(api_key: str) -> riva.client.Auth:
    """Build authenticated Riva Auth object for the NVCF cloud endpoint."""
    metadata = [
        ("function-id", WHISPER_NVCF_FUNCTION_ID),
        ("authorization", f"Bearer {api_key}"),
    ]
    return riva.client.Auth(
        use_ssl=True,
        uri=RIVA_SERVER,
        metadata_args=metadata,
    )


def _audio_bytes_to_linear16(audio_bytes: bytes) -> tuple[bytes, int]:
    """
    Read WAV bytes and return (raw_pcm_bytes, sample_rate).
    Converts to 16-bit mono if necessary.
    """
    with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
        n_channels = wf.getnchannels()
        samp_width = wf.getsampwidth()  # bytes per sample
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    # Convert to numpy int16
    if samp_width == 2:
        samples = np.frombuffer(raw, dtype=np.int16)
    elif samp_width == 4:
        samples = np.frombuffer(raw, dtype=np.int32).astype(np.int16)
    elif samp_width == 1:
        samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.int16) - 128) * 256
    else:
        raise ValueError(f"Unsupported sample width: {samp_width}")

    # Mix stereo → mono
    if n_channels == 2:
        samples = samples.reshape(-1, 2).mean(axis=1).astype(np.int16)
    elif n_channels > 2:
        samples = samples.reshape(-1, n_channels).mean(axis=1).astype(np.int16)

    return samples.tobytes(), framerate


def transcribe_audio(audio_bytes: bytes, filename: str = "recording.wav") -> str:
    """
    Transcribe audio bytes using NVIDIA NIM Whisper Large V3 (Riva gRPC Cloud API).

    Args:
        audio_bytes: Raw audio file bytes (WAV format, recorded by st.audio_input).
        filename: Filename hint (unused, kept for API compatibility).

    Returns:
        Transcribed text string.

    Raises:
        ValueError: If the Whisper API key is missing.
        RuntimeError: If transcription fails.
    """
    api_key = ModelConfig.WHISPER_API_KEY
    if not api_key:
        raise ValueError(
            "Whisper API key not found. "
            "Make sure 'whisper_large_v3' is set in your .env file."
        )

    try:
        # Parse WAV and get raw Linear16 PCM
        pcm_bytes, sample_rate = _audio_bytes_to_linear16(audio_bytes)
    except Exception as e:
        raise RuntimeError(f"Failed to decode audio: {e}") from e

    try:
        auth = _get_auth(api_key)
        asr_service = riva.client.ASRService(auth)

        config = riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            language_code=LANGUAGE_CODE,
            max_alternatives=1,
            enable_automatic_punctuation=True,
            audio_channel_count=AUDIO_CHANNEL_COUNT,
            sample_rate_hertz=sample_rate,
        )

        response = asr_service.offline_recognize(pcm_bytes, config)

        # Extract transcript text from all result alternatives
        transcript_parts = []
        for result in response.results:
            if result.alternatives:
                transcript_parts.append(result.alternatives[0].transcript)

        return " ".join(transcript_parts).strip()

    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}") from e
