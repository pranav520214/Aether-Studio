#!/usr/bin/env python3
"""
Privantrix AI OS - Main Entry Point
CLI interface using Typer
"""

import os
import sys
from pathlib import Path

# Add src to path
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="privantrix", help="Privantrix AI OS CLI")
console = Console()


@app.command()
def init():
    """Initialize the Privantrix AI OS environment"""
    from bootstrap import BootstrapInstaller
    installer = BootstrapInstaller(str(base_dir))
    success = installer.run()
    if not success:
        raise typer.Exit(1)


@app.command()
def hardware():
    """Detect and benchmark hardware"""
    from src.hardware import HardwareDetector
    
    console.print("[bold blue]Hardware Detection[/bold blue]")
    detector = HardwareDetector()
    info = detector.detect_all()
    
    table = Table(title="System Information")
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("OS", f"{info.os_name} {info.os_version}")
    table.add_row("Python", info.python_version)
    table.add_row("CPU Cores", str(info.cpu.cores_logical))
    table.add_row("RAM Total", f"{info.ram.total_gb:.1f} GB")
    table.add_row("GPU Count", str(len(info.gpus)))
    
    if info.gpus:
        for gpu in info.gpus:
            table.add_row("GPU", f"{gpu.name} ({gpu.vram_total_gb:.1f} GB)")
    
    console.print(table)
    
    # Run benchmarks
    console.print("\n[bold blue]Running Benchmarks...[/bold blue]")
    results = detector.benchmark()
    
    bench_table = Table(title="Benchmark Results")
    bench_table.add_column("Test", style="cyan")
    bench_table.add_column("Score", style="green")
    
    bench_table.add_row("CPU Score", str(results["cpu_score"]))
    bench_table.add_row("Memory Bandwidth", f"{results['memory_bandwidth_gb_s']} GB/s")
    bench_table.add_row("Disk Read", f"{results['disk_read_mb_s']} MB/s")
    bench_table.add_row("Disk Write", f"{results['disk_write_mb_s']} MB/s")
    bench_table.add_row("Overall Score", str(results["overall_score"]))
    
    console.print(bench_table)


@app.command()
def lmstudio(host: str = "localhost", port: int = 1234):
    """Check LM Studio status"""
    from src.lmstudio import LMStudioClient
    
    client = LMStudioClient(host=host, port=port)
    
    if client.health_check():
        console.print("[green]✓ LM Studio is available[/green]")
        
        models = client.get_models()
        if models:
            table = Table(title="Available Models")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            
            for model in models:
                table.add_row(model.id, model.name)
            
            console.print(table)
    else:
        console.print("[red]✗ LM Studio is not available[/red]")
        console.print(f"Make sure LM Studio is running on {host}:{port}")


@app.command()
def config(show: bool = True):
    """Show or edit configuration"""
    from src.config import ConfigurationManager
    
    manager = ConfigurationManager()
    config = manager.load()
    
    if show:
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Base Directory", config.base_dir)
        table.add_row("Environment", config.environment)
        table.add_row("Debug Mode", str(config.debug))
        table.add_row("Default Model", config.model.default_model)
        table.add_row("Log Level", config.logging.level)
        
        console.print(table)


@app.command()
def memory(query: str = ""):
    """Search memory or show memory status"""
    from src.memory import init_memory
    
    memory_mgr = init_memory(str(base_dir))
    
    if query:
        results = memory_mgr.search_memory(query)
        if results:
            console.print(f"[green]Found {len(results)} results for '{query}'[/green]")
            for r in results[:5]:
                content = r.get("content", str(r.get("data", "")))[:100]
                console.print(f"  - {content}...")
        else:
            console.print(f"[yellow]No results found for '{query}'[/yellow]")
    else:
        console.print(f"[cyan]Working Memory Size: {memory_mgr.working.size()}[/cyan]")


@app.command()
def planner():
    """Show planner status"""
    from src.planner import init_planner
    
    planner = init_planner(str(base_dir))
    progress = planner.get_progress()
    
    table = Table(title="Planner Progress")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Task Progress", f"{progress['task_progress']*100:.1f}%")
    table.add_row("Milestone Progress", f"{progress['milestone_progress']*100:.1f}%")
    table.add_row("Total Tasks", str(progress['total_tasks']))
    table.add_row("Completed Tasks", str(progress['completed_tasks']))
    table.add_row("Pending Tasks", str(progress['pending_tasks']))
    
    console.print(table)


@app.command()
def dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Start the web dashboard"""
    console.print(f"[bold blue]Starting dashboard on http://{host}:{port}[/bold blue]")
    console.print("[yellow]Dashboard implementation pending - use API directly[/yellow]")


@app.command()
def verify():
    """Verify installation"""
    console.print("[bold blue]Verifying Installation...[/bold blue]\n")
    
    checks = [
        ("Source files", (base_dir / "src").exists()),
        ("Config directory", (base_dir / "configs").exists()),
        ("Database directory", (base_dir / "database").exists()),
        ("Requirements file", (base_dir / "requirements.txt").exists()),
        ("README file", (base_dir / "README.md").exists()),
    ]
    
    all_passed = True
    for name, passed in checks:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        console.print("\n[green]All checks passed![/green]")
    else:
        console.print("\n[red]Some checks failed.[/red]")
        raise typer.Exit(1)


def cli():
    """Main CLI entry point"""
    app()


if __name__ == "__main__":
    cli()
