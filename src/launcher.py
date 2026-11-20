"""Inicializador local; nenhum texto de subprocesso e persistido nos logs."""
import argparse
import importlib.metadata
import logging
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

from src import observability as obs
from src.settings import ROOT


def dependencies():
    from packaging.requirements import Requirement
    if sys.version_info < (3, 11):
        raise RuntimeError('Python incompativel')
    for line in (ROOT / 'requirements.txt').read_text(encoding='utf-8-sig').splitlines():
        if line.strip() and not line.startswith('#'):
            req = Requirement(line)
            if req.name == 'pytest':  # Ferramenta de desenvolvimento; nao impede uso cotidiano.
                continue
            if importlib.metadata.version(req.name) not in req.specifier:
                raise RuntimeError('Dependencia incompativel')


def healthy(port):
    try:
        # Nunca encaminhar localhost a proxies configurados no computador.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f'http://127.0.0.1:{port}/_stcore/health', timeout=1) as response:
            return response.status == 200 and response.read(16).strip() == b'ok'
    except (OSError, ValueError):
        return False


def acquire(handle):
    import msvcrt
    handle.seek(0)
    try:
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except OSError:
        return False


def available_port():
    for port in range(8501, 8601):
        with socket.socket() as sock:
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except OSError:
                pass
    raise RuntimeError('Sem porta livre')


def run(open_browser=True, timeout=60):
    # Lock por projeto, fora dos logs, sem depender de PID reciclavel.
    runtime = ROOT / 'outputs'
    runtime.mkdir(exist_ok=True)
    with (runtime / 'launcher.lock').open('a+b') as lock:
        lock.seek(0, 2)
        if lock.tell() == 0:
            lock.write(b'0')
            lock.flush()
        state = runtime / 'launcher.port'
        if not acquire(lock):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    port = int(state.read_text(encoding='ascii'))
                    if 8501 <= port <= 8600 and healthy(port):
                        if open_browser:
                            webbrowser.open(f'http://127.0.0.1:{port}')
                        print('Aplicacao ja em execucao. Use a janela original para encerrar.')
                        return 0
                except (OSError, ValueError):
                    pass
                time.sleep(.3)
            raise RuntimeError('Instancia sem resposta')
        state.unlink(missing_ok=True)
        port = available_port()
        child = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', str(ROOT / 'app.py'),
            '--server.address', '127.0.0.1', '--server.port', str(port),
            '--server.headless', 'true', '--server.maxUploadSize', '30',
            '--browser.gatherUsageStats', 'false',
        ], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        try:
            deadline = time.monotonic() + timeout
            while not healthy(port):
                if child.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError('Servidor sem resposta')
                time.sleep(.3)
            state.write_text(str(port), encoding='ascii')
            obs.emit('launcher_ready', 'launcher')
            print(f'Aplicacao disponivel em http://127.0.0.1:{port}')
            print('Mantenha esta janela aberta. Para encerrar, pressione Ctrl+C nesta janela.')
            if open_browser and not webbrowser.open(f'http://127.0.0.1:{port}'):
                print('Abra o endereco acima no navegador.')
            while child.poll() is None:
                time.sleep(.5)
            if child.returncode:
                raise RuntimeError('Servidor encerrado com erro')
            return 0
        finally:
            if child.poll() is None:
                import signal
                child.send_signal(signal.CTRL_BREAK_EVENT)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.terminate()  # Somente o filho criado por este inicializador.
                    child.wait(timeout=10)
            state.unlink(missing_ok=True)


def main():
    if sys.platform == 'win32':
        import signal
        def interrupt(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGBREAK, interrupt)
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        dependencies()
        if args.check:
            print('Python e requisitos compativeis.')
            return 0
        return run(not args.no_browser)
    except KeyboardInterrupt:
        print('Aplicacao encerrada.')
        return 0
    except Exception:
        try:
            obs.emit('launcher_failed', 'launcher', logging.ERROR, sys.exc_info())
        except Exception:
            pass
        print('Falha ao iniciar. Execute INSTALAR_AMBIENTE.bat e consulte logs/errors.log (ou PORTFOLIO_LOG_DIR).')
        return 1


if __name__ == '__main__':
    sys.exit(main())
