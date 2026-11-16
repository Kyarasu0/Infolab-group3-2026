"""ADXL345 を 800Hz で読んで、ブラウザにリアルタイムで流す最小のバックエンド。
  python3 server.py              # ラズパイで実行 → ブラウザで http://<ラズパイのIP>:8000
  python3 server.py --sim        # センサなしで疑似データを流す（画面の確認用）
追加のインストールは不要（smbus は PDF の手順で入っている）
"""
import argparse, csv, json, math, random, threading, time
from datetime import datetime
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--port", type=int, default=8000)
p.add_argument("--sim", action="store_true", help="疑似データを流す")
a = p.parse_args()

RATE, ADDR, LSB = 800, 0x53, 0.0039      # 出力レート[Hz]、I2Cアドレス、1LSBあたりのg（full-res）
buf = deque(maxlen=RATE * 5)             # 直近5秒分 (x, y, z)
total = 0                                # 今の記録のサンプル数
running = False                          # 記録中か（ストップ中はセンサを読んでも捨てる）
csv_file = csv_w = csv_path = None
lock = threading.Lock()

logs = Path(__file__).parent / "raw_logs"
logs.mkdir(exist_ok=True)


def start():
    """再生：新しい CSV を作って、最初から記録する"""
    global total, running, csv_file, csv_w, csv_path
    with lock:
        if running:
            return
        buf.clear()
        total = 0
        csv_path = logs / f"{datetime.now():%Y%m%d_%H%M%S}.csv"
        csv_file = open(csv_path, "w", newline="", buffering=1)   # 1行ごとに書き出す
        csv_w = csv.writer(csv_file)
        csv_w.writerow(["seq", "t_s", "x_g", "y_g", "z_g"])
        running = True
    print(f"記録開始：{csv_path}", flush=True)


def stop():
    """ストップ：CSV を閉じる"""
    global running
    with lock:
        if not running:
            return
        running = False
        csv_file.close()
    print(f"記録停止：{csv_path}（{total} サンプル）", flush=True)


def push(x, y, z):
    global total
    with lock:
        if not running:
            return
        buf.append((x, y, z))
        csv_w.writerow([total, f"{total / RATE:.5f}", f"{x:.4f}", f"{y:.4f}", f"{z:.4f}"])
        total += 1


def read_sensor():
    import smbus
    bus = smbus.SMBus(1)
    if bus.read_byte_data(ADDR, 0x00) != 0xE5:
        raise SystemExit("ADXL345 が見つかりません（i2cdetect -y 1 で確認）")
    bus.write_byte_data(ADDR, 0x2C, 0x0D)   # 800Hz
    bus.write_byte_data(ADDR, 0x31, 0x09)   # full-res・±4g
    bus.write_byte_data(ADDR, 0x38, 0x9F)   # FIFO（ストリームモード）
    bus.write_byte_data(ADDR, 0x2D, 0x08)   # 測定開始
    while True:
        for _ in range(bus.read_byte_data(ADDR, 0x39) & 0x3F):   # FIFO に溜まっている個数
            d = bus.read_i2c_block_data(ADDR, 0x32, 6)
            v = [d[i] | d[i + 1] << 8 for i in (0, 2, 4)]
            push(*[(n - 65536 if n > 32767 else n) * LSB for n in v])
        time.sleep(0.005)


def simulate():
    t0, n = time.monotonic(), 0
    while True:
        while n < int((time.monotonic() - t0) * RATE):
            n += 1
            t = n / RATE
            push(0.3 * math.sin(2 * math.pi * 5 * t) + random.gauss(0, 0.02),
                 0.1 * math.sin(2 * math.pi * 20 * t) + random.gauss(0, 0.02),
                 1 + random.gauss(0, 0.02))
        time.sleep(0.005)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            sent = total
            try:
                while True:
                    time.sleep(0.1)
                    with lock:
                        if total < sent:                        # 再生し直して、番号が0に戻った
                            sent = 0
                        new, sent = min(total - sent, len(buf)), total
                        first = total - new                     # 先頭の行の seq
                        rows = list(buf)[len(buf) - new:] if new else []
                    msg = {"run": running, "first": first, "rate": RATE, "x": [r[0] for r in rows], "y": [r[1] for r in rows], "z": [r[2] for r in rows]}
                    self.wfile.write(f"data: {json.dumps(msg, separators=(',', ':'))}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return
        elif self.path == "/":
            body = (Path(__file__).parent / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")   # 古い画面が残らないようにする
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path in ("/run", "/stop"):
            (start if self.path == "/run" else stop)()
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404)


start()                                  # 起動したら、すぐ記録を始める（ストップボタンで止められる）
threading.Thread(target=simulate if a.sim else read_sensor, daemon=True).start()
print(f"http://0.0.0.0:{a.port} で待ち受け中（Ctrl+C で終了）")
ThreadingHTTPServer(("0.0.0.0", a.port), Handler).serve_forever()
