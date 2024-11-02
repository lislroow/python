import re
import subprocess
import pandas as pd
from datetime import datetime
import os

# basic
TARGET_BASE = 'C:\\project'
COMMIT_PATTERN = re.compile(r"^([0-9a-f]{7})\|(\S+)\|(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) ([+-]\d{4})$")
CMD='git log --pretty=format:%h|%cn|%cd --name-only --date=iso main'

# filters
PROJECTS = ['react', 'java']
COMMITTERS = ['myeonggu.kim', '김명구']
FROM_DATE = '2024-01-02'

try:
    subdirs = [d for d in os.listdir(TARGET_BASE) if os.path.isdir(os.path.join(TARGET_BASE, d))]
except FileNotFoundError:
    print(f"지정한 디렉토리가 존재하지 않습니다: {TARGET_BASE}")
except PermissionError:
    print(f"지정한 디렉토리에 접근할 수 없습니다: {TARGET_BASE}")

RESULT_LIST = []

for subdir in subdirs:
    project = os.path.basename(subdir)
    if project in PROJECTS:
        repo_path = os.path.join(TARGET_BASE, subdir)
        result = subprocess.run(CMD.split(' ', -1), capture_output=True, text=True, cwd=repo_path, encoding='utf-8')
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            commit_hash = ''
            committer = ''
            date = ''
            time = ''
            timezone = ''
            for line in lines:
                print(f"line: {line}")
                match = COMMIT_PATTERN.match(line)
                if match:
                    commit_hash = match.group(1)
                    committer = match.group(2)
                    date = match.group(3)
                    time = match.group(4)
                    timezone = match.group(5)
                    print(f"date: {date}")
                else:
                    if FROM_DATE <= date and committer in COMMITTERS:
                        if line.strip() != "":
                            RESULT_LIST.append({
                                '프로젝트': project,
                                'COMMIT': commit_hash,
                                '일시': f"{date} {time}",
                                '개발자': committer,
                                '파일경로': f"{project}/{line}"
                            })
        else:
            print("Error executing git command:", result.stderr)
        
        for file in RESULT_LIST:
            print(f"{file['프로젝트']} {file['COMMIT']} {file['일시']} {file['개발자']} {file['파일경로']}")

if RESULT_LIST:
    df = pd.DataFrame(RESULT_LIST)
    now = datetime.now()
    formatted_now = now.strftime('%Y%m%d_%H%M%S')
    df.to_excel('소스파일_변경내역_'+formatted_now +'.xlsx', index=False)
