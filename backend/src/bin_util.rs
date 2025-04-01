use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

use crate::net_util::get_vod_meta;

pub async fn download_videos_from_csv<P, C, F>(
    csv_path: &str,
    on_progress: P,
    on_completion: C,
    on_fail: F,
) -> anyhow::Result<()>
where
    P: Fn(&str, JSON) + Send + 'static + Clone,
    C: Fn(&str) + Send + 'static + Clone,
    F: Fn(&str, anyhow::Error) + Send + 'static + Clone,
{
    let file = File::open(csv_path)?;
    let reader = io::BufReader::new(file);

    for line in reader.lines() {
        let url = line?;
        let vod = get_vod_meta(&url).await?;
        start_download(&vod, false, on_progress.clone(), on_completion.clone(), on_fail.clone()).await?;
    }

    Ok(())
}
