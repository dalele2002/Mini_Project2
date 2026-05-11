import ray
import csv
import os
import platform
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ["RAY_raylet_start_wait_time_s"] = "60"
ray.init(ignore_reinit_error=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "download_data", "Comp3041J MiniProject 2 Dataset.csv"))
OUTPUT_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "results", "ray_degraded_services.csv"))

RUNTIME_ENV = {
    "platform": f"Local Machine / {platform.system()}",
    "framework": f"Ray {ray.__version__}",
    "cpus": os.cpu_count(),
    "data_source": "Task1 download.py -> download_data/",
    "pipeline_step": "Task 3: Ray Degraded Service Detection",
}


@ray.remote
def process_shard(shard_lines):
    """
    Ray remote task: processes a shard of log lines in parallel.
    Input: subset of log lines.
    Output: service_stats dictionary for this shard.
    """
    stats = {}
    for line in shard_lines:
        line = line.strip()
        if not line or line.startswith("timestamp"):
            continue
        try:
            row = next(csv.reader([line]))
            service, status, rt = row[3], int(row[6]), float(row[7])
            error = row[9] if len(row) > 9 else ""

            if service not in stats:
                stats[service] = {"total": 0, "slow": 0, "errors": 0, "timeouts": 0}

            stats[service]["total"] += 1
            if status >= 500:
                stats[service]["errors"] += 1
            if rt > 800:
                stats[service]["slow"] += 1
            if error == "Timeout":
                stats[service]["timeouts"] += 1
        except Exception:
            continue
    return stats


def merge_results(partial_results):
    """Merges partial results from multiple Ray remote tasks."""
    final = {}
    for part in partial_results:
        for service, vals in part.items():
            if service not in final:
                final[service] = {"total": 0, "slow": 0, "errors": 0, "timeouts": 0}
            for k in vals:
                final[service][k] += vals[k]
    return final


def detect_degraded(final_stats):
    """Detects degraded services based on combined evidence."""
    degraded = []
    for service, s in final_stats.items():
        total = s["total"]
        if total == 0:
            continue
        reasons = []
        if s["slow"] / total > 0.2:
            reasons.append("high slow request rate")
        if s["errors"] / total > 0.1:
            reasons.append("high server error rate")
        if s["timeouts"] >= 5:
            reasons.append("repeated timeout errors")
        if reasons:
            degraded.append((service, "; ".join(reasons)))
    return degraded


def validate(raw_file, final_stats, target="payment-service"):
    """Validation: manual count vs Ray merged result (Criteria 3)."""
    manual = {"total": 0, "slow": 0, "errors": 0, "timeouts": 0}
    with open(raw_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 9 or row[3] != target:
                continue
            manual["total"] += 1
            if int(row[6]) >= 500:
                manual["errors"] += 1
            if float(row[7]) > 800:
                manual["slow"] += 1
            if len(row) > 9 and row[9] == "Timeout":
                manual["timeouts"] += 1

    ray_stats = final_stats.get(target, {})
    ok = all(manual[k] == ray_stats.get(k, 0) for k in manual)
    print(f"Validation {target}: manual={manual} Ray={dict(ray_stats)} {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found. Please run Task 1 download.py first.", file=sys.stderr)
        sys.exit(1)

    start = time.time()

    with open(DATA_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Shard by CPU count, dispatch Ray remote tasks
    num_shards = os.cpu_count() or 4
    shard_size = max(1, len(lines) // num_shards)
    shards = [lines[i:i + shard_size] for i in range(0, len(lines), shard_size)]

    futures = [process_shard.remote(shard) for shard in shards]
    partial_results = ray.get(futures)

    # Merge partial results -> final statistics
    final_stats = merge_results(partial_results)

    # Degraded service detection
    degraded = detect_degraded(final_stats)

    # Validate correctness for all services
    all_ok = True
    for svc in ["auth-service", "notification-service", "order-service", "payment-service", "search-service"]:
        if not validate(DATA_PATH, final_stats, target=svc):
            all_ok = False
    
    print(f"Validation summary: {'ALL PASSED' if all_ok else 'SOME FAILED'}")
    
    elapsed = time.time() - start

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(f"# Runtime: {RUNTIME_ENV['platform']}, {RUNTIME_ENV['framework']}, {RUNTIME_ENV['cpus']} CPUs\n")
        f.write(f"# Data: {RUNTIME_ENV['data_source']}\n")
        f.write(f"# Pipeline: Task1(OSS) -> Task2(mrjob) -> Task3(Ray remote tasks + merge)\n")
        f.write(f"# Elapsed: {elapsed:.2f}s\n\n")
        for service, reason in degraded:
            f.write(f"{service},{reason}\n")

    print(f"\nTask 3 complete: {OUTPUT_PATH}")
    print(f"Ray elapsed: {elapsed:.2f}s")
    for service, reason in degraded:
        print(f"  {service},{reason}")


if __name__ == "__main__":
    main()
    ray.shutdown()