"""VoxCPM batch voice clone helper — chạy bằng voxcpm_env/Scripts/python.exe."""
import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf
import torch
import torchaudio


# Patch torchaudio.load để tránh lỗi backend trên Windows
def _patched_load(path, *args, **kwargs):
    data, sr = sf.read(str(path), dtype='float32', always_2d=True)
    return torch.from_numpy(data.T), sr

torchaudio.load = _patched_load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texts-json",    required=True,  help="JSON [{index, text}]")
    parser.add_argument("--output-dir",    required=True,  help="Thư mục lưu line_NNNN.wav")
    parser.add_argument("--ckpt-dir",      required=True,  help="Thư mục model VoxCPM")
    parser.add_argument("--reference",     default="",     help="File audio giọng mẫu")
    parser.add_argument("--reference-text",default="",     help="Lời thoại của audio mẫu")
    parser.add_argument("--timesteps",     type=int,   default=10)
    parser.add_argument("--cfg-value",     type=float, default=2.0)
    parser.add_argument("--max-len",       type=int,   default=600)
    args = parser.parse_args()

    # Đọc danh sách text
    with open(args.texts_json, encoding='utf-8-sig') as f:
        items = json.load(f)

    if not items:
        print("ALL_DONE", flush=True)
        return

    # Phát hiện GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        print(f"[VoxCPM] GPU: {gpu_name} → dùng CUDA", file=sys.stderr, flush=True)
    else:
        print(f"[VoxCPM] Không có GPU → dùng CPU", file=sys.stderr, flush=True)

    # Load model một lần
    print(f"[VoxCPM] Đang load model: {args.ckpt_dir}", file=sys.stderr, flush=True)
    from voxcpm.core import VoxCPM
    model = VoxCPM.from_pretrained(
        hf_model_id=args.ckpt_dir,
        load_denoiser=False,
        optimize=False,
    )
    sample_rate = model.tts_model.sample_rate

    # Đảm bảo model chạy trên đúng device
    try:
        model.tts_model = model.tts_model.to(device)
    except Exception:
        pass

    print(f"[VoxCPM] Model loaded. Sample rate: {sample_rate}Hz | device: {device}", file=sys.stderr, flush=True)

    ref_audio = args.reference if args.reference and os.path.exists(args.reference) else None
    ref_text  = args.reference_text.strip() if args.reference_text else None

    # VoxCPM 1.5: prompt_wav_path và prompt_text phải đi cùng nhau
    if ref_audio and not ref_text:
        print("[VoxCPM] CẢNH BÁO: Audio mẫu cần có 'Nội dung mẫu' để nhân bản giọng. "
              "Đang chạy TTS thường (không nhân bản).", file=sys.stderr, flush=True)
        ref_audio = None

    if ref_audio:
        print(f"[VoxCPM] Chế độ: Nhân bản giọng (voice cloning)", file=sys.stderr, flush=True)
    else:
        print(f"[VoxCPM] Chế độ: TTS thường (không có audio mẫu)", file=sys.stderr, flush=True)

    os.makedirs(args.output_dir, exist_ok=True)

    MAX_RETRIES = 3

    for item in items:
        idx  = item["index"]
        text = item["text"]

        out_wav = os.path.join(args.output_dir, f"line_{idx:04d}.wav")

        best_audio = None
        best_peak  = 0.0

        for attempt in range(MAX_RETRIES):
            try:
                # Mỗi lần retry tăng thêm timesteps để thoát local minimum
                ts = args.timesteps + attempt * 5
                audio_np = model.generate(
                    text=text,
                    prompt_wav_path=ref_audio,
                    prompt_text=ref_text if ref_audio else None,
                    cfg_value=args.cfg_value,
                    inference_timesteps=ts,
                    max_len=args.max_len,
                    denoise=False,
                )

                audio_np = np.nan_to_num(audio_np, nan=0.0, posinf=0.0, neginf=0.0)
                peak = float(np.abs(audio_np).max())

                if peak > best_peak:
                    best_peak  = peak
                    best_audio = audio_np

                if peak > 1e-6:
                    break  # có âm thanh, không cần retry
                else:
                    print(f"WARN:{idx}:silent attempt {attempt + 1}/{MAX_RETRIES} "
                          f"(ts={ts}, peak={peak:.2e})", flush=True)

            except Exception as e:
                print(f"WARN:{idx}:attempt {attempt + 1} error: {e}", flush=True)

        if best_audio is None or best_peak < 1e-6:
            print(f"ERROR:{idx}:audio silent sau {MAX_RETRIES} lần thử", flush=True)
            continue

        # Chuẩn hoá biên độ
        best_audio = (best_audio / best_peak * 0.95).astype('float32')
        sf.write(out_wav, best_audio, sample_rate)
        print(f"DONE:{idx}", flush=True)

    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
