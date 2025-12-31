# cc

## Virtual Camera Sink Abstraction

This repo defines a minimal, cross-platform abstraction for writing frames to
virtual camera devices.

```python
from virtual_camera import create_default_sink

sink = create_default_sink()

sink.open(width=1280, height=720, fps=30.0)
try:
    sink.write(b"...")
finally:
    sink.close()
```

Platform notes:
- **Windows:** Consider OBS VirtualCam or DirectShow-based implementations.
- **macOS:** Consider AVFoundation with a CoreMediaIO extension.
- **Linux:** Consider using v4l2loopback to create a device node for frames.
