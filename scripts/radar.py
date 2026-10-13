import argparse, json
from pathlib import Path
from radar_core import build_report, markdown_report

def main() -> None:
    p = argparse.ArgumentParser(description="Build an evidence-linked AI skill radar report")
    sub = p.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan"); scan.add_argument("--input", required=True); scan.add_argument("--output", required=True); scan.add_argument("--profile"); scan.add_argument("--limit", type=int, default=5)
    args = p.parse_args()
    if args.command == "scan":
        records = json.loads(Path(args.input).read_text(encoding="utf-8")); profile = json.loads(Path(args.profile).read_text(encoding="utf-8")) if args.profile else None
        Path(args.output).write_text(markdown_report(build_report(records, profile), args.limit), encoding="utf-8")
        print(args.output)
if __name__ == "__main__": main()
