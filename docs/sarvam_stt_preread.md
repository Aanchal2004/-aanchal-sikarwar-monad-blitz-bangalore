# Sarvam AI Speech-to-Text — Pre-Read for Hackathon

> Quick reference pulled from [docs.sarvam.ai](https://docs.sarvam.ai) via the Sarvam docs MCP. Use this when wiring voice input into agents (voice commands, live captions, meeting transcription, Hindi/Indic support).

---

## Executive Summary

**What is Sarvam STT?**
Indian-language-first speech recognition from [Sarvam AI](https://sarvam.ai). Optimized for Indic accents, code-mixed speech (Hinglish), and telephony audio. Three transport options: REST (short clips), WebSocket (live streaming), Batch (long files + diarization).

**Why use it in the hackathon?**
- You have **₹100 free credits** on signup (never expire)
- Strong on **11–22 Indian languages** + auto-detect
- **Saaras v3** is the current model — use `mode="transcribe"` instead of legacy Saarika v2.5
- Fits agent UX: push-to-talk commands, voice-to-agent pipeline, multilingual demos

**Pricing (bill per second, rounded up):**

| Service | Price |
|---------|-------|
| Speech to Text | ₹30 / hour |
| STT + Diarization | ₹45 / hour |
| STT & Translate (→ English) | ₹30 / hour |

---

## Setup

1. Sign up: [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
2. Generate API key in **API Keys** section
3. Store in env — never commit:

```env
SARVAM_API_KEY=your_key_here
```

4. Install Python SDK:

```bash
pip install sarvamai
```

**Auth header (all requests):**

```
api-subscription-key: YOUR_SARVAM_API_KEY
```

> Auth failures return **HTTP 403** (not 401). Error code: `invalid_api_key_error`.

---

## Which API to Use?

| | REST | WebSocket | Batch |
|---|------|-----------|-------|
| **Endpoint** | `POST /speech-to-text` | `wss://api.sarvam.ai/speech-to-text/ws` | `POST /speech-to-text/job/v1` |
| **Processing** | Sync | Real-time stream | Async job |
| **Max length** | 30 seconds | Continuous | 1 hour / file |
| **Files** | 1 | 1 stream | Up to 20 / job |
| **Diarization** | No | No | Yes |
| **Timestamps** | No | No | Yes (chunk-level) |
| **Formats** | All major formats | WAV + PCM only | All major formats |

**Decision guide:**
- **REST** — voice search, push-to-talk, short voice notes (≤30s)
- **WebSocket** — live mic, browser audio, voice agents, captions
- **Batch** — meetings, interviews, call recordings, speaker labels

Docs: [Which API to use](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/which-api-to-use)

---

## Models

### Saaras v3 (recommended)

```python
model="saaras:v3"
```

Supports **23 languages**, auto-detect, and 5 output **modes**:

| Mode | What it does |
|------|--------------|
| `transcribe` | Native script, normalized numbers (default) |
| `translate` | Speech → **English** text |
| `verbatim` | Raw speech, fillers preserved, spoken numbers |
| `translit` | Roman/Latin script |
| `codemix` | English words in English, Indic in native script |

### Saarika v2.5 (legacy — deprecating)

```python
model="saarika:v2.5"
language_code="hi-IN"  # or "unknown" for auto-detect
```

Migrate to Saaras v3 with `mode="transcribe"`.

---

## Supported Languages (core 11)

| Language | Code |
|----------|------|
| English (Indian) | `en-IN` |
| Hindi | `hi-IN` |
| Bengali | `bn-IN` |
| Tamil | `ta-IN` |
| Telugu | `te-IN` |
| Kannada | `kn-IN` |
| Malayalam | `ml-IN` |
| Marathi | `mr-IN` |
| Gujarati | `gu-IN` |
| Punjabi | `pa-IN` |
| Odia | `od-IN` |

Saaras v3 adds: `as-IN`, `ur-IN`, `ne-IN`, and others. Use `language_code="unknown"` only when language is truly unknown — specifying language improves accuracy.

---

## REST API (short audio)

**Endpoint:** `POST https://api.sarvam.ai/speech-to-text`

**Required:** `file` (multipart audio)

**Optional:** `model`, `language_code`, `mode`, `input_audio_codec` (required for PCM)

```python
from sarvamai import SarvamAI
from sarvamai.core.api_error import ApiError

client = SarvamAI(api_subscription_key="YOUR_SARVAM_API_KEY")

response = client.speech_to_text.transcribe(
    file=open("audio.wav", "rb"),
    model="saaras:v3",
    language_code="hi-IN",
    mode="transcribe",
)
print(response.transcript)
print(response.language_code)
print(response.language_probability)  # 0.0–1.0
```

**Response fields:**

| Field | Description |
|-------|-------------|
| `request_id` | Unique request ID |
| `transcript` | Transcribed (or translated) text |
| `language_code` | Detected BCP-47 code (e.g. `hi-IN`) |
| `language_probability` | Detection confidence |

**Audio formats:** WAV, MP3, AAC, AIFF, OGG, OPUS, FLAC, MP4/M4A, AMR, WMA, WebM, PCM (`pcm_s16le`, `pcm_l16`, `pcm_raw` at **16 kHz only**).

Best sample rate: **16 kHz**. Multi-channel auto-merged to mono.

---

## Speech-to-Text-Translate

Dedicated endpoint for **English output** from Indic speech:

```
POST https://api.sarvam.ai/speech-to-text-translate
```

Or use Saaras v3 on the main endpoint with `mode="translate"`.

```python
response = client.speech_to_text.translate(
    file=open("audio.wav", "rb"),
    model="saaras:v3",
    mode="translate",
)
# response.transcript is English
```

---

## WebSocket (live streaming)

**Endpoint:** `wss://api.sarvam.ai/speech-to-text/ws`

**Use when:** mic input, voice agents, live captions.

**Constraints:**
- WAV and raw PCM only (`wav`, `pcm_s16le`, `pcm_l16`, `pcm_raw`)
- Sample rates: **8 kHz** (telephony) or **16 kHz**

**Key query params:** `language-code`, `model`, `mode`, `sample_rate`, VAD tuning (`high_vad_sensitivity`, speech thresholds, `flush_signal`, etc.)

**Message types:** send audio chunks → receive `Transcription`; use `Speech Flush Signal` between segments.

Prefer SDK over raw WebSocket for streaming. Docs playground is not ideal for streaming tests.

---

## Batch API (long audio + diarization)

For files up to **1 hour**, up to **20 files** per job.

```python
job = client.speech_to_text_job.create_job(
    model="saaras:v3",
    language_code="en-IN",
    mode="transcribe",
    with_diarization=True,
    num_speakers=2,  # optional, 1–10; omit to auto-detect
)
job.upload_files(file_paths=["meeting.mp3"])
job.start()
job.wait_until_complete()
job.download_outputs(output_dir="./output")
```

**Diarized output** includes per-speaker entries with `start_time_seconds`, `end_time_seconds`, `speaker_id`.

**Polling:** wait ≥ **5 ms** between status checks to avoid rate limits.

---

## Rate Limits (by plan)

| Plan | REST | WebSocket | Batch |
|------|------|-----------|-------|
| Starter | 60 req/min | 20 concurrent | 20 req/min |
| Pro | 100 req/min | 100 concurrent | 100 req/min |
| Business | 4,000 req/min | 100 concurrent | 500 req/min |

---

## Error Handling

| Status | Code | Action |
|--------|------|--------|
| 403 | `invalid_api_key_error` | Fix API key — do not retry |
| 429 | `insufficient_quota_error` | Out of credits — add billing |
| 429 | `rate_limit_exceeded_error` | Exponential backoff |
| 500/503 | server error | Retry with backoff |
| 400/422 | bad request | Fix payload — do not retry |

```python
import time
from sarvamai.core.api_error import ApiError

def call_with_backoff(fn, max_retries=5):
    delay = 1.0
    for attempt in range(max_retries):
        try:
            return fn()
        except ApiError as e:
            if e.status_code not in (429, 500, 503) or attempt == max_retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)
```

Status page: [status.sarvam.ai](https://status.sarvam.ai/) · Support: `developer@sarvam.ai`

---

## Hackathon Integration Ideas

1. **Voice → agent pipeline** — WebSocket STT → FastAPI `/agents/run` with transcript as user message
2. **Multilingual demo** — Hindi voice command → Saaras transcribe → agent executes on Monad testnet
3. **Push-to-talk UI** — Frontend records ≤30s blob → REST STT → display + send to backend
4. **Meeting digest agent** — Batch STT + diarization → LangGraph summarizer → on-chain reputation attestation

**Architecture sketch:**

```
Mic / audio file
    → Sarvam STT (REST or WS)
    → transcript string
    → FastAPI agent endpoint
    → structured intent JSON
    → policy validator
    → Monad tx (separate signer)
```

Keep STT on the **proposal** side — never let raw LLM output sign transactions.

---

## Key Doc Links

- [STT Overview](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/overview)
- [REST API guide](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/rest-api)
- [WebSocket API](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe/ws)
- [Batch API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/speech-to-text/batch-api)
- [Saaras v3 model](https://docs.sarvam.ai/api-reference-docs/getting-started/models/saaras)
- [Authentication](https://docs.sarvam.ai/api-reference-docs/authentication)
- [Pricing](https://docs.sarvam.ai/api-reference-docs/pricing)
- [Errors & troubleshooting](https://docs.sarvam.ai/api-reference-docs/errors-troubleshooting)

---

*Last synced from Sarvam docs MCP — June 2026*
