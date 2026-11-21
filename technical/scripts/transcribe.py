"""Расшифровка записи с таймкодами через faster-whisper.

Запуск: python technical/scripts/transcribe.py <файл.mp4> <папка_для_результата> [модель]
Пишет transcript.txt (строки «[мм:сс] текст») и transcript.json (сегменты).
На Windows с видеокартой NVIDIA нужны пакеты nvidia-cublas-cu12 и nvidia-cudnn-cu12.
"""
import json, os, sys, time
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # загрузка через xet обрывалась

# Подключаем DLL CUDA из pip-пакетов nvidia-* (Windows)
try:
    import nvidia
    base = Path(nvidia.__path__[0])
    for sub in ["cublas/bin", "cudnn/bin"]:
        d = base / sub
        if d.exists():
            os.add_dll_directory(str(d))
            os.environ["PATH"] = str(d) + os.pathsep + os.environ["PATH"]
except Exception:
    pass

from faster_whisper import WhisperModel

src, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
model_name = sys.argv[3] if len(sys.argv) > 3 else "large-v3"
out_dir.mkdir(parents=True, exist_ok=True)

model = None
# Сначала GPU в float16, потом GPU в int8 (меньше памяти), в конце CPU
for device, ctype in [("cuda", "float16"), ("cuda", "int8_float16"), ("cpu", "int8")]:
    try:
        model = WhisperModel(model_name, device=device, compute_type=ctype)
        break
    except Exception as e:
        print(f"{device}/{ctype} не подошёл: {e}", flush=True)
if model is None:
    sys.exit("Не удалось загрузить модель")

def load_audio(path, sr=16000):
    """Звук в 16 кГц моно float32. Свой декодер: decode_audio из faster-whisper 1.2 не работает с PyAV 15+."""
    import av, numpy as np
    chunks = []
    with av.open(str(path)) as c:
        rs = av.AudioResampler(format="s16", layout="mono", rate=sr)
        for frame in c.decode(audio=0):
            for f in rs.resample(frame):
                chunks.append(f.to_ndarray().reshape(-1))
        for f in rs.resample(None):
            chunks.append(f.to_ndarray().reshape(-1))
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def cut_points(audio, sr=16000, chunk_s=300, search_s=10):
    """Границы кусков около каждых chunk_s секунд, в самом тихом месте окна ±search_s.
    Кусками — чтобы не держать в памяти признаки всей записи (для часа это ~0,5 ГБ)."""
    import numpy as np
    n, cuts, pos = len(audio), [0], chunk_s * sr
    win = sr // 10  # окна по 0,1 с
    while pos < n - search_s * sr:
        lo, hi = pos - search_s * sr, pos + search_s * sr
        seg = audio[lo:hi][: (hi - lo) // win * win].reshape(-1, win)
        cut = lo + int(np.argmin((seg ** 2).mean(axis=1))) * win + win // 2
        cuts.append(cut)
        pos = cut + chunk_s * sr
    cuts.append(n)
    return cuts


t0 = time.time()
audio = load_audio(src)
duration = len(audio) / 16000
print(f"audio loaded: {duration:.0f}s", flush=True)
print(f"device={device}/{ctype} model={model_name}", flush=True)

fmt = lambda s: f"{int(s // 60):02d}:{int(s % 60):02d}"
prompt = "VK Case Champ, ВКонтакте, Маркет ВКонтакте, шопсы, чекаут, GMV, Партнёр, датасет, самозанятые."
rows = []
cuts = cut_points(audio)
with open(out_dir / "transcript.txt", "w", encoding="utf-8") as f:
    for a, b in zip(cuts[:-1], cuts[1:]):
        offset = a / 16000
        segments, _ = model.transcribe(audio[a:b], language="ru", vad_filter=True, beam_size=5,
                                       initial_prompt=prompt)
        for seg in segments:
            s, e, text = seg.start + offset, seg.end + offset, seg.text.strip()
            rows.append({"start": round(s, 1), "end": round(e, 1), "text": text})
            f.write(f"[{fmt(s)}] {text}\n")
            f.flush()
        print(f"{fmt(b / 16000)} / {fmt(duration)}  ({time.time() - t0:.0f}s)", flush=True)
json.dump(rows, open(out_dir / "transcript.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"done: {len(rows)} segments in {time.time() - t0:.0f}s", flush=True)
