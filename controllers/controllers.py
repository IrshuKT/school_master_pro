from odoo import http
import os
import time
import random

class CustomSession(http.Controller):
    @classmethod
    def session_gc(cls, session_store):
        if random.random() < 0.1:  # Run on ~10% of requests
            timeout = 30  # 30 seconds for testing
            for fname in os.listdir(session_store.path):
                path = os.path.join(session_store.path, fname)
                try:
                    if os.path.getmtime(path) < time.time() - timeout:
                        os.unlink(path)
                except OSError:
                    pass

http.session_gc = CustomSession.session_gc
