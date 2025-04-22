import yt_dlp
import requests
import os

def get_vod_stream_url(vod_id):
    url = f"https://dce-frontoffice.imggaming.com/api/v3/stream/vod/{vod_id}"
    response = requests.get(url)
    response.raise_for_status()
    json_response = response.json()
    return json_response['hls'][0]['url']

def generate_vod_download_config(config, vod, is_restart):
    vid_quality = config['vid_quality']
    aud_quality = config['aud_quality']
    resolution = config['resolution']
    merge_ext = config['merge_ext']
    dl_path = config['dl_path']
    number_files = config['number_files']
    cur_number = config['cur_number']
    throttle = config['throttle']
    dl_rate = config['dl_rate']
    multi_frag = config['multi_frag']
    concur_frags = config['concur_frags']
    cus_format = config['cus_format']
    format_id = config['format_id']
    metadata = config['metadata']
    dl_args = config['dl_args']

    title = vod['title']
    hls = vod['hls']

    final_title = title if is_restart or not number_files else f"{cur_number}. {title}"
    default_format = f"{vid_quality}[height={resolution}]+{aud_quality}/{vid_quality}*[height={resolution}]"
    dl_path = os.path.join(dl_path, f"{final_title}.%(ext)s")
    bin_path = os.path.join(os.getcwd(), "bin")
    concur_frags_string = str(concur_frags)

    arg_setup = [
        "--format", format_id if cus_format else default_format,
        "--merge-output-format", merge_ext,
        "--output", dl_path,
        "--progress-template", '{"status": "%(progress.status)s", "total_size": %(progress.total_bytes_estimate)d, "dl_size": %(progress.downloaded_bytes)d, "size": "%(progress._total_bytes_estimate_str)s", "speed": "%(progress._speed_str)s", "eta": "%(progress._eta_str)s", "vcodec": "%(info.vcodec)s"}',
        "--ffmpeg-location", bin_path
    ]

    if throttle:
        arg_setup.extend(["--limit-rate", dl_rate])
    if multi_frag:
        arg_setup.extend(["--concurrent-fragments", concur_frags_string])
    if metadata:
        arg_setup.append("--add-metadata")

    arg_setup.extend(dl_args)
    arg_setup.append(hls)

    return final_title, arg_setup

def download_video(vod, config, is_restart=False):
    final_title, dl_config = generate_vod_download_config(config, vod, is_restart)
    ydl_opts = {
        'progress_hooks': [lambda d: print(f"Status: {d['status']}, Downloaded: {d['downloaded_bytes']} bytes")]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(dl_config)
    print(f"Download completed: {final_title}")

if __name__ == "__main__":
    config = {
        "vid_quality": "bestvideo",
        "aud_quality": "bestaudio",
        "resolution": "720",
        "merge_ext": "mp4",
        "dl_path": "./downloads",
        "number_files": True,
        "cur_number": 1,
        "throttle": False,
        "dl_rate": "100K",
        "multi_frag": True,
        "concur_frags": 64,
        "cus_format": False,
        "format_id": "",
        "metadata": False,
        "dl_args": ["--no-warnings", "--no-mtime", "--output-na-placeholder", "\"\"", "--no-cache-dir", "--ignore-config", "--no-check-certificate"]
    }
    vod = {
        "title": "Sample Video",
        "hls": get_vod_stream_url(12345)
    }
    download_video(vod, config)
