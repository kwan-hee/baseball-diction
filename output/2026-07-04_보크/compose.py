# 보크 영상 조립: 삽화 Ken Burns + seedance 클립 + 내레이션 + 자막 burn-in → 최종 MP4
import subprocess
import wave  # noqa: F401  (참고: mp3라 ffprobe로 길이 측정)
from pathlib import Path

BASE = Path(r"C:\야구사전\output\2026-07-04_보크")
FFMPEG = (
    r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.EXE"
)
FFPROBE = FFMPEG.replace("ffmpeg.EXE", "ffprobe.EXE")
W, H, FPS = 1280, 720, 30
PAD = 0.8  # 장면 앞뒤 여백 합계(초)

SCENES = {
    "s01": "투수가 공을 던지지도 않았어요. 그런데 심판이 갑자기 주자들을 한 베이스씩 보내줍니다. 타자는 가만히 서 있었는데요. 방금 무슨 일이 벌어진 걸까요? 오늘 야구사전의 주인공, 보크입니다.",
    "s02": "술래잡기에서 술래가 페이크를 쓰면 얄밉잖아요. 야구에서 투수가 주자한테 그러면 안 됩니다. 그게 보크예요. 루에 주자가 있을 때, 투수가 규칙에 어긋나는 동작으로 주자를 속이면, 벌칙으로 모든 주자가 한 베이스씩 공짜로 갑니다.",
    "s03": "종류가 13가지나 되는데, 자주 나오는 건 딱 세 가지예요. 투구 동작을 시작해 놓고 멈추는 것. 1루나 3루로 던지는 척만 하는 것. 그리고 견제할 때 발을 그 베이스 쪽으로 안 내딛는 것. 핵심은 하나입니다. 던질 것처럼 하다가 안 던지면 반칙.",
    "s04": "이 규칙, 생각보다 훨씬 오래됐습니다. 보크라는 단어가 규칙집에 처음 등장한 게 1857년이에요. 조선으로 치면 철종 때입니다. 1898년에는 지금과 같은 규칙으로 자리를 잡았어요. 그 시절 투수들이 하도 교묘하게 주자를 속여서, 도루라는 플레이 자체가 죽어가고 있었거든요. 보크라는 단어 자체가, 멈칫하다, 라는 뜻입니다.",
    "s05": "KBO에서 제일 유명한 장면, 2011년 6월 8일 잠실입니다. LG와 한화, 9회초 2사 3루. 한화 정원석 선수가 그 귀한 홈스틸을 시도합니다. 홈에서 아웃, 경기 끝.",
    "s06": "그런데 느린 화면을 보니, 투수 임찬규 선수가 투구 동작을 시작했다가 멈춘 거예요. 명백한 보크였죠. 하지만 심판 다섯 명 모두 홈스틸에 시선이 쏠려서 투수를 못 봤습니다. 결국 다음 날 KBO는 심판 다섯 명 전원에게 9경기 출장 정지를 내렸습니다. 보크 하나 때문에요.",
    "s07": "1986년에는 장명부 선수가 판정에 화가 나서 일부러 보크를 해버립니다. 고의 볼넷으로 만루를 만들고, 스스로 보크를 범해서 결승점을 내주고 경기를 끝내버린 거예요. KBO 역사상 유일한 고의 보크. 벌금 30만 원을 냈습니다.",
    "s08": "여기서 퀴즈. 주자가 아무도 없을 때 투수가 투구 동작을 하다 멈추면, 보크일까요? 정답은 아니오. 보크는 주자가 있어야만 성립합니다. 주자가 없으면 그냥 반칙투구로 볼 하나만 올라가요. 그리고 견제를 열 번 해도 그 자체는 보크가 아닙니다.",
    "s09": "다만 메이저리그는 2023년부터 한 타석에 견제를 사실상 두 번까지만 허용합니다. 세 번째 견제에서 주자를 못 잡으면, 그게 바로 보크입니다. 규칙이 백이십구 년 만에 또 진화한 거죠.",
    "s10": "정리하면 보크는, 투수야 주자 속이지 마, 이 한 문장입니다. 다음 편에서는 심판이 미리 아웃을 선언해 주는 이상한 규칙, 인필드 플라이를 파봅니다. 궁금하시면 구독 버튼 눌러두세요.",
}
VIDEO_SCENE = "s05"  # seedance 클립 사용 장면


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (rc={r.returncode}):\n{r.stderr[-1500:]}")


def duration_of(path):
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def ts(sec):
    ms = int(round(sec * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_sentences(text):
    parts, cur = [], ""
    for ch in text:
        cur += ch
        if ch in ".?!":
            if cur.strip():
                parts.append(cur.strip())
            cur = ""
    if cur.strip():
        parts.append(cur.strip())
    return parts


scene_dir = BASE / "scenes"
scene_dir.mkdir(exist_ok=True)

srt_lines, cue_idx, t_cursor = [], 1, 0.0
scene_files = []

for i, (sid, text) in enumerate(SCENES.items()):
    audio = BASE / "audio" / f"{sid}.mp3"
    adur = duration_of(audio)
    sdur = adur + PAD
    out = scene_dir / f"{sid}.mp4"
    frames = int(sdur * FPS)

    if out.exists() and out.stat().st_size > 0:
        scene_files.append(out)
        print(f"{sid}: cached ({sdur:.1f}s)")
        sentences = split_sentences(text)
        total_chars = sum(len(s) for s in sentences)
        cue_t = t_cursor + 0.4
        for s in sentences:
            cdur = adur * len(s) / total_chars
            srt_lines.append(f"{cue_idx}\n{ts(cue_t)} --> {ts(min(cue_t + cdur, t_cursor + sdur))}\n{s}\n")
            cue_idx += 1
            cue_t += cdur
        t_cursor += sdur
        continue

    if sid == VIDEO_SCENE:
        clip = BASE / "clips" / "s05_seedance.mp4"
        if not clip.exists():
            raise SystemExit(f"STOP: seedance clip not ready: {clip}")
        # 클립을 장면 길이에 맞춤: 부족하면 마지막 프레임 유지(tpad clone)
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"fps={FPS},tpad=stop_mode=clone:stop_duration=30,trim=duration={sdur:.3f},setpts=PTS-STARTPTS"
        )
        cmd = [FFMPEG, "-y", "-i", str(clip), "-i", str(audio),
               "-filter_complex",
               f"[0:v]{vf}[v];[1:a]adelay=400|400,apad,atrim=duration={sdur:.3f}[a]",
               "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-threads", "2", str(out)]
    else:
        img = BASE / "images" / f"{sid}.png"
        # Ken Burns: 짝수 장면 줌인, 홀수 장면 줌아웃
        if i % 2 == 0:
            zexpr = f"min(1+0.10*on/{frames},1.10)"
        else:
            zexpr = f"max(1.10-0.10*on/{frames},1.0)"
        vf = (
            f"scale=1920:1080,zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
            f":d={frames}:s={W}x{H}:fps={FPS}"
        )
        # 이미지는 단일 프레임 입력 — zoompan d={frames}가 전체 길이를 만든다 (-loop 사용 금지: d가 중복 적용됨)
        cmd = [FFMPEG, "-y", "-i", str(img), "-i", str(audio),
               "-filter_complex",
               f"[0:v]{vf}[v];[1:a]adelay=400|400,apad,atrim=duration={sdur:.3f}[a]",
               "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-threads", "2", str(out)]
    run(cmd)
    scene_files.append(out)
    print(f"{sid}: {sdur:.1f}s")

    # 자막 큐: 문장 단위, 발화 구간(0.4s 오프셋 ~ 오디오 끝)에 글자수 비례 배분
    sentences = split_sentences(text)
    total_chars = sum(len(s) for s in sentences)
    cue_t = t_cursor + 0.4
    for s in sentences:
        cdur = adur * len(s) / total_chars
        srt_lines.append(f"{cue_idx}\n{ts(cue_t)} --> {ts(min(cue_t + cdur, t_cursor + sdur))}\n{s}\n")
        cue_idx += 1
        cue_t += cdur
    t_cursor += sdur

srt_path = BASE / "보크.srt"
srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
print(f"SRT: {srt_path} ({cue_idx - 1} cues)")

# concat
concat_txt = BASE / "concat.txt"
concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in scene_files), encoding="utf-8")
joined = BASE / "보크_nosub.mp4"
run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
     "-c", "copy", str(joined)])

# 자막 burn-in (경로 이스케이프 문제 회피: cwd를 BASE로)
final = BASE / "2026-07-04_보크_final.mp4"
r = subprocess.run(
    [FFMPEG, "-y", "-i", "보크_nosub.mp4",
     "-vf", "subtitles=보크.srt:force_style='FontName=Malgun Gothic,FontSize=18,Outline=2,MarginV=40'",
     "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
     "-c:a", "copy", "-threads", "2", final.name],
    capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(BASE),
)
if r.returncode != 0:
    raise RuntimeError(f"subtitle burn failed:\n{r.stderr[-1500:]}")
print(f"FINAL: {final} ({final.stat().st_size:,} bytes, total {t_cursor:.1f}s)")
