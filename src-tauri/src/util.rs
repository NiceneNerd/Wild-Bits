use crate::{AppError, Result};
use std::{io::{BufWriter, Cursor}, path::Path};
use yaz0::*;

pub(crate) fn decompress<B: AsRef<[u8]>>(data: B) -> Result<Vec<u8>> {
    let data = data.as_ref();
    let mut decomp =
        Yaz0Archive::new(Cursor::new(&data)).map_err(|_| AppError::from("Failed to decompress"))?;
    Ok(decomp
        .decompress()
        .map_err(|_| AppError::from("Failed to decompress"))?)
}

pub(crate) fn compress<B: AsRef<[u8]>>(data: B) -> Result<Vec<u8>> {
    let mut compressed: Vec<u8> = Vec::with_capacity(data.as_ref().len());
    let mut buffer = BufWriter::new(&mut compressed);
    let writer = Yaz0Writer::new(&mut buffer);
    writer
        .compress_and_write(data.as_ref(), CompressionLevel::Lookahead { quality: 6 })
        .map_err(|_| AppError::from("Failed to compress"))?;
    drop(buffer);
    Ok(compressed)
}

pub(crate) fn should_compress<P: AsRef<Path>>(file: P) -> bool {
    if let Some(ext) = file.as_ref().extension() {
        let ext = ext.to_str().unwrap();
        ext.starts_with('s') && ext != "sarc"
    } else {
        false
    }
}
