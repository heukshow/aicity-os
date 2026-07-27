"""
GlobalSaaSHub - SSH 기반 자동 배포 스크립트
=====================================================================
SSH Key 방식으로 깃허브에 자동 배포합니다.
비밀번호/토큰 로그인이나 브라우저 인증이 필요 없으므로 백그라운드에서도 100% 동작합니다.
"""
import os
import sys
import shutil
import subprocess
import datetime
import traceback

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

REPO_OWNER = "heukshow"
REPO_NAME = "aicity-os"
BRANCH = "gh-pages"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
LOG_FILE = os.path.join(SCRIPT_DIR, "deploy_log.txt")

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    sys.stdout.flush()
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def run_cmd(cmd, cwd):
    env = {**os.environ, "GIT_SSH_COMMAND": "ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519_deploy"}
    res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout = res.stdout.decode('utf-8', errors='ignore').strip()
    stderr = res.stderr.decode('utf-8', errors='ignore').strip()
    return res.returncode == 0, stdout, stderr

def build_site():
    log("🔨 recategorize_tools.py 실행 및 마이크로 카테고리 재정돈...")
    recat_script = os.path.join(SCRIPT_DIR, "recategorize_tools.py")
    subprocess.run([sys.executable, recat_script], cwd=PROJECT_DIR)

    log("🔨 Programmatic SEO 페이지 및 sitemap.xml 생성 시작...")
    seo_script = os.path.join(SCRIPT_DIR, "generate_seo_pages.py")
    subprocess.run([sys.executable, seo_script], cwd=PROJECT_DIR)

    dist_dir = os.path.join(PROJECT_DIR, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)

    log("🔨 Vite 사이트 빌드 시작...")
    env = {**os.environ, "PYTHONUTF8": "1"}
    res = subprocess.run("npm run build", shell=True, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if res.returncode == 0 and os.path.exists(dist_dir) and any(os.scandir(dist_dir)):
        log("✅ 빌드 성공!")
        return True
    log(f"❌ 빌드 실패: {res.stderr.decode('utf-8', errors='ignore')[:300]}")
    return False




def deploy_via_ssh():
    dist_dir = os.path.join(PROJECT_DIR, "dist")
    git_dir = os.path.join(dist_dir, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir, ignore_errors=True)

    ssh_url = f"git@github.com:{REPO_OWNER}/{REPO_NAME}.git"
    msg = f"auto-deploy: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    cmds = [
        f"git init",
        f'git config user.name "GlobalSaaSHub-Bot"',
        f'git config user.email "bot@coshuma.com"',
        f"git remote add origin {ssh_url}",
        f"git checkout -b {BRANCH}",
        f"git add .",
        f'git commit -m "{msg}"',
        f"git push -f origin {BRANCH}"
    ]

    for cmd in cmds:
        ok, out, err = run_cmd(cmd, dist_dir)
        if not ok:
            if "nothing to commit" in out or "nothing to commit" in err:
                continue
            log(f"❌ 명령어 실패: {cmd}\nERR: {err}")
            return False

    log("🎉 SSH를 통한 gh-pages 배포 완전 성공!")
    return True

def main():
    log("=" * 60)
    log("GlobalSaaSHub SSH 자동 배포 시작")
    log("=" * 60)
    if not build_site():
        sys.exit(1)
    if not deploy_via_ssh():
        sys.exit(1)
    log("=" * 60)

if __name__ == "__main__":
    main()
