import copy
import random
import time
from block import Blockchain
from network import Node, Network
from analysis import mining_time_vs_difficulty, attack_analysis, make_plots

def demo_supply_chain():
    print("=" * 60)
    print("DEMO 1: rejestr zdarzeń łańcucha dostaw + konsensus")
    print("=" * 60)
    net = Network(
        [Node("Producent", 300), Node("Transport", 200), Node("Hurtownia", 100), Node("Sklep", 100)],
        difficulty=3,
    )
    events = [
        ["Partia #A17 wyprodukowana (Producent)"],
        ["Partia #A17 odebrana przez Transport"],
        ["Partia #A17 dostarczona do Hurtowni"],
        ["Własność #A17 przeniesiona: Hurtownia -> Sklep"],
    ]
    wins = {n.name: 0 for n in net.nodes}
    for ev in events:
        winner, block = net.mining_round(ev)
        wins[winner] += 1
        print(f"Blok {block.index} wykopał: {winner:10s} hash={block.hash[:16]}...")
    return net

def demo_tampering(net):
    print("\n" + "=" * 60)
    print("DEMO 2: próba oszustwa (zmiana historii)")
    print("=" * 60)
    attacker = net.nodes[3]
    chain = attacker.blockchain.chain
    print("Przed zmianą:", Blockchain.validate_chain(chain))
    
    chain[2].events = ["FAŁSZYWY WPIS"]
    chain[2].hash = chain[2].calculate_hash()
    for i in range(2, len(chain)):
        chain[i].previous_hash = chain[i - 1].hash
        chain[i].nonce = 0
        chain[i].hash = chain[i].calculate_hash()
        chain[i].mine()
        
    honest = net.nodes[:3]
    blk = honest[0].blockchain.new_block(["Kolejne uczciwe zdarzenie"])
    blk.mine()
    for n in honest:
        n.blockchain.chain.append(copy.deepcopy(blk))
        
    replaced = net.consensus()
    print("Konsensus podmienił fałszywą kopię u:", replaced)

def demo_corrupted_node_recovers():
    print("\n" + "=" * 60)
    print("DEMO 3: uszkodzona kopia zostaje naprawiona przez konsensus")
    print("=" * 60)
    net = Network([Node("A", 200), Node("B", 200), Node("C", 200)], difficulty=3)
    for i in range(3):
        net.mining_round([f"zdarzenie {i+1}"])
    net.nodes[1].blockchain.chain[1].events = ["ZMANIPULOWANE"]
    replaced = net.consensus()
    print("Naprawiono u:", replaced)

if __name__ == "__main__":
    random.seed(42)
    net = demo_supply_chain()
    demo_tampering(net)
    demo_corrupted_node_recovers()
    diff_results = mining_time_vs_difficulty()
    table = attack_analysis()
    make_plots(table, diff_results)