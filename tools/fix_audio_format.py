# 把 public/audio 下全部 MP3 统一转码为 44.1kHz MPEG-1 Layer III CBR 128k
# 原因：edge-tts 默认输出 24kHz MPEG-2 LSF MP3，部分浏览器内核不支持在线播放
# 用法：python tools/fix_audio_format.py
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, 'public', 'audio')

def get_ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def normalize(ff, path):
    tmp = path + '.fix.mp3'
    subprocess.run([ff, '-y', '-i', path, '-ar', '44100', '-ac', '1', '-b:a', '128k',
                    '-f', 'mp3', tmp], check=True, capture_output=True)
    os.replace(tmp, path)

def main():
    ff = get_ff()
    files = sorted(f for f in os.listdir(AUDIO_DIR) if f.endswith('.mp3') and not f.endswith('.fix.mp3'))
    ok = fail = 0
    for i, f in enumerate(files, 1):
        p = os.path.join(AUDIO_DIR, f)
        try:
            normalize(ff, p)
            ok += 1
            if i % 20 == 0 or i == len(files):
                print(f'进度 {i}/{len(files)}')
        except Exception as e:
            fail += 1
            print('FAIL', f, e)
    print(f'转码完成：成功 {ok}，失败 {fail}')

if __name__ == '__main__':
    main()
