"""
Speech masking using Silero VAD — pipeline integration
=======================================================
Runs after process_speech_MITAST.py. For every clip labelled "Speech" by
MIT-AST, this script:
  1. Loads the wav from disk
  2. Runs Silero VAD at 16 kHz to detect speech frames
  3. Zeros out speech frames in the 48 kHz stereo audio (masks in-place)
  4. Overwrites the original wav with the masked version
  5. Adds two columns to the _speechless.xlsx metadata:
       - speech_masked_pct      : float, percentage of the 3s clip that was
                                  silenced (0.0 for non-Speech clips)
       - speech_masked_intervals: str,   JSON list of [start_ms, end_ms] pairs
                                  for each masked interval ("[]" if none)

Called from run_preprocessing.py via process_all_data(conf).

Dependencies:
    pip install torch torchaudio soundfile pandas numpy openpyxl

"""

import json
import os
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
import torch
import torchaudio


# ── Constants ─────────────────────────────────────────────────────────────────

SAMPLE_RATE = 48000
SILERO_SR   = 16000          # Silero VAD native sample rate
RATIO       = SAMPLE_RATE // SILERO_SR   # = 3

COL_MIT       = "MIT_AST_label"
COL_MASKED_PCT = "speech_masked_pct"
COL_MASKED_INT = "speech_masked_intervals"


# ── Silero VAD ────────────────────────────────────────────────────────────────

def load_silero_vad():
    print("Loading Silero VAD model...")
    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False,
        verbose=False
    )
    get_speech_timestamps = utils[0]
    print("Silero VAD loaded.")
    return model, get_speech_timestamps


# ── VAD + masking ─────────────────────────────────────────────────────────────

def get_speech_mask_and_intervals(audio: np.ndarray,
                                  model,
                                  get_speech_timestamps,
                                  threshold: float):
    """
    Parameters
    ----------
    audio : np.ndarray, shape (channels, n_frames) at 48 kHz

    Returns
    -------
    mask_48k   : np.ndarray bool, shape (n_frames,)  — True where speech
    intervals_ms : list of [start_ms, end_ms] pairs (at 48 kHz resolution,
                   expressed in milliseconds from clip start)
    """
    mono   = audio.mean(axis=0)
    tensor = torch.from_numpy(mono).unsqueeze(0)

    resampler  = torchaudio.transforms.Resample(orig_freq=SAMPLE_RATE,
                                                new_freq=SILERO_SR)
    tensor_16k = resampler(tensor).squeeze(0)
    tensor_16k = tensor_16k.to(next(model.parameters()).device)

    n_original = audio.shape[1]
    n_16k      = tensor_16k.shape[0]

    speech_ts = get_speech_timestamps(
        tensor_16k, model,
        threshold=threshold,
        sampling_rate=SILERO_SR,
        return_seconds=False          # frame indices at 16 kHz
    )

    # Build boolean mask at 16 kHz, then upsample to 48 kHz
    mask_16k = np.zeros(n_16k, dtype=bool)
    for ts in speech_ts:
        mask_16k[max(0, ts['start']):min(n_16k, ts['end'])] = True

    mask_48k = np.repeat(mask_16k, RATIO)
    if len(mask_48k) > n_original:
        mask_48k = mask_48k[:n_original]
    elif len(mask_48k) < n_original:
        mask_48k = np.pad(mask_48k, (0, n_original - len(mask_48k)))

    # Convert Silero 16 kHz frame indices → milliseconds at 48 kHz
    # (we use 48 kHz frames as ground truth to match the actual zeroed region)
    intervals_ms = []
    for ts in speech_ts:
        start_48k = min(ts['start'] * RATIO, n_original)
        end_48k   = min(ts['end']   * RATIO, n_original)
        start_ms  = round(start_48k / SAMPLE_RATE * 1000)
        end_ms    = round(end_48k   / SAMPLE_RATE * 1000)
        intervals_ms.append([start_ms, end_ms])

    return mask_48k, intervals_ms


# ── Main processing function (called by run_preprocessing.py) ─────────────────
def process_all_data(conf):
    fpath  = f"./er_path/fl_{conf['data_name']}"
    fpath0 = "./er_path/"
    threshold = conf.get("vad_threshold", 0.5)

    # Find all _metadata.xlsx files produced by the MIT-AST step
    all_files = list(Path(fpath).rglob("*_metadata.xlsx"))
    if not all_files:
        print("No _metadata.xlsx files found — skipping speech masking.")
        return

    # Load Silero once for all metadata files
    model, get_speech_timestamps = load_silero_vad()
    model.eval()
    if torch.cuda.is_available():
        model = model.to('cuda')
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")


    for mfile in all_files:
        mfile = str(mfile)
        print(f"\nSilero masking: {mfile}")

        data = pd.read_excel(mfile)
        data = data.dropna(subset=["time"])

        # Initialise new columns — 0.0 / "[]" for all rows
        data[COL_MASKED_PCT] = 0.0
        data[COL_MASKED_INT] = "[]"

        speech_rows = data[(data[COL_MIT] == "file_missing")|
                           (data[COL_MIT] == "Speech")]
        print(f"  Speech clips to mask : {len(speech_rows):,}  "
              f"(out of {len(data):,} total)")

        n_ok = n_missing = n_fail = n_no_speech = n_speech_found = 0

        for row_idx, row in speech_rows.iterrows():
            afile = fpath0 + str(row["filename"])

            if not os.path.isfile(afile):
                # Should not happen in the new pipeline, but guard anyway
                n_missing += 1
                continue

            # Load wav
            try:
                audio_data, sr = sf.read(afile, dtype="float32", always_2d=True)
                audio = audio_data.T   # → (channels, frames)
                if sr != SAMPLE_RATE:
                    print(f"    !! unexpected sample rate {sr} in {afile}")
                    n_fail += 1
                    continue
            except Exception as e:
                print(f"    !! read error for {afile}: {e}")
                n_fail += 1
                continue

            # Run VAD
            try:
                with torch.no_grad():
                    mask, intervals_ms = get_speech_mask_and_intervals(
                        audio, model, get_speech_timestamps, threshold
                    )
            except Exception as e:
                print(f"    !! VAD error for {afile}: {e}")
                n_fail += 1
                continue

            speech_pct = 100.0 * mask.sum() / len(mask)

            # Apply mask and overwrite wav in-place
            audio[:, mask] = 0.0
            try:
                sf.write(afile, audio.T, SAMPLE_RATE, subtype="PCM_16")
            except Exception as e:
                print(f"    !! write error for {afile}: {e}")
                n_fail += 1
                continue

            # Update metadata row
            data.loc[row_idx, COL_MASKED_PCT] = round(speech_pct, 2)
            data.loc[row_idx, COL_MASKED_INT] = json.dumps(intervals_ms)

            n_ok += 1
            if speech_pct > 0:
                n_speech_found += 1
            else:
                n_no_speech += 1

        # Overwrite the same _speechless.xlsx with the two new columns
        data.to_excel(mfile)

        # ── Per-file summary ───────────────────────────────────────────────
        print(f"  {'─'*50}")
        print(f"  Processed OK            : {n_ok:,}")
        print(f"  File not found          : {n_missing:,}")
        print(f"  Errors (read/VAD/write) : {n_fail:,}")
        print(f"  Speech detected (>0%)   : {n_speech_found:,}")
        print(f"  No speech detected      : {n_no_speech:,}")
        if n_speech_found > 0:
            avg = data.loc[data[COL_MASKED_PCT] > 0, COL_MASKED_PCT].mean()
            print(f"  Avg masked pct (when>0) : {avg:.1f}%")
        print(f"  Updated metadata saved  : {mfile}")


if __name__ == '__main__':
    # Standalone usage — mirrors the pipeline conf structure
    import json as _json
    import sys
    cfile = sys.argv[1] if len(sys.argv) > 1 else "conf.json"
    with open(cfile) as f:
        conf = _json.load(f)
    process_all_data(conf)
