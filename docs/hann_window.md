# Why hanning window is needed in audio processing
FFT assumes that a finite signal segment repeats periodically. But real audio signals are not periodic within that segment. 
Spectral leakage happens because the FFT “wraps” the signal, and if the endpoints don’t match, it creates an artificial jump.

That’s exactly why the Hann window is used:
* It reduces the edge discontinuity
* reduces leakage

By touching zero at the endpoints of Hann window, it removes any discontinuities.

There are also other windowing technique like Hamming window, blackman window