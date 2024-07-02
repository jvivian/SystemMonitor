import asyncio
import datetime
from pathlib import Path
import psutil
import subprocess
from textual_plotext import PlotextPlot
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text

class GPUStats:
    def __init__(self):
        self.temp = 0
        self.gpu = 0
        self.gpu_vram = 0

    async def update(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,utilization.memory", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                check=True
            )
            temp, perc_gpu, perc_mem = map(int, result.stdout.strip().split(','))
            self.temp = temp
            self.gpu = perc_gpu
            self.gpu_vram = perc_mem
        except subprocess.CalledProcessError:
            # Handle error (e.g., NVIDIA GPU not found)
            pass
        except TypeError:
            # header
            pass

class UsageGraph(PlotextPlot):
    """A widget for plotting usage data."""
    # marker = var("dot")

    def __init__(
        self,
        title: str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._title = title
        self._unit = "%"
        self._data: list[float] = []
        self._time: list[str] = []

    def on_mount(self) -> None:
        """Set up the plot."""
        self.plt.title(self._title)
        self.plt.xlabel("Time")
        self.plt.ylabel(self._unit)
        self.plt.ylim(0, 100)

    def replot(self) -> None:
        """Redraw the plot."""
        self.plt.clear_data()
        self.plt.plot(self._time, self._data, marker=self.marker, color="blue")
        self.refresh()

    def update(self, value: float) -> None:
        """Update the data for the usage plot."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self._data.append(value)
        self._time.append(current_time)
        if len(self._data) > 60:  # Keep only the last 60 data points
            self._data.pop(0)
            self._time.pop(0)
        self.replot()

    def watch_marker(self) -> None:
        """React to the marker being changed."""
        self.replot()

class SystemMonitor(App):
    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = Path(__file__).parent / 'styles.css'

    cpu_usage = reactive(0.0)
    ram_usage = reactive(0.0)
    gpu_usage = reactive(0.0)
    gpu_memory = reactive(0.0)

    def __init__(self):
        super().__init__()
        self.gpu_stats = GPUStats()

    def compose(self) -> ComposeResult:
        yield Header()
        # yield Container(
        #     Static(id="graph_cpu", classes="graph"),
        #     Static(id="graph_ram", classes="graph"),
        #     Static(id="graph_gpu", classes="graph"),
        #     id="graphs"
        # )
        yield Container(
            Static(id="cpu_bar"),
            Static(id="ram_bar"),
            Static(id="gpu_bar"),
            Static(id="gpu_memory_bar"),
        )
        yield Footer()

    def on_mount(self):
        self.set_interval(1, self.update_stats)

    async def update_stats(self):
        self.cpu_usage = psutil.cpu_percent()
        self.ram_usage = psutil.virtual_memory().percent
        await self.gpu_stats.update()
        self.gpu_usage = self.gpu_stats.gpu
        self.gpu_memory = self.gpu_stats.gpu_vram
        self.gpu_temp = self.gpu_stats.temp

        self.update_bars()
        self.update_graphs()

    def update_bars(self):
        self.query_one("#cpu_bar").update(self.create_bar("CPU", self.cpu_usage))
        self.query_one("#ram_bar").update(self.create_bar("RAM", self.ram_usage))
        self.query_one("#gpu_bar").update(self.create_bar("GPU", self.gpu_usage))
        self.query_one("#gpu_memory_bar").update(self.create_bar("GPU Memory", self.gpu_memory))
    
    def create_bar(self, label: str, value: float) -> Panel:
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=50),
            TextColumn("[bold]{task.percentage:.0f}%")
        )
        progress.add_task(label, total=100, completed=value)
        return Panel(progress, title=f"{label} Usage", border_style="bright_blue")

    def update_graphs(self):
        # This is a placeholder. In a real implementation, you'd update the graphs here.
        # You might use a library like plotext or create custom widgets with Textual
        pass

def main():
    app = SystemMonitor()
    app.run()


if __name__ == "__main__":
    main()
