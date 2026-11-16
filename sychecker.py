#!/usr/bin/env python3
"""
SYchecker - Check your computer's components and see how good they are.
"""

import time
import math
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

try:
    import psutil
    import cpuinfo
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Missing dependencies. Please run:")
    print("  pip install -r requirements.txt")
    raise SystemExit(1)

console = Console()


def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    brand = info.get("brand_raw", "Unknown CPU")
    arch = info.get("arch_string_raw", "")
    cores = psutil.cpu_count(logical=False) or 1
    threads = psutil.cpu_count(logical=True) or 1
    return {
        "brand": brand,
        "arch": arch,
        "cores": cores,
        "threads": threads,
    }


def get_ram_info():
    mem = psutil.virtual_memory()
    total_gb = round(mem.total / (1024 ** 3), 1)
    return {"total_gb": total_gb}


def cpu_work(n: int = 12_000_000) -> float:
    """Simple CPU-bound work: count primes up to n."""
    if n < 2:
        return 0.0
    count = 0
    for i in range(2, n):
        is_prime = True
        limit = int(math.sqrt(i)) + 1
        for j in range(2, limit):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return float(count)


def run_single_core() -> float:
    """Return operations per second for single-core test."""
    start = time.perf_counter()
    cpu_work(8_000_000)
    elapsed = time.perf_counter() - start
    # Higher is better. Scale later.
    return 8_000_000 / elapsed if elapsed > 0 else 0.0


def run_multi_core(threads: int) -> float:
    """Run the same work across multiple processes."""
    workers = max(1, threads)
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(cpu_work, 4_000_000) for _ in range(workers)]
        for f in futures:
            f.result()
    elapsed = time.perf_counter() - start
    total_work = workers * 4_000_000
    return total_work / elapsed if elapsed > 0 else 0.0


def run_memory_test() -> float:
    """Rough memory bandwidth / throughput test (MB/s style)."""
    size = 64 * 1024 * 1024  # 64 MB
    data = bytearray(size)
    start = time.perf_counter()
    # Write pass
    for i in range(0, size, 4096):
        data[i] = 1
    # Read pass
    total = 0
    for i in range(0, size, 4096):
        total += data[i]
    elapsed = time.perf_counter() - start
    # Approximate MB/s (two passes)
    mb = (size * 2) / (1024 * 1024)
    return mb / elapsed if elapsed > 0 else 0.0


def calculate_scores(single_ops: float, multi_ops: float, mem_bw: float, threads: int):
    """
    Produce human-friendly scores.
    Rough calibration target:
      - Decent mid-range desktop ~ 2500-3500 overall
      - High-end / top-tier systems approach ~ 5500-6200
    """
    # Raw-ish scores
    single_score = single_ops / 2800.0          # tuned so strong single-core ~ 2500-3000
    multi_score = multi_ops / (threads * 900.0) # normalize a bit by thread count
    mem_score = mem_bw / 18.0                   # rough

    single = max(1, int(single_score))
    multi = max(1, int(multi_score * threads * 0.85))  # scale multi higher
    memory = max(1, int(mem_score))

    # Weighted overall (CPU heavy)
    overall = int(single * 0.35 + (multi / max(threads, 1)) * 0.45 + memory * 0.20)
    # Final boost so top systems land near 6000
    overall = int(overall * 1.15)

    return {
        "single": single,
        "multi": multi,
        "memory": memory,
        "overall": overall,
    }


def tier_label(score: int) -> str:
    if score >= 5500:
        return "Top Tier"
    if score >= 4000:
        return "High-End"
    if score >= 2500:
        return "Mid-Range"
    if score >= 1200:
        return "Entry-Level"
    return "Low"


def main():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SYchecker[/bold cyan]\n[dim]Check your computer's components and see how good they are[/dim]",
        border_style="cyan"
    ))
    console.print()

    with console.status("[bold green]Detecting hardware..."):
        cpu = get_cpu_info()
        ram = get_ram_info()

    console.print(f"[bold]CPU:[/bold]  {cpu['brand']}")
    console.print(f"      {cpu['cores']} cores / {cpu['threads']} threads  ({cpu['arch']})")
    console.print(f"[bold]RAM:[/bold]  {ram['total_gb']} GB")
    console.print()

    with console.status("[bold green]Running single-core test..."):
        single_ops = run_single_core()

    with console.status("[bold green]Running multi-core test..."):
        multi_ops = run_multi_core(cpu["threads"])

    with console.status("[bold green]Running memory test..."):
        mem_bw = run_memory_test()

    scores = calculate_scores(single_ops, multi_ops, mem_bw, cpu["threads"])
    tier = tier_label(scores["overall"])

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold")
    table.add_column(justify="right")

    table.add_row("Single-core", f"{scores['single']:,}")
    table.add_row("Multi-core", f"{scores['multi']:,}")
    table.add_row("Memory", f"{scores['memory']:,}")
    table.add_row("", "")
    table.add_row("[bold cyan]Overall Score[/bold cyan]", f"[bold cyan]{scores['overall']:,}[/bold cyan]")
    table.add_row("", f"[bold]{tier}[/bold]")

    console.print(Panel(table, title="[bold]Results[/bold]", border_style="green"))
    console.print()
    console.print("[dim]Scores are approximate and relative. Higher is better. Top-tier systems aim for ~6000.[/dim]")
    console.print()


if __name__ == "__main__":
    # Required on Windows for multiprocessing
    mp.freeze_support()
    main()
