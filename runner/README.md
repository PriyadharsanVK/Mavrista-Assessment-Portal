# Isolated coding runner

Coding submissions use a stdin/stdout contract: each input test is passed to the program's standard input and trimmed standard output is compared with the expected output. Java programs use `public class Main` in `Main.java`; Python uses `main.py`; JavaScript uses `main.js`; C++ uses `main.cpp`; C uses `main.c`.

Build the image from this folder:

```text
docker build -t assessment-runner:local .
```

At runtime the server starts one container per question run. Containers have no network, read-only source mounts, dropped Linux capabilities, a non-root UID, memory/CPU/process limits, and a small writable `/tmp`. The server refuses coding execution when Docker or the image is unavailable.

For real assessments, run the API and runner on a dedicated host with Docker configured safely, restrict access to the Docker daemon, add operational monitoring, and test the container limits in the intended deployment environment.
