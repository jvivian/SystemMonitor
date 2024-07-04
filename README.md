# SystemMonitor
 CPU, RAM, GPU/VRAM (via `nvidia-smi`) usage in the terminal, built using `textual`.

![`SystemMonitor` running in the terminal](image.png)

## Quickstart with Anaconda
1. Install NVIDIA drivers so `nvidia-smi` is runnable on your system.
2. clone and install the package
```bash
git clone https://github.com/jvivian/SystemMonitor && cd SystemMonitor
conda env update -f environment.yml
conda activate system-monitor
pip install ./
system-monitor
```
