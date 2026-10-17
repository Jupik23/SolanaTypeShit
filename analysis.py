import random
import time
from block import Block

def mining_time_vs_difficulty(max_d=5, repeats=5):
    print("\n" + "=" * 60)
    print("ANALIZA 1: złożoność kopania a trudność")
    print("=" * 60)
    print(f"{'trudność':>9} | {'oczekiwane próby 16^d':>22} | {'średni czas [s]':>16}")
    results = []
    for d in range(1, max_d + 1):
        times = []
        for _ in range(repeats):
            b = Block(1, ["test"], "0" * 64, d)
            t0 = time.time()
            b.mine()
            times.append(time.time() - t0)
        avg = sum(times) / len(times)
        results.append((d, avg))
        print(f"{d:>9} | {16**d:>22,} | {avg:>16.4f}")
    return results

def attack_probability_formula(q, z):
    p = 1 - q
    if q >= p:
        return 1.0
    return (q / p) ** z

def attack_probability_simulation(q, z, trials=20000):
    successes = 0
    for _ in range(trials):
        deficit = z
        while 0 < deficit < z + 40:
            deficit += -1 if random.random() < q else 1
        if deficit <= 0:
            successes += 1
    return successes / trials

def attack_analysis():
    print("\n" + "=" * 60)
    print("ANALIZA 2: prawdopodobieństwo ataku 51%")
    print("=" * 60)
    shares = [0.10, 0.20, 0.30, 0.40, 0.45, 0.50, 0.51, 0.60]
    zs = [1, 3, 6]
    print(f"{'udział q':>9} | " + " | ".join(f"z={z} wzór / symul." for z in zs))
    table = {}
    for q in shares:
        row = []
        for z in zs:
            f = attack_probability_formula(q, z)
            s = attack_probability_simulation(q, z, trials=5000)
            row.append(f"{f:6.3f} / {s:6.3f}")
            table[(q, z)] = f
        print(f"{q:>9.2f} | " + " | ".join(f"{r:>14}" for r in row))
    return table

def make_plots(table, difficulty_results):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    qs = [i / 100 for i in range(1, 60)]
    plt.figure(figsize=(7, 4.5))
    for z in (1, 3, 6, 10):
        plt.plot(qs, [attack_probability_formula(q, z) for q in qs], label=f"z = {z}")
    plt.axvline(0.5, color="gray", linestyle="--")
    plt.xlabel("Udział mocy obliczeniowej atakującego (q)")
    plt.ylabel("Prawdopodobieństwo powodzenia ataku")
    plt.title("Atak 51%: szansa vs moc atakującego")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig("wykres_atak51.png", dpi=150); plt.close()

    plt.figure(figsize=(7, 4.5))
    ds, ts = zip(*difficulty_results)
    plt.semilogy(ds, ts, marker="o")
    plt.xlabel("Trudność (liczba zer w hashu)")
    plt.ylabel("Średni czas kopania [s] (skala log.)")
    plt.title("Trudność kopania a czas")
    plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig("wykres_trudnosc.png", dpi=150); plt.close()
