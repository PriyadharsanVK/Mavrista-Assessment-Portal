"""Container entrypoint. Executes stdin/stdout coding tasks with no network."""
import json
import os
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

LANGUAGE = sys.argv[1]
TIME_LIMIT = max(1, min(30, int(sys.argv[2])))
WORK = Path('/work')
TMP = Path('/tmp')
FILES = {'Python':'main.py','JavaScript':'main.js','Java':'Main.java','C++':'main.cpp','C':'main.c'}

def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT + 1, TIME_LIMIT + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (65536, 65536))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))

def compile_command():
    src = str(WORK / FILES[LANGUAGE])
    if LANGUAGE == 'Java': return ['javac','-J-Xmx96m','-d',str(TMP),src]
    if LANGUAGE == 'C++': return ['g++','-O2','-std=c++17',src,'-o',str(TMP/'main')]
    if LANGUAGE == 'C': return ['gcc','-O2','-std=c17',src,'-o',str(TMP/'main')]
    return None

def program_command():
    src=str(WORK/FILES[LANGUAGE])
    if LANGUAGE == 'Python': return ['python3','-I',src]
    if LANGUAGE == 'JavaScript': return ['node',src]
    if LANGUAGE == 'Java': return ['java','-Xmx96m','-cp',str(TMP),'Main']
    return [str(TMP/'main')]

def invoke(command, stdin=b'', timeout=TIME_LIMIT, capture=65536):
    out_path=TMP/'stdout'; err_path=TMP/'stderr'
    try:
        with open(out_path,'wb') as out, open(err_path,'wb') as err:
            proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=out,stderr=err,preexec_fn=limits)
            try: proc.communicate(stdin,timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.communicate()
                return 124,b'',b'Time limit exceeded.'
        output=out_path.read_bytes()[:capture]
        error=err_path.read_bytes()[:capture]
        return proc.returncode,output,error
    except FileNotFoundError as e: return 127,b'',str(e).encode()
    except Exception as e: return 126,b'',str(e).encode()

try:
    tests=json.loads((WORK/'tests.json').read_text(encoding='utf-8'))
    if not isinstance(tests,list) or len(tests)>100: raise ValueError('Invalid test set.')
    compile_cmd=compile_command()
    if compile_cmd:
        code,out,err=invoke(compile_cmd,b'',timeout=15)
        if code:
            print(json.dumps({'compileError':err.decode(errors='replace')[:4000],'results':[]}));sys.exit(0)
    results=[]
    for case in tests:
        code,out,err=invoke(program_command(),str(case.get('input','')).encode(),timeout=TIME_LIMIT)
        actual=out.decode(errors='replace').strip()
        expected=str(case.get('output','')).strip()
        results.append({'passed':code==0 and actual==expected,'output':actual[:4000],
                        'error':'' if code==0 else (err.decode(errors='replace')[:4000] or f'Program exited with code {code}.')})
    print(json.dumps({'results':results},ensure_ascii=False))
except Exception as exc:
    print(json.dumps({'compileError':str(exc)[:1000],'results':[]}))
