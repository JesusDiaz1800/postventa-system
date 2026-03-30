import traceback
import os
import sys

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            # Calculate path to backend/debug_crash.log
            # This file is in backend/apps/core/debug_middleware.py
            # ../../../debug_crash.log -> backend/debug_crash.log
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'debug_crash.log')
            
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*30}\n")
                    f.write(f"CRASH DETECTED AT: {request.path}\n")
                    f.write(f"METHOD: {request.method}\n")
                    f.write(f"{'='*30}\n")
                    traceback.print_exc(file=f)
                    f.write(f"\n{'='*30}\n")
            except Exception as e:
                # Fallback to stderr if file write fails
                print(f"FAILED TO WRITE TO CRASH LOG: {e}", file=sys.stderr)
                traceback.print_exc()
            
            raise
