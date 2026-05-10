import sys, csv, os


def parse(input_file):
    req, err, slow = {}, {}, []
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if '\t' not in line:
                continue
            parts = line.split('\t', 1)
            key = parts[0].strip().strip('"')
            val = parts[1].strip()
            if not val.isdigit():
                continue
            n = int(val)
            if key.startswith("REQ|"):
                req[key[4:]] = n
            elif key.startswith("ERR|"):
                err[key[4:]] = n
            elif key.startswith("SLOW|"):
                slow.append((key[5:], n))
    return req, err, slow


def validate(raw_file, req, err, slow, target="payment-service"):
    total = errors = slow_cnt = 0
    with open(raw_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 8 or row[3] != target:
                continue
            total += 1
            if int(row[6]) >= 500:
                errors += 1
            if float(row[7]) > 800:
                slow_cnt += 1

    mr_total = req.get(target, 0)
    mr_err = err.get(target, 0)
    mr_slow = sum(c for ep, c in slow if ep.startswith(f"{target},"))

    ok = total == mr_total and errors == mr_err and slow_cnt == mr_slow
    print(f"Validation {target}: REQ={mr_total}/{total} ERR={mr_err}/{errors} SLOW={mr_slow}/{slow_cnt} {'PASS' if ok else 'FAIL'}")
    return ok


def process(input_file, output_file, raw_file=None):
    req, err, slow = parse(input_file)
    slow.sort(key=lambda x: x[1], reverse=True)
    top10 = slow[:10]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Runtime: Local Machine / Windows, mrjob local mode\n")
        f.write("# Data: Task1 download.py -> download_data/\n\n")
        f.write("=== Output 1: Request Count by Service ===\n")
        for s, c in sorted(req.items()):
            f.write(f"{s} {c}\n")
        f.write("\n=== Output 2: Server Error Count by Service ===\n")
        for s, c in sorted(err.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{s} {c}\n")
        f.write("\n=== Output 3: Top 10 Slow Endpoints ===\n")
        for ep, c in top10:
            f.write(f"{ep} {c}\n")

    print(f"Report generated: {output_file}")
    if raw_file and os.path.exists(raw_file):
        all_ok = True
        for svc in ["auth-service", "notification-service", "order-service", "payment-service", "search-service"]:
            if not validate(raw_file, req, err, slow, target=svc):
                all_ok = False
        print(f"Validation summary: {'ALL PASSED' if all_ok else 'SOME FAILED'}")
        return all_ok
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_task2_output.py <task2_raw_output.txt> <task2_output.txt> [raw.csv]")
        sys.exit(1)
    raw = sys.argv[3] if len(sys.argv) > 3 else None
    process(sys.argv[1], sys.argv[2], raw)