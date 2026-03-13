import os
import shutil
import subprocess
import sys
import platform

# --- AUTOMATED ENVIRONMENT SETUP for PyImageJ ---
def setup_env():
    current_os = platform.system()

    # 1. Java Detection
    if not os.environ.get('JAVA_HOME'):
        try:
            if current_os == "Darwin":  # Mac
                try:
                    # Specifically ask for the newest version (17 or higher)
                    path = subprocess.check_output(['/usr/libexec/java_home', '-v', '17+'], text=True).strip()
                    os.environ['JAVA_HOME'] = path
                except Exception:
                    # Fallback to the Zulu path directly if the command fails
                    zulu_path = "/Library/Java/JavaVirtualMachines/zulu-25.jdk/Contents/Home"
                    if os.path.exists(zulu_path):
                        os.environ['JAVA_HOME'] = zulu_path
            elif current_os == "Windows":  # Windows
                java_cmd = shutil.which("java")
                if java_cmd:
                    # Climbs out of bin/java.exe to the root folder
                    os.environ['JAVA_HOME'] = os.path.dirname(os.path.dirname(java_cmd))
        except Exception:
            pass

    # 2. Maven Path Injection (Fixes 'mvn not found')
    if not shutil.which("mvn"):
        if current_os == "Darwin":
            # Add common Homebrew locations to the active PATH
            for p in ["/opt/homebrew/bin", "/usr/local/bin"]:
                if os.path.exists(p) and p not in os.environ["PATH"]:
                    os.environ["PATH"] += os.pathsep + p

    # 3. macOS Library Bridge (Fixes libjli.dylib error)
    if current_os == "Darwin" and os.environ.get('JAVA_HOME'):
        libjli = os.path.join(os.environ['JAVA_HOME'], "lib", "jli")
        if os.path.exists(libjli):
            # Prepend to DYLD_LIBRARY_PATH
            existing = os.environ.get('DYLD_LIBRARY_PATH', '')
            os.environ['DYLD_LIBRARY_PATH'] = f"{libjli}:{existing}".strip(':')