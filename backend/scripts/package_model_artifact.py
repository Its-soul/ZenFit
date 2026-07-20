import argparse
from pathlib import Path
from app.ai.artifacts import package_artifact

def main():
    p=argparse.ArgumentParser();p.add_argument("candidate",type=Path);p.add_argument("destination",type=Path);p.add_argument("--environment",choices=("developer-beta","development","production"),required=True);a=p.parse_args();package_artifact(a.candidate,a.destination,environment=a.environment);print(f"Packaged file-only {a.environment} artifact at {a.destination}")
if __name__=="__main__":main()
