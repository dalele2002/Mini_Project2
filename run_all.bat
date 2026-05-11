@echo off
chcp 65001 >nul

echo COMP3041J Mini-Project 2 - Execution
echo.

:: Create results directory if not exists
if not exist results mkdir results

:: Task 1: Upload to OSS
echo.
echo [1/4] Task 1: Upload to OSS...
echo [INFO] You will be prompted to enter OSS credentials in the terminal.
cd task1_cloud_storage
python upload.py
cd ..

:: Task 1: Download from OSS
echo.
echo [2/4] Task 1: Download from OSS...
echo [INFO] You will be prompted to enter OSS credentials again.
cd task1_cloud_storage
python download.py
cd ..

:: Task 2: MapReduce Baseline
echo.
echo [3/4] Task 2: MapReduce baseline...
echo [INFO] Reading from download_data/ and writing to results/...
python task2_mapreduce/task2_mapreduce.py < "download_data/Comp3041J MiniProject 2 Dataset.csv" > "results/task2_raw_output.txt"
if %errorlevel% neq 0 (
    echo [ERROR] MapReduce execution failed.
    pause
    exit /b 1
)

cd task2_mapreduce
python process_task2_output.py "..\results\task2_raw_output.txt" "..\results\task2_output.txt" "..\download_data\Comp3041J MiniProject 2 Dataset.csv"
if %errorlevel% neq 0 (
    echo [ERROR] MapReduce post-processing failed.
    pause
    exit /b 1
)
cd ..

:: Task 3: Ray Extension
echo.
echo [4/4] Task 3: Ray degraded service detection...
cd task3_ray
python task3_ray.py
if %errorlevel% neq 0 (
    echo [ERROR] Ray execution failed.
    pause
    exit /b 1
)
cd ..

echo.
echo Execution complete.
echo Output files:
echo   - results/task2_raw_output.txt
echo   - results/task2_output.txt
echo   - results/ray_degraded_services.csv
pause