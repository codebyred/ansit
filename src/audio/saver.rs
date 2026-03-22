use hound;
use anyhow::{Context, Result};
use std::f32::consts::PI;

pub fn load_wav_file(path: &str) -> Result<(Vec<f32>, u32)> {
    let mut wavfile = hound::WavReader::open(path)   
        .with_context(|| format!("Failed to open WAV file: {}", path))?;
    
    let wavfile_spec = wavfile.spec();
    let sample_rate = wavfile_spec.sample_rate;

    let samples = wavfile.samples::<i32>()
        .map(|s| Ok(s? as f32/ i16::MAX as f32))
        .collect::<anyhow::Result<Vec<f32>>>()?;

    Ok((samples, sample_rate))
}

pub fn framing(samples:&[f32], frame_size: usize, hop_size: usize) -> Vec<&[f32]> {
    let mut frames = Vec::new();
    let mut start = 0;

    while start+frame_size as usize <= samples.len() {
        frames.push(&samples[start..start+frame_size]);
        start += hop_size;
    }

    println!("{:?}", frames);

    frames
}

pub fn hann_window(frames: &[&[f32]]) -> Vec<Vec<f32>> {
    let mut hann_frames = Vec::new();

    for &frame in frames {
        if frame.len() <= 1 {
            hann_frames.push(frame.to_vec());
            continue;
        }

        let mut hann_frame = Vec::with_capacity(frame.len());
        let n = frame.len() as f32;
        let factor = 2.0 * PI / (n - 1.0);

        for (i, &sample) in frame.iter().enumerate() {
            let w = 0.5 * (1.0 - (factor * i as f32).cos());
            hann_frame.push(sample * w);
        }

        hann_frames.push(hann_frame);
    }

    hann_frames
}