+++
title = 'Audio Processing Pipleine for Ansit'
description = "" 
date = 2026-03-07T16:10:57+06:00
draft = false
tags = ["general"]
authors = ["Redoan"]
+++

For quran audio finder application Ansit, I created a python script that downloads mp3 files and uses ffmpeg to convert it to WAV fromat. Now My rust backend loads these wav files and use the following pipeline to generate hash and store in database for audio retrival. 
o
# 1. PCM Samples (from WAV)

When a WAV file is decoded, the audio samples are stored as **16‑bit
signed integers**.

Example:

    [1200, 2400, -1000, -2000, 500, 1500, -500, -1200]

Range:

    -32768 → 32767

Conceptually this represents a waveform in the **time domain**.

    time →

    1200  2400  -1000  -2000  500  1500  -500  -1200

------------------------------------------------------------------------

# 2. Normalize to f32

Convert integers to floating point values between **-1 and 1**.

Formula:

    x[n] = pcm / 32768

Example:

    [0.0366, 0.0732, -0.0305, -0.0610, 0.0152, 0.0458, -0.0152, -0.0366]

Visualization:

    Amplitude
     0.07 |        *
     0.04 |  *           *
     0.00 |-----------------------
    -0.04 |      *         *
    -0.07 |          *
           ----------------------→ time

------------------------------------------------------------------------

# 3. Pre‑emphasis (Optional)

A filter that boosts high frequencies.

Formula:

    y[n] = x[n] − α * x[n-1]
    α ≈ 0.95

Example result:

    [0.0366, 0.0385, -0.1001, -0.0310, 0.0730, 0.0314, -0.0588, -0.0221]

This step is **often skipped in music fingerprinting**.

------------------------------------------------------------------------

# 4. Framing

Split the signal into overlapping windows.

Example:

    frame_size = 4
    hop_size = 2

Frames:

    Frame1
    [0.0366, 0.0732, -0.0305, -0.0610]

    Frame2
    [-0.0305, -0.0610, 0.0152, 0.0458]

    Frame3
    [0.0152, 0.0458, -0.0152, -0.0366]

Visualization:

    Original signal
    x0 x1 x2 x3 x4 x5 x6 x7

    Frames

    [ x0 x1 x2 x3 ]
          [ x2 x3 x4 x5 ]
               [ x4 x5 x6 x7 ]

------------------------------------------------------------------------

# 5. Windowing

Each frame is multiplied by a **window function** (usually Hann).

Example Hann window:

    [0.0, 0.75, 0.75, 0.0]

Frame before:

    [0.0366, 0.0732, -0.0305, -0.0610]

After windowing:

    [0.0, 0.0549, -0.0228, 0.0]

Purpose:

-   Reduces **spectral leakage**
-   Smooths frame edges

------------------------------------------------------------------------

# 6. FFT (Fast Fourier Transform)

Converts **time domain → frequency domain**.

Input frame:

    [0.0, 0.0549, -0.0228, 0.0]

FFT output (complex numbers):

    [
     0.0321 + 0.0i,
     0.0120 - 0.0412i,
     -0.0777 + 0.0i,
     0.0120 + 0.0412i
    ]

Magnitude spectrum:

    [0.0321, 0.0429, 0.0777, 0.0429]

Frequency bins:

    Bin0  Bin1  Bin2  Bin3
    0.03  0.04  0.07  0.04

------------------------------------------------------------------------

# 7. Spectrogram

Stack FFT magnitudes from multiple frames.

Example:

    Frame1 → [0.03, 0.04, 0.07, 0.04]
    Frame2 → [0.02, 0.10, 0.03, 0.01]
    Frame3 → [0.01, 0.06, 0.09, 0.02]

Matrix:

              Frequency →
            f0    f1    f2    f3
    t0     0.03  0.04  0.07  0.04
    t1     0.02  0.10  0.03  0.01
    t2     0.01  0.06  0.09  0.02
    ↓
    time

This is the **spectrogram** representation.

------------------------------------------------------------------------

# 8. Peak Detection

Find strong frequency peaks.

Example peaks:

    (t0, f2)
    (t1, f1)
    (t2, f2)

Visualization:

    Spectrogram

            f0 f1 f2 f3
    t0      .  .  X  .
    t1      .  X  .  .
    t2      .  .  X  .

------------------------------------------------------------------------

# 9. Fingerprint Hashing

Shazam pairs peaks to create hashes.

Example pair:

    Peak A (t0,f2)
    Peak B (t1,f1)

Hash format:

    (f1, f2, Δt)

Example:

    (2,1,1)

These hashes are stored in the **song fingerprint database**.

------------------------------------------------------------------------

# Final Data Transformation

    PCM samples
          ↓
    Normalize
          ↓
    Framing
          ↓
    Windowing
          ↓
    FFT
          ↓
    Spectrogram
          ↓
    Peak detection
          ↓
    Fingerprint hashes

This pipeline enables fast audio identification similar to
**Shazam‑style systems**.