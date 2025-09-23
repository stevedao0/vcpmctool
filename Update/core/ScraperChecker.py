# -*- coding: utf-8 -*-
import os
import re
import pandas as pd
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import yt_dlp
import multiprocessing
from typing import Callable, Optional, Union, List, Tuple

TOPIC_OVERRIDES = {
    "UCdW9arh-ckZrMW_wHu4xPYA": ("UCNqz53FCc3mUg5NyzHxsXGQ", "Quang Lê Official"),
}

class Utils:
    @staticmethod
    def format_duration(seconds):
        if seconds is None:
            return "N/A"
        try:
            sec = int(float(seconds)); h, rem = divmod(sec, 3600); m, s = divmod(rem, 60)
            return f"{h:02}:{m:02}:{s:02}"
        except Exception:
            return "N/A"

    @staticmethod
    def format_date(upload_date):
        if not upload_date:
            return "N/A"
        try:
            dt = datetime.strptime(str(upload_date), "%Y%m%d"); return dt.strftime("%d/%m/%Y")
        except Exception:
            try:
                if isinstance(upload_date, datetime): return upload_date.strftime("%d/%m/%Y")
                dt = datetime.fromisoformat(str(upload_date)); return dt.strftime("%d/%m/%Y")
            except Exception:
                return "N/A"

    @staticmethod
    def sanitize_filename(name: str) -> str:
        return re.sub(r'[\\/*?:\"<>|]', "", str(name)).strip()

    @staticmethod
    def extract_channel_id(info: dict) -> str:
        for key in ("owner_channel_id", "channel_id", "uploader_id"):
            cid = info.get(key)
            if cid and isinstance(cid, str) and cid.startswith("UC"):
                return cid
        for key in ("uploader_url", "channel_url"):
            url = info.get(key, "")
            m = re.search(r"/channel/(UC[0-9A-Za-z_-]+)", url)
            if m: return m.group(1)
        return "N/A"

def _normalize_input(channel: str) -> str:
    c = channel.strip()
    if c.startswith("http"):
        for pat, prefix in [(r"/channel/([^/?&]+)", ""),
                            (r"/c/([^/?&]+)", ""),
                            (r"/user/([^/?&]+)", ""),
                            (r"/@([^/?&]+)", "@")]:
            m = re.search(pat, c)
            if m: return prefix + m.group(1)
    return c

def get_video_info(video_id: str) -> dict:
    opts = {'ignoreerrors': False, 'skip_download': True, 'nocheckcertificate': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except Exception as e:
        return {"error": str(e)}

def get_channel_info(channel_input: str) -> Tuple[str, list]:
    cid = _normalize_input(channel_input); entries, title = [], cid
    ydl_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True, 'ignoreerrors': True, 'nocheckcertificate': True}
    if cid.startswith("UC"):
        pl = "UU" + cid[2:]
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(f"https://www.youtube.com/playlist?list={pl}", download=False)
            title = data.get('uploader') or data.get('title') or title
            entries = data.get('entries') or []
        except Exception:
            entries = []
    if not entries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data2 = ydl.extract_info(f"https://www.youtube.com/channel/{cid}/videos", download=False)
            title = title if title != cid else data2.get('uploader') or data2.get('title') or title
            entries = data2.get('entries') or []
        except Exception:
            entries = []
    return title, entries

def get_shorts_info(channel_input: str) -> Tuple[str, list]:
    cid = _normalize_input(channel_input)
    ydl_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True, 'ignoreerrors': True, 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(f"https://www.youtube.com/channel/{cid}/shorts", download=False)
        title = data.get('uploader') or data.get('title') or cid
        entries = data.get('entries') or []
        return title, entries
    except Exception:
        return cid, []

def _scraper_worker(entry: dict, idx: int, title: str, cid_input: str, ftype: str) -> dict:
    vid = entry.get('id')
    if not vid: return None
    info = get_video_info(vid)
    if not info or 'error' in info:
        return {'Số thứ tự': idx,'Tên Kênh': title,'ID Kênh': cid_input,'Tên Video': 'N/A',
                'ID Video': vid,'Link Video': f'https://www.youtube.com/watch?v={vid}',
                'Thời gian': 'N/A','Ngày xuất bản': 'N/A','Lượt xem': 'N/A',
                'Tình trạng': info.get('error', 'N/A') if info else 'N/A','Hình thức': ftype}
    cid_real = Utils.extract_channel_id(info); name_real = info.get('uploader', title)
    if cid_real in TOPIC_OVERRIDES: cid_real, name_real = TOPIC_OVERRIDES[cid_real]
    return {'Số thứ tự': idx,'Tên Kênh': name_real,'ID Kênh': cid_real,'Tên Video': info.get('title', 'N/A'),
            'ID Video': vid,'Link Video': info.get('webpage_url', f'https://www.youtube.com/watch?v={vid}'),
            'Thời gian': Utils.format_duration(info.get('duration')),
            'Ngày xuất bản': Utils.format_date(info.get('upload_date')),
            'Lượt xem': info.get('view_count', 'N/A'),'Tình trạng': 'OK','Hình thức': ftype}

def run_scraper(channel_input: str, out_folder: str,
                log_func: Optional[Callable]=None,
                progress_callback: Optional[Callable[[int, int], None]]=None,
                stop_event: Optional[object]=None) -> Optional[str]:
    s_title, s_items = get_shorts_info(channel_input)
    u_title, u_items = get_channel_info(channel_input)
    if not (s_items or u_items):
        log_func and log_func('Không thể lấy video.', prefix='Scraper'); return None
    title = s_title if s_items else u_title
    args, idx = [], 1
    for e in s_items: args.append((e, idx, title, channel_input, 'Shorts')); idx += 1
    for e in u_items: args.append((e, idx, title, channel_input, 'Video')); idx += 1
    total = len(args); log_func and log_func(f'Tổng số video: {total}', prefix='Scraper')
    if progress_callback: progress_callback(0, total)
    results = []
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = {executor.submit(_scraper_worker, *a): a for a in args}
        done = 0
        for f in as_completed(futures):
            if stop_event and stop_event.is_set():
                executor.shutdown(cancel_futures=True); return None
            res = f.result()
            if res: results.append(res)
            done += 1
            if progress_callback: progress_callback(done, total)
            log_func and log_func(f'Đã xử lý {done}/{total}', prefix='Scraper')
    df = pd.DataFrame(results)
    if df.empty: return None
    df['p'] = df['Hình thức'].apply(lambda x: 0 if x == 'Shorts' else 1)
    df = df.sort_values(['ID Video','p']).drop_duplicates('ID Video').drop('p', axis=1)
    safe = Utils.sanitize_filename(title); os.makedirs(out_folder, exist_ok=True)
    path = os.path.join(out_folder, f"{safe}_Videos.xlsx"); df.to_excel(path, index=False)
    log_func and log_func(f'Xong: {path}', prefix='Scraper'); return path

def read_input_file(fp: str) -> Optional[pd.DataFrame]:
    ext = os.path.splitext(fp)[1].lower()
    if ext in ['.xls','.xlsx']: return pd.read_excel(fp)
    if ext == '.csv': return pd.read_csv(fp)
    return None

def _checker_worker(item: Tuple[int, str]) -> dict:
    idx, vid = item; info = get_video_info(vid)
    status = 'OK' if info and 'error' not in info else f"Error: {info.get('error','N/A') if info else 'N/A'}"
    return {'index': idx,'ID Kênh': Utils.extract_channel_id(info) if info and 'error' not in info else 'N/A',
            'Tên Kênh': info.get('uploader','N/A') if info else 'N/A','ID Video': vid,
            'Tên Video': info.get('title','N/A') if info else 'N/A',
            'Thời Lượng': Utils.format_duration(info.get('duration')) if info else 'N/A',
            'Ngày Xuất Bản': Utils.format_date(info.get('upload_date')) if info else 'N/A',
            'Lượt View': info.get('view_count','N/A') if info else 'N/A',
            'Tình trạng': status,'Hình thức': 'Shorts' if info and info.get('duration',0)<=60 else 'Video'}

def run_checker(fp: str, max_workers: int=4,
                progress_callback: Optional[Callable[[int, int], None]]=None,
                log_func: Optional[Callable]=None,
                stop_event: Optional[object]=None) -> Optional[str]:
    df_in = read_input_file(fp)
    if df_in is None or 'ID Video' not in df_in.columns:
        log_func and log_func("File không hợp lệ hoặc thiếu cột 'ID Video'.", prefix='Checker'); return None
    items = list(df_in['ID Video'].items())
    total = len(items); results = []
    if progress_callback: progress_callback(0, total)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_checker_worker, it): it for it in items}
        done = 0
        for f in as_completed(futures):
            if stop_event and stop_event.is_set():
                executor.shutdown(cancel_futures=True); return None
            res = f.result(); results.append(res); done += 1
            if progress_callback: progress_callback(done, total)
            log_func and log_func(f'Checker {done}/{total}', prefix='Checker')
    df_out = pd.DataFrame(results); df_out.insert(0, 'Số thứ tự', range(1, len(df_out)+1))
    cols = ['Số thứ tự','ID Kênh','Tên Kênh','ID Video','Tên Video','Thời Lượng','Ngày Xuất Bản','Lượt View','Tình trạng','Hình thức']
    df_out = df_out[cols]; out_path = os.path.splitext(fp)[0] + '_checked.xlsx'
    df_out.to_excel(out_path, index=False); return out_path

def _build_ydl_opts_for_download(
    out_folder: str,
    quality: str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
    audio_only: bool = False,
    preferred_audio_codec: str = 'mp3',
    preferred_audio_quality: str = '192',
    concurrent_frags: int = 8,
    merge_to: str = 'mp4',
    cookies_file: Optional[str] = None,
    proxy: Optional[str] = None,
    write_thumbnail: bool = False,
    add_metadata: bool = True,
    embed_thumbnail: bool = False,
    download_archive_path: Optional[str] = None,
    enable_aria2: bool = False,
    rate_limit: Optional[int] = None,
    throttled_rate: Optional[int] = None,
    http_chunk_size: Optional[int] = 10_485_760,
    retries: int = 10,
    fragment_retries: int = 10,
    sleep_interval: Optional[float] = None,
    max_sleep_interval: Optional[float] = None
) -> dict:
    os.makedirs(out_folder, exist_ok=True)
    outtmpl = os.path.join(out_folder, '%(uploader)s - %(title)s [%(id)s].%(ext)s')
    ydl_opts = {
        'outtmpl': outtmpl,'quiet': True,'no_warnings': True,'restrictfilenames': False,'windowsfilenames': True,
        'noprogress': True,'format': 'bestaudio/best' if audio_only else quality,
        'concurrent_fragment_downloads': concurrent_frags,'merge_output_format': None if audio_only else merge_to,
        'postprocessors': [],'continuedl': True,'retries': retries,'fragment_retries': fragment_retries,'nocheckcertificate': True,
        'ffmpeg_location': os.environ.get('FFMPEG_LOCATION'),
    }
    if proxy: ydl_opts['proxy'] = proxy
    if cookies_file and os.path.exists(cookies_file): ydl_opts['cookiefile'] = cookies_file
    if download_archive_path: ydl_opts['download_archive'] = download_archive_path
    if rate_limit: ydl_opts['ratelimit'] = rate_limit
    if throttled_rate: ydl_opts['throttled_rate'] = throttled_rate
    if http_chunk_size: ydl_opts['http_chunk_size'] = http_chunk_size
    if sleep_interval: ydl_opts['sleep_interval'] = sleep_interval
    if max_sleep_interval: ydl_opts['max_sleep_interval'] = max_sleep_interval
    if enable_aria2:
        ydl_opts['external_downloader'] = 'aria2c'
        ydl_opts['external_downloader_args'] = ['-x16', '-k1M', '--file-allocation=none']
    if add_metadata: ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})
    if write_thumbnail: ydl_opts['writethumbnail'] = True
    if embed_thumbnail: ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
    if audio_only:
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio','preferredcodec': preferred_audio_codec,'preferredquality': preferred_audio_quality
        })
    return ydl_opts

def download_video(
    video: str, out_folder: str = 'downloads',
    quality: str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
    audio_only: bool = False, concurrent_frags: int = 8,
    cookies_file: Optional[str] = None, proxy: Optional[str] = None,
    write_thumbnail: bool = False, embed_thumbnail: bool = False,
    add_metadata: bool = True, download_archive_path: Optional[str] = None,
    enable_aria2: bool = False, rate_limit: Optional[int] = None,
    throttled_rate: Optional[int] = None, http_chunk_size: Optional[int] = 10_485_760,
    retries: int = 10, fragment_retries: int = 10,
    sleep_interval: Optional[float] = None, max_sleep_interval: Optional[float] = None,
    progress_callback: Optional[Callable[[dict], None]] = None,
    log_func: Optional[Callable[[str], None]] = None, stop_event: Optional[object] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    if not video: return False, None, 'Thiếu video ID/URL'
    url = f'https://www.youtube.com/watch?v={video}' if re.match(r'^[0-9A-Za-z_-]{11}$', video) else video
    ydl_opts = _build_ydl_opts_for_download(
        out_folder=out_folder, quality=quality, audio_only=audio_only,
        concurrent_frags=concurrent_frags, cookies_file=cookies_file, proxy=proxy,
        write_thumbnail=write_thumbnail, embed_thumbnail=embed_thumbnail, add_metadata=add_metadata,
        download_archive_path=download_archive_path, enable_aria2=enable_aria2,
        rate_limit=rate_limit, throttled_rate=throttled_rate, http_chunk_size=http_chunk_size,
        retries=retries, fragment_retries=fragment_retries, sleep_interval=sleep_interval, max_sleep_interval=max_sleep_interval
    )

    def _hook(d):
        if stop_event and hasattr(stop_event, "is_set") and stop_event.is_set():
            raise yt_dlp.utils.DownloadError("Cancelled by user")
        if progress_callback:
            payload = {'phase': d.get('status')}
            if d.get('status') == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes') or 0
                percent = (downloaded / total) if total else None
                payload.update({'percent': percent,'downloaded': downloaded,'total': total,
                                'speed': d.get('speed'),'eta': d.get('eta'),'filename': d.get('filename')})
            elif d.get('status') in ('finished', 'postprocessing'):
                payload.update({'filename': d.get('filename')})
            try: progress_callback(payload)
            except Exception: pass
        if log_func and d.get('status') == 'downloading':
            info = []
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total and d.get('downloaded_bytes'):
                try:
                    p = d['downloaded_bytes'] / float(total); info.append(f"{p*100:.1f}%")
                except Exception: pass
            if d.get('speed'): info.append(f"{d['speed']/1024/1024:.2f} MB/s")
            if d.get('eta'): info.append(f"ETA {d['eta']}s")
            if info: log_func('[Downloader] ' + ' | '.join(info))

    ydl_opts['progress_hooks'] = [_hook]
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            out_path = None
            if info:
                if '_filename' in info: out_path = info.get('_filename')
                else:
                    ext = info.get('ext') or ('mp3' if audio_only else 'mp4')
                    out_path = os.path.join(
                        out_folder,
                        f"{Utils.sanitize_filename(info.get('uploader',''))} - "
                        f"{Utils.sanitize_filename(info.get('title',''))} [{info.get('id','')}].{ext}"
                    )
            return True, out_path, None
    except Exception as e:
        if log_func: log_func(f'[Downloader] Lỗi: {e}')
        return False, None, str(e)

def _expand_video_ids_from_url(url: str) -> List[str]:
    flat_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True, 'ignoreerrors': True, 'nocheckcertificate': True}
    ids: List[str] = []
    try:
        with yt_dlp.YoutubeDL(flat_opts) as ydl:
            data = ydl.extract_info(url, download=False)
        if not data: return ids
        entries = data.get('entries') or []
        if entries:
            for e in entries:
                if not e: continue
                vid = e.get('id')
                if vid and re.match(r'^[0-9A-Za-z_-]{11}$', vid): ids.append(vid)
        else:
            vid = data.get('id')
            if vid and re.match(r'^[0-9A-Za-z_-]{11}$', vid): ids.append(vid)
    except Exception:
        pass
    return ids

def run_downloader(
    input_value: Union[str, List[str]], out_folder: str,
    quality: str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
    audio_only: bool = False, max_workers: int = 2, concurrent_frags: int = 8,
    cookies_file: Optional[str] = None, proxy: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    detail_callback: Optional[Callable[[dict], None]] = None,
    log_func: Optional[Callable[[str, str], None]] = None,
    stop_event: Optional[object] = None, enable_aria2: bool = False, use_archive: bool = True
) -> Optional[str]:
    os.makedirs(out_folder, exist_ok=True)
    archive_path = os.path.join(out_folder, 'download_archive.txt') if use_archive else None

    def _log(msg: str):
        if log_func:
            try: log_func(msg, prefix='[Downloader]')
            except TypeError: log_func(f'[Downloader] {msg}')

    id_list: List[str] = []
    if isinstance(input_value, list):
        id_list = [str(x).strip() for x in input_value if str(x).strip()]
    elif isinstance(input_value, str) and os.path.isfile(input_value):
        df = read_input_file(input_value)
        if df is None or 'ID Video' not in df.columns:
            _log('File không hợp lệ hoặc thiếu cột ID Video'); return None
        id_list = [str(x).strip() for x in df['ID Video'].tolist() if str(x).strip()]
    elif isinstance(input_value, str):
        s = input_value.strip()
        if s.startswith('http'):
            expanded = _expand_video_ids_from_url(s); id_list = expanded if expanded else [s]
        else: id_list = [s]
    else:
        _log('Input không hợp lệ'); return None

    total = len(id_list)
    if total == 0:
        _log('Không có mục nào để tải'); return None
    if progress_callback: progress_callback(0, total)

    results, done_counter = [], 0

    def _task(vid):
        return download_video(
            vid, out_folder=out_folder, quality=quality, audio_only=audio_only,
            concurrent_frags=concurrent_frags, cookies_file=cookies_file, proxy=proxy,
            progress_callback=detail_callback, log_func=_log, stop_event=stop_event,
            download_archive_path=archive_path, enable_aria2=enable_aria2
        )

    if total == 1 or max_workers <= 1:
        ok, path, err = _task(id_list[0]); done_counter += 1
        if progress_callback: progress_callback(done_counter, total)
        results.append({'ID/URL': id_list[0], 'Trạng thái': 'OK' if ok else f'Error: {err}', 'Đường dẫn': path})
    else:
        workers = max(1, min(max_workers, 4))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(_task, vid): vid for vid in id_list}
            for fut in as_completed(futures):
                vid = futures[fut]
                ok, path, err = fut.result(); done_counter += 1
                if progress_callback: progress_callback(done_counter, total)
                results.append({'ID/URL': vid, 'Trạng thái': 'OK' if ok else f'Error: {err}', 'Đường dẫn': path})

    if total == 1: return None
    try:
        df_out = pd.DataFrame(results); df_out.insert(0, 'Số thứ tự', range(1, len(df_out)+1))
        out_report = os.path.join(out_folder, 'Download_Report.xlsx'); df_out.to_excel(out_report, index=False)
        _log(f'Đã lưu báo cáo: {out_report}'); return out_report
    except Exception as e:
        _log(f'Lỗi lưu báo cáo: {e}'); return None
