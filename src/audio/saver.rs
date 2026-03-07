use hound;
use anyhow::{Context, Result};

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