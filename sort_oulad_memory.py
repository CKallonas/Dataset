import csv
import time
from pathlib import Path

input_file = Path("/data/studentVle.csv")
output_file = Path("/data/studentVle_sorted_memory.csv")

start = time.perf_counter()

with input_file.open("r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    header = next(reader)
    rows = list(reader)

print(f"Rows loaded: {len(rows):,}", flush=True)

rows.sort(key=lambda row: int(row[5]))

with output_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(rows)

elapsed = time.perf_counter() - start
print(f"Rows sorted: {len(rows):,}")
print(f"Elapsed time: {elapsed:.2f} seconds")
print(f"Throughput: {len(rows) / elapsed:,.0f} rows/second")

peak_file = Path("/sys/fs/cgroup/memory.peak")
if peak_file.exists():
    peak_mib = int(peak_file.read_text().strip()) / (1024 * 1024)
    print(f"Peak container memory: {peak_mib:.1f} MiB")

print(f"Output: {output_file}")