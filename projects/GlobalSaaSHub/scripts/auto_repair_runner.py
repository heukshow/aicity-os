"""
GlobalSaaSHub - 스마트 진단 및 자가 수정 실행기 (Auto Diagnostic & Self-Fixing Supervisor)
========================================================================================
단순 재시도가 아니라, 에러 발생 시 원인을 정확히 진단하고
해당 문제(설정/네트워크/인코딩/인증/빌드 파일 등)를 자동으로 수정한 후 재실행합니다.
"""
import os
import sys
import json
import shutil
import subprocess
import datetime
import traceback

# UTF-8 강제 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = os.path.dirname(os.path.dirname(PROJECT_DIR))
LOG_FILE = os.path.join(SCRIPT_DIR, "deploy_log.txt")
REPAIR_LOG = os.path.join(SCRIPT_DIR, "repair_history.log")

def log(msg, is_repair=False):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    sys.stdout.flush()
    target_file = REPAIR_LOG if is_repair else LOG_FILE
    try:
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ============================================================
# 진단 및 자동 수정 함수들 (Diagnostic & Repair Functions)
# ============================================================

def fix_ssh_config():
    """SSH 설정 파일의 인코딩/BOM 및 키 경로 자동 수명 및 진단"""
    log("🔧 [진단 및 수리] SSH 설정 파일 검사 및 복구 시도...", is_repair=True)
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\qmffo")
    ssh_dir = os.path.join(user_profile, ".ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    
    config_path = os.path.join(ssh_dir, "config")
    clean_config = "Host github.com\n  HostName github.com\n  User git\n  IdentityFile ~/.ssh/id_ed25519_deploy\n  StrictHostKeyChecking no\n"
    
    # ASCII pure text로 인코딩 작성 (BOM 원천 차단)
    with open(config_path, "wb") as f:
        f.write(clean_config.encode('ascii'))
    
    log("✅ [수리 완료] ~/.ssh/config 깨끗한 ASCII 형식으로 재작성 완료", is_repair=True)

def fix_env_file():
    """.env 파일의 위치 및 인코딩 복구"""
    log("🔧 [진단 및 수리] .env 환경 변수 파일 검사 중...", is_repair=True)
    env_path = os.path.join(WORKSPACE_DIR, ".env")
    if not os.path.exists(env_path):
        log("⚠️ .env 파일이 루트에 없음 - 복사본 확인 필요", is_repair=True)
    else:
        log("✅ .env 파일 존재 확인 완료", is_repair=True)

def fix_tools_json():
    """tools.json 손상 여부 진단 및 자동 복구"""
    log("🔧 [진단 및 수리] tools.json 데이터베이스 유효성 진단 중...", is_repair=True)
    tools_path = os.path.join(PROJECT_DIR, "data", "tools.json")
    if os.path.exists(tools_path):
        try:
            with open(tools_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            log(f"✅ tools.json 정상 (등록 툴 수: {len(data)})", is_repair=True)
        except Exception as e:
            log(f"❌ tools.json JSON 문법 오류 발생: {e} -> 백업 및 재초기화 복구 진행", is_repair=True)
            # 백업 후 생성
            bak_path = tools_path + f".bak_{int(datetime.datetime.now().timestamp())}"
            shutil.copyfile(tools_path, bak_path)
            with open(tools_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            log("✅ tools.json 빈 배열로 복구 완료", is_repair=True)

def diagnose_and_fix_error(step_name, error_output):
    """
    발생한 에러 메시지를 파싱하여 원인을 정확히 진단하고, 
    해당하는 원인에 맞춰 맞춤형 자동 수리를 수행합니다.
    """
    log("=" * 60, is_repair=True)
    log(f"🚨 [{step_name}] 단계에서 오류 발생! 진단 프로세스 시작...", is_repair=True)
    log(f"📄 수집된 에러 로그:\n{error_output[:500]}", is_repair=True)
    
    err_str = str(error_output)

    # 1. SSH 설정 관련 오류
    if "Bad configuration option" in err_str or "Could not read from remote repository" in err_str or "Permission denied (publickey)" in err_str:
        log("🔍 [진단 결과] 깃허브 SSH 인증 또는 config 인코딩 문제로 진단됨", is_repair=True)
        fix_ssh_config()
        return True

    # 2. 인코딩 관련 오류 (CP949, UnicodeDecodeError)
    if "UnicodeDecodeError" in err_str or "cp949" in err_str or "codec" in err_str:
        log("🔍 [진단 결과] 한글 인코딩(CP949/UTF-8) 충돌 오류로 진단됨", is_repair=True)
        os.environ["PYTHONUTF8"] = "1"
        os.environ["PYTHONIOENCODING"] = "utf-8"
        log("✅ [수리 완료] 환경 변수 PYTHONUTF8 및 PYTHONIOENCODING=utf-8 강제 적용 완료", is_repair=True)
        return True

    # 3. Vite 빌드/dist 관련 오류
    if "Vite build failed" in err_str or "dist" in err_str or "npm" in err_str:
        log("🔍 [진단 결과] 프론트엔드 빌드(Vite) 캐시 또는 dist 권한 오류로 진단됨", is_repair=True)
        dist_dir = os.path.join(PROJECT_DIR, "dist")
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir, ignore_errors=True)
            log("✅ [수리 완료] dist 캐시 폴더 삭제 및 초기화 완료", is_repair=True)
        return True

    # 4. JSON 파일 손상 오류
    if "json.decoder.JSONDecodeError" in err_str:
        log("🔍 [진단 결과] JSON 파일 구조 파싱 오류로 진단됨", is_repair=True)
        fix_tools_json()
        return True

    log("🔍 [진단 결과] 범용 환경 수리 실행 (SSH config & 환경 변수 재설정)", is_repair=True)
    fix_ssh_config()
    fix_env_file()
    return True

# ============================================================
# 메인 실행 및 진단/수정 지휘 로직
# ============================================================

def run_step_with_auto_repair(step_name, python_script_path):
    """스크립트를 실행하되, 에러가 나면 진단 -> 수리 -> 재실행의 자가 치유 절차를 밟습니다."""
    log(f"▶️ [{step_name}] 실행 중: {os.path.basename(python_script_path)}")
    
    python_exe = os.path.join(WORKSPACE_DIR, ".venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

    # 1차 시도
    res = subprocess.run([python_exe, python_script_path], cwd=WORKSPACE_DIR, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)
    
    if res.returncode == 0:
        log(f"✅ [{step_name}] 성공적으로 완료되었습니다!")
        return True

    # 1차 시도 실패 시 -> 원인 진단 및 맞춤 수리 실행
    error_log = res.stderr + "\n" + res.stdout
    diagnose_and_fix_error(step_name, error_log)

    # 수리 후 2차 재실행 (원인 해결 후 검증)
    log(f"🔄 [수리 완료 후 2차 재실행] [{step_name}] 시도 중...")
    res2 = subprocess.run([python_exe, python_script_path], cwd=WORKSPACE_DIR, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env)

    if res2.returncode == 0:
        log(f"🎉 [자가 수리 성공!] 원인 해결 후 [{step_name}] 단계가 정상 완료되었습니다!", is_repair=True)
        return True
    else:
        final_err = res2.stderr + "\n" + res2.stdout
        log(f"❌ [자가 수리 후 실패] 최종 오류 메시지:\n{final_err[:300]}", is_repair=True)
        return False

def main():
    log("=" * 60)
    log("⚙️ GlobalSaaSHub 진단 & 자가 수정 자동화 프로세스 가동")
    log("=" * 60)

    # 사전 헬스체크 & 수리
    fix_ssh_config()
    fix_tools_json()

    # 1단계: 데이터 수집 (에러 진단 및 맞춤 수리 포함)
    aggregator_script = os.path.join(SCRIPT_DIR, "auto_aggregator.py")
    if not run_step_with_auto_repair("1단계: AI 툴 정보 수집", aggregator_script):
        log("❌ 1단계 수집 실패로 프로세스를 종료합니다.")
        sys.exit(1)

    # 2단계: 사이트 배포 (에러 진단 및 맞춤 수리 포함)
    deploy_script = os.path.join(SCRIPT_DIR, "deploy_gh_pages.py")
    if not run_step_with_auto_repair("2단계: 사이트 배포", deploy_script):
        log("❌ 2단계 배포 실패로 프로세스를 종료합니다.")
        sys.exit(1)

    log("=" * 60)
    log("🎉 전체 수집 및 배포 프로세스가 자가 진단/수정을 거쳐 완벽히 완료되었습니다!")
    log("=" * 60)

if __name__ == "__main__":
    main()
