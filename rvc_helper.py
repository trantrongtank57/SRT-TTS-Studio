"""Helper script chạy bằng rvc_env (Python 3.10) để thực hiện RVC inference."""
import argparse
import soundfile as sf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",            required=True)
    parser.add_argument("--output",           required=True)
    parser.add_argument("--model",            required=True)
    parser.add_argument("--index",            default="")
    parser.add_argument("--pitch",            type=int,   default=0)
    parser.add_argument("--algo",             default="rmvpe",
                        choices=["rmvpe", "fcpe", "harvest", "crepe", "pm"])
    parser.add_argument("--index_influence",  type=float, default=0.75)
    parser.add_argument("--rmvpe_path",       default="")
    parser.add_argument("--hubert_path",      default="")
    parser.add_argument("--cpu",              action="store_true")
    args = parser.parse_args()

    from infer_rvc_python import BaseLoader

    loader = BaseLoader(
        only_cpu=args.cpu,
        hubert_path=args.hubert_path or None,
        rmvpe_path=args.rmvpe_path or None,
    )
    loader.apply_conf(
        tag="model",
        file_model=args.model,
        file_index=args.index or "",
        pitch_lvl=args.pitch,
        pitch_algo=args.algo,
        index_influence=args.index_influence,
    )
    audio_array, sample_rate = loader.generate_from_cache(
        audio_data=args.input,
        tag="model",
    )
    sf.write(args.output, audio_array, sample_rate)
    print(f"OK: {args.output}")


if __name__ == "__main__":
    main()
