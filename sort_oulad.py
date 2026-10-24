import csv
import heapq
import time
import tempfile
from pathlib import Path

DATA_DIR = Path("/data")
INPUT_FILE = DATA_DIR / "studentVle.csv"
OUTPUT_FILE = DATA_DIR / "studentVle_sorted.csv"

CHUNK_ROWS = 100_000
KEY_COLUMN = 5  # sum_click


def write_sorted_chunk(rows, folder, number):
    rows.sort(key=lambda row: int(row[KEY_COLUMN]))
    path = Path(folder) / f"chunk_{number:04d}.csv"

    with path.open("w", newline="", encoding="utf-8") as file:
        csv.writer(file).writerows(rows)

    return path


def read_chunk(path):
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.reader(file):
            yield int(row[KEY_COLUMN]), row


def main():
    start = time.perf_counter()
    chunk_paths = []
    row_count = 0

    with tempfile.TemporaryDirectory(prefix="sort_", dir=DATA_DIR) as temp_folder:
        with INPUT_FILE.open(newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)

            if header[-1] != "sum_click":
                raise ValueError(f"Unexpected CSV header: {header}")

            batch = []

            for row in reader:
                batch.append(row)
                row_count += 1

                if len(batch) >= CHUNK_ROWS:
                    chunk_paths.append(
                        write_sorted_chunk(batch, temp_folder, len(chunk_paths))
                    )
                    batch = []

            if batch:
                chunk_paths.append(
                    write_sorted_chunk(batch, temp_folder, len(chunk_paths))
                )

        with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)

            previous_key = None
            merged_chunks = heapq.merge(
                *(read_chunk(path) for path in chunk_paths),
                key=lambda item: item[0],
            )

            for key, row in merged_chunks:
                if previous_key is not None and key < previous_key:
                    raise ValueError("Output is not sorted")

                writer.writerow(row)
                previous_key = key

    elapsed = time.perf_counter() - start
    print(f"Rows sorted: {row_count:,}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Throughput: {row_count / elapsed:,.0f} rows/second")
    peak_file = Path("/sys/fs/cgroup/memory.peak")
    if peak_file.exists():
        peak_mib = int(peak_file.read_text().strip()) / (1024 * 1024)
        print(f"Peak container memory: {peak_mib:.1f} MiB")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()