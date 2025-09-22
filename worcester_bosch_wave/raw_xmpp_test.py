#!/usr/bin/env python3
"""
Raw XMPP Protocol Test
Test the exact XMPP handshake with Worcester Bosch
"""

import socket
import time

def test_raw_xmpp():
    """Test raw XMPP connection to see server behavior"""
    
    print("🔌 Raw XMPP Connection Test")
    print("=" * 40)
    
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print("🔌 Connecting to wa2-mz36-qrmzh6.bosch.de:5222...")
        sock.connect(('wa2-mz36-qrmzh6.bosch.de', 5222))
        print("✅ TCP connection established")
        
        # Send XMPP stream start
        stream_start = '''<?xml version='1.0'?>
<stream:stream
    to='wa2-mz36-qrmzh6.bosch.de'
    xmlns='jabber:client'
    xmlns:stream='http://etherx.jabber.org/streams'
    version='1.0'>'''
    
        print("📤 Sending XMPP stream start...")
        print(f"📝 Content: {stream_start}")
        
        sock.send(stream_start.encode('utf-8'))
        
        # Receive response
        print("📨 Waiting for server response...")
        response = sock.recv(4096)
        print(f"✅ Received: {response.decode('utf-8', errors='ignore')}")
        
        # Keep connection alive to see what server expects
        print("⏱️ Keeping connection alive for 5 seconds...")
        time.sleep(5)
        
        sock.close()
        print("🔌 Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Raw connection failed: {e}")
        return False

if __name__ == "__main__":
    test_raw_xmpp()