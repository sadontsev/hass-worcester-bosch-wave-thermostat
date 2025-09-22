#!/usr/bin/env python3
"""
Quick network check for Worcester Bosch XMPP endpoint.
Tests DNS resolution and TCP connectivity to wa2-mz36-qrmzh6.bosch.de:5222.
This runs on your current machine; for Home Assistant, run a similar check via SSH add-on.
"""
import socket
import sys
import time

HOST = "wa2-mz36-qrmzh6.bosch.de"
PORT = 5222


def dns_lookup(host: str):
    try:
        infos = socket.getaddrinfo(host, None)
        addrs = sorted({i[4][0] for i in infos})
        print(f"DNS OK: {host} -> {', '.join(addrs)}")
        return True
    except Exception as e:
        print(f"DNS FAIL: {host} -> {e}")
        return False


def tcp_connect(host: str, port: int, timeout=5):
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(2)
            print(f"TCP OK: connected to {host}:{port}")
            # Try a minimal read to confirm server responds (optional)
            try:
                time.sleep(0.5)
                data = s.recv(64)
                if data:
                    print(f"RECV: {data[:64]!r}")
            except Exception:
                pass
            return True
    except Exception as e:
        print(f"TCP FAIL: {host}:{port} -> {e}")
        return False


if __name__ == "__main__":
    ok_dns = dns_lookup(HOST)
    ok_tcp = tcp_connect(HOST, PORT) if ok_dns else False
    sys.exit(0 if (ok_dns and ok_tcp) else 1)
