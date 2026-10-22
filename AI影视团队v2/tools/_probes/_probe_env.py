import sys
for m in ("cv2", "numpy", "scipy", "torch", "PIL"):
    try:
        mod = __import__(m)
        print("OK", m, getattr(mod, "__version__", "?"))
    except Exception as e:
        print("NO", m, type(e).__name__)

