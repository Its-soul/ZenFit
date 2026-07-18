import argparse,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("version");p.add_argument("--environment",choices=("development","production"),default="development");p.add_argument("--models-dir",type=Path,default=Path("../data/models/indian_food"));args=p.parse_args()
    if not (args.models_dir/args.version).is_dir():raise FileNotFoundError("Requested immutable version does not exist")
    target="development.json" if args.environment=="development" else "active.json";(args.models_dir/target).write_text(json.dumps({"version":args.version},indent=2));print(f"Rolled back {args.environment} model to {args.version}")
if __name__=="__main__":main()
