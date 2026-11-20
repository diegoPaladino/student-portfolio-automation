"""Inicializacao Windows com dados sinteticos e processos de propriedade do teste."""
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from src import launcher


def test_requirements_and_health():
    launcher.dependencies()
    assert not launcher.healthy(1)


@pytest.mark.skipif(sys.platform != 'win32', reason='Inicializador Windows')
def test_server_reuse_busy_port_and_shutdown(tmp_path):
    env = dict(os.environ, PORTFOLIO_DATA_DIR=str(tmp_path / 'data'),
               PORTFOLIO_LOG_DIR=str(tmp_path / 'logs'))
    # Simula outro aplicativo: sua porta deve permanecer intacta.
    with socket.socket() as occupied:
        try:
            occupied.bind(('127.0.0.1', 8501))
        except OSError:
            pytest.skip('Porta de teste ja ocupada')
        occupied.listen()
        child = subprocess.Popen([sys.executable, '-m', 'src.launcher', '--no-browser'],
                                 env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        state = launcher.ROOT / 'outputs' / 'launcher.port'
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and child.poll() is None:
                if state.exists() and launcher.healthy(int(state.read_text())):
                    break
                time.sleep(.2)
            assert child.poll() is None
            port = int(state.read_text())
            assert port != 8501 and launcher.healthy(port)
            duplicate = subprocess.run([sys.executable, '-m', 'src.launcher', '--no-browser'],
                                       env=env, capture_output=True, timeout=15)
            assert duplicate.returncode == 0
            assert b'ja em execucao' in duplicate.stdout
            assert child.poll() is None
        finally:
            if child.poll() is None:
                child.send_signal(signal.CTRL_BREAK_EVENT)
            child.communicate(timeout=25)
        assert not state.exists()
        assert not launcher.healthy(port)
        assert occupied.getsockname()[1] == 8501


def test_browser_only_after_health(tmp_path):
    # Caminho de reutilizacao: nao abre navegador enquanto health falha.
    (tmp_path / 'outputs').mkdir()
    (tmp_path / 'outputs' / 'launcher.port').write_text('8502')
    with patch.object(launcher, 'ROOT', tmp_path), patch.object(launcher, 'acquire', return_value=False), \
         patch.object(launcher, 'healthy', side_effect=[False, True]), \
         patch.object(launcher.time, 'sleep'), patch.object(launcher.webbrowser, 'open') as browser:
        assert launcher.run() == 0
        browser.assert_called_once_with('http://127.0.0.1:8502')
