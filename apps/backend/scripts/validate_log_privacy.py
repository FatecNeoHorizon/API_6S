import json
import sys
from pathlib import Path

FORBIDDEN_FIELDS = {"email", "cpf", "password", "name", "nome", "senha"}

def validate(log_path: str) -> None:
    path = Path(log_path)

    if not path.exists():
        print(f"[SKIP] Log file not found: {log_path}")
        sys.exit(0)

    violations = []

    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            found = FORBIDDEN_FIELDS & set(entry.keys())
            if found:
                violations.append((line_number, found, line))

    if violations:
        print(f"[FAIL] {len(violations)} violation(s) found in {log_path}:\n")
        for line_number, fields, line in violations:
            print(f"  Line {line_number}: forbidden fields {fields}")
            print(f"  {line}\n")
        sys.exit(1)

    print(f"[OK] No forbidden fields found in {log_path}")
    sys.exit(0)


if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else "logs/app.log"
    validate(log_path)