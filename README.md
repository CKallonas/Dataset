# OULAD Sorting Benchmark Under Docker Memory Limits

This project compares two Python approaches for sorting the OULAD `studentVle.csv` dataset inside Docker containers limited to 1, 2, 4, or 8 GiB of memory. It records elapsed time, throughput, peak container memory, and whether each run completed.

## Dataset

The benchmark uses `studentVle.csv` from the Open University Learning Analytics Dataset (OULAD). The file contains 10,655,280 data rows and is approximately 432.8 MB. It is not included in this repository because of its size.

Download OULAD from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset), extract the archive, and locate `studentVle.csv`.

**Dataset citation:** Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2015). *Open University Learning Analytics dataset* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5KK69.

## The two sorting approaches

- `sort_oulad.py` uses fixed chunks of 100,000 rows. It sorts each chunk, writes temporary chunk files, and merges them. This limits the amount of data held in memory at one time.
- `sort_oulad_memory.py` loads all rows into memory and sorts the complete dataset in one operation. This tests how a whole-file workload behaves under different Docker memory limits.

Both scripts sort by the `sum_click` column and report rows processed, elapsed time, throughput, peak container memory, and output location. The Docker memory limit is applied to the container running the script.

## Requirements

- Windows 10 or 11
- Docker Desktop running with the WSL 2 backend
- Visual Studio Code
- Git, if you want to clone or publish the repository
- The OULAD dataset file `studentVle.csv`

## Prepare the dataset in Docker

The scripts expect the input file at `/data/studentVle.csv` in a Docker volume named `oulad-data`. In PowerShell, change to the extracted OULAD folder containing `studentVle.csv`, then run:

```powershell
docker volume create oulad-data
docker run --rm -v "${PWD}:/source:ro" -v oulad-data:/data python:3.12-slim python -c "import shutil; shutil.copyfile('/source/studentVle.csv', '/data/studentVle.csv')"
```

The volume keeps the dataset and generated output separate from the source-code repository. Do not commit the dataset or sorted output files to GitHub.

## Run from Visual Studio Code

1. Clone the repository and open its folder in Visual Studio Code.
2. Start Docker Desktop.
3. Ensure the Docker task in `.vscode/tasks.json` points to the folder containing your extracted OULAD dataset. Update the Windows dataset path if it differs from the original computer's path.
4. In the task configuration, select the script to run by setting the container command to either `/source/sort_oulad.py` or `/source/sort_oulad_memory.py`.
5. Select **Terminal → Run Task** and choose the Docker benchmark task. Enter a unique container name and the RAM limit when prompted.
6. Repeat for each memory limit. Use the same script, dataset, and other settings when comparing memory limits within an experiment.

The two scripts are separate experiments because they use different memory strategies. Record their results in separate tables. The task's unique container name should change for every run, for example `oulad-chunk-1g` and `oulad-memory-1g`.

## Results collected so far

Each configuration below has one recorded run. These measurements are preliminary; repeated trials would provide a more reliable comparison.

### Fixed chunks of 100,000 rows

| Docker memory limit | Elapsed time | Throughput | Peak container memory |
|---:|---:|---:|---:|
| 1 GiB | 36.21 s | 294,229 rows/s | 1,024.0 MiB |
| 2 GiB | 36.18 s | 294,501 rows/s | 1,135.7 MiB |
| 4 GiB | 35.25 s | 302,291 rows/s | 1,135.5 MiB |
| 8 GiB | 35.84 s | 297,280 rows/s | 1,135.2 MiB |

### Whole-file in-memory sort

| Docker memory limit | Result | Elapsed time | Throughput | Peak container memory |
|---:|---|---:|---:|---:|
| 1 GiB | Stopped, exit code 137 | — | — | — |
| 2 GiB | Stopped, exit code 137 | — | — | — |
| 4 GiB | Completed | 27.91 s | 381,736 rows/s | 4,096.0 MiB |
| 8 GiB | Completed | 27.37 s | 389,262 rows/s | 4,607.6 MiB |

Exit code 137 means the process was forcibly terminated; memory exhaustion is the likely explanation for the 1 GiB and 2 GiB whole-file runs. The successful runs each processed 10,655,280 rows.

## Initial interpretation

With the chunk size held at 100,000 rows, peak memory and elapsed time were similar across the 2, 4, and 8 GiB limits. The chunked approach did not need the additional memory available at those limits. The 1 GiB run reached its limit.

The whole-file approach did not complete with 1 or 2 GiB, while it completed with 4 and 8 GiB. The 8 GiB run was slightly faster than the 4 GiB run, but the difference is small and there is only one trial per setting. Repeated runs are needed before drawing a firm conclusion about timing differences.

## Repository contents

- `.vscode/tasks.json` — Visual Studio Code Docker task configuration
- `sort_oulad.py` — fixed-chunk sorting script
- `sort_oulad_memory.py` — whole-file in-memory sorting script
- `.gitignore` — excludes dataset CSV files and generated outputs
- `OULAD.names` — dataset information file

The dataset and sorted outputs are kept outside the Git repository.
