"""Utils"""
import time
import random

def fake_stream(text: str):
    """Emulate streaming effect"""
    for ch in text:
        time.sleep(random.uniform(0.01, 0.05))
        yield ch
