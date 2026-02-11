import requests, time, re
import os, sys


# 字节bytes转化K\M\G
def format_size(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fG" % (G)
        else:
            return "%.2fM" % (M)
    else:
        return "%.2fK" % (kb)


def parse_video_input(raw_input):
    raw_input = raw_input.strip()
    page_match = re.search(r'[?&]p=(\d+)', raw_input)
    page = page_match.group(1) if page_match else None
    bvid_match = re.search(r'BV[0-9A-Za-z]+', raw_input)
    if bvid_match:
        return "bvid", bvid_match.group(0), page

    aid_match = re.search(r'av(\d+)', raw_input, re.IGNORECASE)
    if aid_match:
        return "aid", aid_match.group(1), page

    if raw_input.isdigit():
        return "aid", raw_input, page

    raise ValueError("无法解析视频编号，请输入BV号、av号或视频链接")


def build_video_urls(id_type, video_id):
    api_url = f"https://api.bilibili.com/x/web-interface/view?{id_type}={video_id}"
    if id_type == "aid":
        referer_url = f"https://www.bilibili.com/video/av{video_id}"
    else:
        referer_url = f"https://www.bilibili.com/video/{video_id}"
    return api_url, referer_url


def download_with_resume(url, filepath, headers, max_retries=5):
    """Download a large file with resume support on failure."""
    for attempt in range(max_retries):
        downloaded = 0
        if os.path.exists(filepath):
            downloaded = os.path.getsize(filepath)

        dl_headers = dict(headers)
        if downloaded > 0:
            dl_headers['Range'] = f'bytes={downloaded}-'
            print(f'  [续传] 从 {format_size(downloaded)} 处继续下载 (第{attempt+1}次)')

        try:
            resp = requests.get(url, headers=dl_headers, stream=True, timeout=60)

            # If server returns 416, file is already complete
            if resp.status_code == 416:
                print('  [完成] 文件已完整下载')
                return True

            if downloaded > 0 and resp.status_code == 206:
                content_range = resp.headers.get('content-range', '')
                total_size = int(content_range.split('/')[-1]) if '/' in content_range else 0
                mode = 'ab'
            else:
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0
                mode = 'wb'

            start_time = time.time()
            with open(filepath, mode) as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        if total_size > 0:
                            pct = downloaded / total_size * 100
                            eta = (total_size - downloaded) / speed if speed > 0 else 0
                            eta_str = f"{int(eta//60)}m{int(eta%60)}s"
                            print(f'\r  {pct:.1f}% {format_size(downloaded)}/{format_size(total_size)} @ {format_size(speed)}/s ETA {eta_str}   ', end='', flush=True)
                        else:
                            print(f'\r  {format_size(downloaded)} @ {format_size(speed)}/s   ', end='', flush=True)
            print()
            return True

        except (requests.exceptions.RequestException, IOError) as e:
            print(f'\n  [错误] 下载中断: {e}')
            if attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f'  [重试] {wait}秒后重试...')
                time.sleep(wait)
            else:
                print(f'  [失败] 达到最大重试次数 ({max_retries})')
                return False


def download_audio(avnum=None) -> str:
    """Download audio-only from a Bilibili video using DASH streams."""
    print('*' * 30 + 'B站音频下载' + '*' * 30)
    start = input('请输入B站av号/BV号或视频链接:') if not avnum else avnum
    id_type, video_id, page_hint = parse_video_input(start)
    api_url, referer_url = build_video_urls(id_type, video_id)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': referer_url,
        'Origin': 'https://www.bilibili.com',
    }

    # 获取视频元数据
    html = requests.get(api_url, headers=headers).json()
    data = html['data']
    video_title = data["title"].replace(" ", "_")
    duration = data.get('duration', 0)
    print(f'[视频标题]: {video_title}')
    print(f'[视频时长]: {duration//3600}h {(duration%3600)//60}m {duration%60}s')

    cid_list = []
    if page_hint:
        cid_list.append(data['pages'][int(page_hint) - 1])
    else:
        cid_list = data['pages']

    os.makedirs("audio/conv", exist_ok=True)

    for item in cid_list:
        cid = str(item['cid'])
        title = item['part']
        if not title:
            title = video_title
        title = re.sub(r'[\/\\:*?"<>|]', '', title)
        print(f'[下载音频]: {title} (cid: {cid})')

        # Use DASH format (fnval=16) to get separate audio streams
        if id_type == 'bvid':
            playurl_api = f'https://api.bilibili.com/x/player/playurl?bvid={video_id}&cid={cid}&qn=16&fnval=16&fourk=0'
        else:
            playurl_api = f'https://api.bilibili.com/x/player/playurl?avid={video_id}&cid={cid}&qn=16&fnval=16&fourk=0'

        play_data = requests.get(playurl_api, headers=headers).json()
        dash = play_data['data'].get('dash')
        if not dash or not dash.get('audio'):
            raise RuntimeError(f'无法获取音频流: {play_data["data"].get("message", "unknown")}')

        # Pick the best quality audio stream (highest bandwidth)
        audio_streams = sorted(dash['audio'], key=lambda x: x['bandwidth'], reverse=True)
        audio_stream = audio_streams[0]
        audio_url = audio_stream['baseUrl']
        backup_urls = audio_stream.get('backupUrl', [])
        print(f'  [音频流]: codec={audio_stream["codecs"]} bitrate={audio_stream["bandwidth"]//1000}kbps')

        filepath = f"audio/conv/{title}.m4s"

        # Try main URL, then backups
        urls_to_try = [audio_url] + backup_urls
        success = False
        for url in urls_to_try:
            if download_with_resume(url, filepath, headers):
                success = True
                break
            print(f'  [切换] 尝试备用地址...')

        if not success:
            raise RuntimeError(f'所有下载地址均失败: {title}')

        # Convert m4s to mp3 using ffmpeg
        mp3_path = f"audio/conv/{title}.mp3"
        print(f'  [转换] m4s -> mp3 ...')
        import subprocess
        subprocess.run(
            ['ffmpeg', '-y', '-i', filepath, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', mp3_path],
            capture_output=True, check=True
        )
        os.remove(filepath)
        print(f'  [完成] {mp3_path}')

    print('[全部完成]')
    return title


if __name__ == "__main__":
    download_audio()
