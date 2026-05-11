# Mini-Project 2: Cloud Service Log Analytics (From MapReduce to Ray)

**Module:** COMP3041J Cloud Computing

## Overview

This project analyses a synthetic cloud service log dataset (~50,000 records, ~4.4 MB) through a pipeline of:

1. **Cloud object storage** (Alibaba Cloud OSS) — centralised repository with integrity verification
2. **MapReduce baseline analytics** (mrjob local mode) — request count, error count, top-10 slow endpoints
3. **Ray-based parallel processing** (local instance, 20 CPU cores) — multi-criteria degraded-service detection

All outputs are validated through manual full-table scans against ground-truth CSV counts.

---

## Environment

- **OS:** Windows 10/11 (tested)
- **Python:** 3.10+
- **Execution:** Local machine (mrjob inline runner, Ray local instance)
- **Dependencies:** See `requirements.txt`

---

## Installation

Install required Python packages:

```bash
pip install -r requirements.txt
```

### requirements.txt

```
mrjob>=0.7.4
ray>=2.55.1
oss2>=2.18.0
```

---

## Project Structure

```
COMP3041J-MiniProject2/
├── data/                                    # Original dataset
│   └── Comp3041J MiniProject 2 Dataset.csv
├── download_data/                           # Verified dataset from OSS (Shared)
│   └── Comp3041J MiniProject 2 Dataset.csv
├── results/                                 # Output files
│   ├── task2_output.txt                     # Formatted MapReduce report 
│   ├── task2_raw_output.txt                 # Raw MapReduce key-value output
│   └── ray_degraded_services.csv            # Ray degraded-service list
├── task1_cloud_storage/                     # Member A: Cloud Storage (Member A)
│   ├── upload.py                            # Upload to Alibaba Cloud OSS (Member A)
│   └── download.py                          # Download from OSS + verify (Member A)
├── task2_mapreduce/                         # MapReduce + Post-processing (Member B)
│   ├── task2_mapreduce.py                   # Mapper/Reducer logic (mrjob) (Member B)
│   └── process_task2_output.py              # Output parser + validate() (Member B)
├── task3_ray/                               # Ray Extension (Member C)
│   └── task3_ray.py                         # @ray.remote shards + merge + detect (Member C)
├── requirements.txt
├── run_all.bat                              # Sequential execution script (Member A)
└── README.md
```

---

## How to Run
### Prerequisites for Task 1

Task 1 requires valid Alibaba Cloud OSS credentials (Access Key ID and Access Key Secret) to upload/download the dataset. **In the source code, credentials are deliberately prompted at runtime (`input()`) and never hard-coded, embedded, or committed to the repository** — this reflects real-world security practice where sensitive access keys should not appear in version-controlled source files.

However, to ensure the project can be fully reproduced by instructors or peer reviewers, **the OSS credentials are provided in the "How to Run" section below** for this academic submission. This separation of concerns — secure code design paired with documented runtime credentials — balances production-ready security practices with the practical need for third-party verification.

**If you prefer not to use cloud storage or do not have an Alibaba Cloud account:**
- Skip Step 1 (Upload/Download)
- Use the dataset directly from `download_data/Comp3041J MiniProject 2 Dataset.csv`
- Proceed to Step 2 (MapReduce) and Step 3 (Ray) using the local copy

### OSS Credentials (For Academic Submission Only)
> **Note:** The following credentials are provided solely to enable instructors and peer reviewers to reproduce the full pipeline.

**Access Key ID** 
- To prevent the leakage of Alibaba Cloud OSS ID and password, for security reasons, we have provided the password and ID in the last question of Mini-lab Project 2 submitted by the coordinator, along with the GitHub repository address. After submission, only the professor can view it.

**Access Key Secret** 
- To prevent the leakage of Alibaba Cloud OSS ID and password, for security reasons, we have provided the password and ID in the last question of Mini-lab Project 2 submitted by the coordinator, along with the GitHub repository address. After submission, only the professor can view it.
  
**Bucket Name**
  - To prevent the leakage of Alibaba Cloud OSS ID and password, for security reasons, we have provided the password and ID in the last question of Mini-lab Project 2 submitted by the coordinator, along with the GitHub repository address. After submission, only the professor can view it.
    
### Step 1: Task 1 — Cloud Object Storage (Member A)

```bash
cd task1_cloud_storage

:: Upload dataset to Alibaba Cloud OSS
:: Credentials are entered at runtime (not hard-coded)
python upload.py
```

**Expected interaction:**
```
Enter OSS Access Key ID: <your-key-id>
Enter OSS Access Key Secret: <your-key-secret>
Uploaded: ..\data\Comp3041J MiniProject 2 Dataset.csv -> oss://comp3041j-minigroupproject2-2026/Comp3041J MiniProject 2 Dataset.csv
Platform: Local Machine / Windows, Cloud: Alibaba Cloud OSS, Region: cn-beijing, Bucket: comp3041j-minigroupproject2-2026
Size Check: local=4450416 cloud=4450416 PASS
Sample Check 1: PASS
Sample Check 2: PASS
Verification: PASSED - Data stored in cloud object storage
```

```bash
:: Download verified dataset from OSS
python download.py
```

**Expected interaction:**
```
Enter OSS Access Key ID: <your-key-id>
Enter OSS Access Key Secret: <your-key-secret>
Downloaded: oss://comp3041j-minigroupproject2-2026/Comp3041J MiniProject 2 Dataset.csv -> ..\download_data\Comp3041J MiniProject 2 Dataset.csv
Platform: Local Machine / Windows, Cloud: Alibaba Cloud OSS, Region: cn-beijing, Bucket: comp3041j-minigroupproject2-2026
Size Check: source=4450416 downloaded=4450416 PASS
Sample Check 1: PASS
Sample Check 2: PASS
Verification: PASSED - Task 1 complete. Data available at download_data/ for Task 2 (MapReduce) and Task 3 (Ray)
```

```bash
cd ..
```

**Security note:** Access credentials are prompted at runtime and never stored in source code or committed to the repository.

---

### Step 2: Task 2 — MapReduce Baseline Analytics (Member B)

```bash
:: Ensure results directory exists
if not exist "results" mkdir "results"

cd task2_mapreduce

:: Run MapReduce job
:: IMPORTANT: The dataset filename contains spaces and MUST be wrapped in quotes
python task2_mapreduce.py < "..\download_data\Comp3041J MiniProject 2 Dataset.csv" > "..\results\task2_raw_output.txt"

:: Post-process raw output and validate against manual CSV counts
python process_task2_output.py
```

**Expected output:**
```
Report generated: results/task2_output.txt
Validation auth-service: REQ=12121/12121 ERR=436/436 SLOW=545/545 PASS
Validation notification-service: REQ=8412/8412 ERR=436/436 SLOW=566/566 PASS
Validation order-service: REQ=10937/10937 ERR=717/717 SLOW=1151/1151 PASS
Validation payment-service: REQ=7914/7914 ERR=1362/1362 SLOW=2134/2134 PASS
Validation search-service: REQ=10616/10616 ERR=904/904 SLOW=4581/4581 PASS
Validation summary: ALL PASSED
```

```bash
cd ..
```

---

### Step 3: Task 3 — Ray Extension Analytics (Member C)

```bash
cd task3_ray

:: Run Ray degraded-service detection
python task3_ray.py
```

**Expected output:**
```
Validation auth-service: manual={'total': 12121, 'slow': 545, 'errors': 436, 'timeouts': 199} Ray={'total': 12121, 'slow': 545, 'errors': 436, 'timeouts': 199} PASS
Validation notification-service: manual={'total': 8412, 'slow': 566, 'errors': 436, 'timeouts': 164} Ray={'total': 8412, 'slow': 566, 'errors': 436, 'timeouts': 164} PASS
Validation order-service: manual={'total': 10937, 'slow': 1151, 'errors': 717, 'timeouts': 308} Ray={'total': 10937, 'slow': 1151, 'errors': 717, 'timeouts': 308} PASS
Validation payment-service: manual={'total': 7914, 'slow': 2134, 'errors': 1362, 'timeouts': 664} Ray={'total': 7914, 'slow': 2134, 'errors': 1362, 'timeouts': 664} PASS
Validation search-service: manual={'total': 10616, 'slow': 4581, 'errors': 904, 'timeouts': 446} Ray={'total': 10616, 'slow': 4581, 'errors': 904, 'timeouts': 446} PASS
Validation summary: ALL PASSED

Task 3 complete: ..\results\ray_degraded_services.csv
Ray elapsed: ~0.5s
  search-service,high slow request rate; repeated timeout errors
  order-service,repeated timeout errors
  payment-service,high slow request rate; high server error rate; repeated timeout errors
  notification-service,repeated timeout errors
  auth-service,repeated timeout errors
```

```bash
cd ..
```

---

### One-Command Execution (Windows)

Alternatively, run all tasks sequentially from the project root:

```bash
run_all.bat
```

---

## Outputs

After successful execution, the `results/` directory contains:

| File | Description | Produced By |
|------|-------------|-------------|
| `task2_raw_output.txt` | Raw tab-separated MapReduce key-value output | `task2_mapreduce.py` |
| `task2_output.txt` | Formatted report: Request Count, Error Count, Top-10 Slow Endpoints | `process_task2_output.py` |
| `ray_degraded_services.csv` | Degraded services list with reasons and runtime metadata | `task3_ray.py` |

---

## Team Members

| Member | Role For Coding | Files |
|--------|-----------------|-------|
| **Member A** | Task 1 (Cloud Storage) + Project Scaffolding | `task1_cloud_storage/upload.py`, `task1_cloud_storage/download.py`, repository structure |
| **Member B** | Task 2 (MapReduce + Post-processing + Validation) | `task2_mapreduce/task2_mapreduce.py`, `task2_mapreduce/process_task2_output.py` |
| **Member C** | Task 3 (Ray Extension + Comparison) | `task3_ray/task3_ray.py` |

**Integration:** `download_data/` serves as the single source of truth for both MapReduce and Ray. Member B's `validate()` approach (manual CSV scan vs program output) is reused by Member C for Ray correctness checking.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `The system cannot find the file specified` | Dataset filename contains spaces; path not quoted | Wrap path in double quotes: `"..\download_data\Comp3041J MiniProject 2 Dataset.csv"` |
| `Credentials not provided` | OSS Access Key not entered when prompted | Enter your Access Key ID and Secret when `upload.py` / `download.py` prompts |
| `results` folder missing | Directory not created before Task 2 | Run `if not exist "results" mkdir "results"` before Task 2 |
| `FileNotFoundError: download_data\...` | Task 1 not completed | Run `download.py` first to generate the verified dataset |
| Ray `FutureWarning` about accelerator/GPU | Ray 2.55.1 version notice | Normal warning, does not affect execution or results |
| `ValueError: Environment variables not set` (old code) | Using previous version of upload/download | Update to latest `upload.py` / `download.py` which use runtime input |

---

## Notes

- **Dataset size:** ~4.4 MB, ~50,000 records — sized for local processing per project constraints.
- **Execution environment:** Local machine is explicitly listed as a valid environment in the project brief.
- **Security:** Cloud credentials are read via runtime `input()` prompts. No sensitive information is embedded in source code or committed to the repository.
- **Validation:** All outputs are cross-checked against manual full-table CSV scans for every service.
