pub mod audio;
use anyhow::{Context, Result};
fn main() -> Result<()> {
    let (samples, _) = audio::saver::load_wav_file("src/static/audio/Alafasy_128kbps/001/001001.wav")
    .context("Failed to load wav file")?;

    let frames = audio::saver::framing(&samples, 4, 4);
    let hann_frames = audio::saver::hann_window(&frames);

    Ok(())
}
