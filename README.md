MemeberA你把ReADME更新一下吧，还有run_all.bat,还有具体的requirements.txt
# Mini-Project 2: Cloud Service Log Analytics (From MapReduce to Ray)

Module: COMP3041J Cloud Computing

## Overview

This project analyses a synthetic cloud service log dataset (~50,000 records) 
through a pipeline of:
1. Cloud object storage (Alibaba Cloud OSS)
2. MapReduce baseline analytics (mrjob)
3. Ray-based parallel processing for degraded-service detection

## Environment

- Python 3.10+
- Windows / Local execution
- Dependencies: `mrjob`, `ray`, `oss2`

## Installation

```bash
pip install -r requirements.txt
