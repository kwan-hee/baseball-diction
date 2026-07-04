# 인필드 플라이 영상 조립: 삽화 Ken Burns + seedance 클립 + 내레이션 + 자막 + BGM → 최종 MP4
import subprocess
from pathlib import Path

BASE = Path(r"C:\야구사전\output\2026-07-04_인필드플라이")
FFMPEG = (
    r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.1-full_build\bin\ffmpeg.EXE"
)
FFPROBE = FFMPEG.replace("ffmpeg.EXE", "ffprobe.EXE")
W, H, FPS = 1280, 720, 30
PAD = 0.8
BGM = BASE / "bgm" / "The Diamond.mp3"
BGM_VOLUME = 0.15
FINAL_FADE = 2.0

SCENES = {
    "s01": "공이 아직 하늘에 떠 있는데, 심판이 벌써 아웃을 외칩니다. 잡지도 않은 공인데요. 이상하죠? 그런데 작년 한국시리즈에서는, 이 선언이 안 나와서 난리가 났습니다. 오늘의 야구사전, 인필드 플라이입니다.",
    "s02": "인필드 플라이는 한마디로 심판이 미리 들어주는 보험입니다. 무사나 1사에 주자가 1, 2루, 혹은 만루. 이때 타자가 평범한 내야 뜬공을 올리면, 심판이 공이 떨어지기 전에 먼저 선언합니다. 타자 아웃.",
    "s03": "왜 보험이냐. 이 선언이 없으면 주자들은 지옥에 갇힙니다. 야수가 잡으면 귀루해야 하고, 떨어뜨리면 뛰어야 하거든요. 수비가 그 심리를 악용하는 걸 원천 차단하는 겁니다. 조건은 딱 세 개. 무사 또는 1사. 주자 1, 2루 또는 만루. 그리고 내야수가 평범하게 잡을 수 있는 뜬공.",
    "s04": "1895년, 미국 내셔널리그로 갑니다. 그 시절 내야수들 사이에 유행하던 꼼수가 있었어요. 쉬운 뜬공을 잡는 척하다가 일부러 툭 떨어뜨리는 겁니다. 베이스에 붙어 있던 주자들은 그제야 허둥지둥 뛰고, 수비는 여유롭게 병살, 운 좋으면 삼중살. 한 명 잡을 공으로 두세 명을 잡는 거죠.",
    "s05": "리그가 칼을 뽑았습니다. 그 공은 그냥 아웃으로 치겠다. 이게 인필드 플라이의 시작이에요. 1901년에 무사 상황까지 넓어졌고, 1904년엔 직선타구 제외, 1920년엔 번트 제외. 130년째 살아 있는 규칙입니다.",
    "s06": "2025년 10월 29일, 대전, 한국시리즈 3차전. 2회말 1사 1, 2루에서 한화 이도윤 선수의 타구가 높이 뜹니다. 낙하 지점은 내야와 외야의 경계, 애매한 곳. LG 유격수 오지환 선수가 먼저 자리를 잡았습니다. 충분히 잡을 수 있어 보였죠. 그런데 안 잡습니다. 공을 일부러 떨어뜨린 다음, 2루로 던져 포스아웃, 런다운에 걸린 주자까지 태그아웃. 순식간에 병살이 완성됐습니다.",
    "s07": "김경문 감독이 뛰쳐나왔어요. 인필드 플라이 아니냐. 하지만 선언은 없었고, 이 규칙은 비디오 판독 대상도 아닙니다. 항의는 받아들여지지 않았죠. 1895년에 막으려던 바로 그 플레이가, 130년 뒤 한국시리즈에서 그대로 재현된 겁니다. 규칙이 있어도, 심판이 선언하지 않으면 없는 규칙이라는 것. 이게 인필드 플라이의 가장 무서운 부분입니다.",
    "s08": "첫 번째 오해. 인필드 플라이가 선언되면 경기가 멈춘다? 아닙니다. 타자만 아웃이고 공은 살아 있어요. 주자는 위험을 감수하면 뛸 수 있습니다. 두 번째 오해. 내야 안에서만 선언된다? 이것도 아니에요. 기준은 위치가 아니라, 내야수가 평범하게 잡을 수 있느냐입니다.",
    "s09": "고인물 여러분을 위한 디테일 하나. 2012년 메이저리그 와일드카드 게임에서는 외야 잔디까지 나간 공에 인필드 플라이가 선언됐고, 화가 난 애틀랜타 관중이 물병을 던져 경기가 19분 멈췄습니다. 안 불러도 논란, 불러도 논란인 규칙이에요.",
    "s10": "정리하면 인필드 플라이는, 수비의 꼼수에서 주자를 지키는 130년짜리 보험입니다. 단, 심판이 불러줘야 효력이 생기죠. 다음 편에서는 이 규칙의 쌍둥이, 일부러 공을 떨어뜨리면 어떻게 되는지, 고의 낙구를 파봅니다. 궁금하시면 구독 버튼 눌러두세요.",
}
VIDEO_SCENE = "s06"


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
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

    if not (out.exists() and out.stat().st_size > 0):
        if sid == VIDEO_SCENE:
            clip = BASE / "clips" / "s06_seedance.mp4"
            if not clip.exists():
                raise SystemExit(f"STOP: seedance clip not ready: {clip}")
            vf = (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"fps={FPS},tpad=stop_mode=clone:stop_duration=40,trim=duration={sdur:.3f},setpts=PTS-STARTPTS"
            )
            cmd = [FFMPEG, "-y", "-i", str(clip), "-i", str(audio),
                   "-filter_complex",
                   f"[0:v]{vf}[v];[1:a]adelay=400|400,apad,atrim=duration={sdur:.3f}[a]",
                   "-map", "[v]", "-map", "[a]",
                   "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-threads", "2", str(out)]
        else:
            img = BASE / "images" / f"{sid}.png"
            if i % 2 == 0:
                zexpr = f"min(1+0.10*on/{frames},1.10)"
            else:
                zexpr = f"max(1.10-0.10*on/{frames},1.0)"
            vf = (
                f"scale=1920:1080,zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
                f":d={frames}:s={W}x{H}:fps={FPS}"
            )
            cmd = [FFMPEG, "-y", "-i", str(img), "-i", str(audio),
                   "-filter_complex",
                   f"[0:v]{vf}[v];[1:a]adelay=400|400,apad,atrim=duration={sdur:.3f}[a]",
                   "-map", "[v]", "-map", "[a]",
                   "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-threads", "2", str(out)]
        run(cmd)
        print(f"{sid}: {sdur:.1f}s")
    else:
        print(f"{sid}: cached ({sdur:.1f}s)")
    scene_files.append(out)

    sentences = split_sentences(text)
    total_chars = sum(len(s) for s in sentences)
    cue_t = t_cursor + 0.4
    for s in sentences:
        cdur = adur * len(s) / total_chars
        srt_lines.append(f"{cue_idx}\n{ts(cue_t)} --> {ts(min(cue_t + cdur, t_cursor + sdur))}\n{s}\n")
        cue_idx += 1
        cue_t += cdur
    t_cursor += sdur

srt_path = BASE / "인필드플라이.srt"
srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
print(f"SRT: {srt_path} ({cue_idx - 1} cues)")

concat_txt = BASE / "concat.txt"
concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in scene_files), encoding="utf-8")
joined = BASE / "인필드플라이_nosub.mp4"
run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(joined)])

# 자막 burn-in
sub = BASE / "인필드플라이_sub.mp4"
run([FFMPEG, "-y", "-i", joined.name,
     "-vf", "subtitles=인필드플라이.srt:force_style='FontName=Malgun Gothic,FontSize=18,Outline=2,MarginV=40'",
     "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
     "-c:a", "copy", "-threads", "2", sub.name], cwd=str(BASE))

# BGM 믹싱 (상시 규칙: The Diamond.mp3, vol 0.15, 루프, 끝 2초 페이드아웃)
final = BASE / "2026-07-04_인필드플라이_final_bgm.mp4"
fade_st = max(0.0, t_cursor - FINAL_FADE)
run([FFMPEG, "-y", "-i", str(sub), "-stream_loop", "-1", "-i", str(BGM),
     "-filter_complex",
     f"[1:a]volume={BGM_VOLUME}[b];[0:a][b]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={fade_st:.1f}:d={FINAL_FADE}[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
print(f"FINAL: {final} ({final.stat().st_size:,} bytes, total {t_cursor:.1f}s)")
