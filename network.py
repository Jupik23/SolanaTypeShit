import copy
from block import Blockchain

class Node:
    def __init__(self, name, hash_power):
        self.name = name
        self.hash_power = hash_power
        self.blockchain = None

    def try_mine(self, candidate):
        for _ in range(self.hash_power):
            candidate.nonce += 1
            candidate.hash = candidate.calculate_hash()
            if candidate.is_hash_valid():
                return True
        return False

class Network:
    def __init__(self, nodes, difficulty=3):
        self.nodes = nodes
        for n in nodes:
            n.blockchain = Blockchain(difficulty)

    def mining_round(self, events):
        candidates = {n.name: n.blockchain.new_block(events) for n in self.nodes}
        while True:
            for n in self.nodes:
                if n.try_mine(candidates[n.name]):
                    winner, block = n, candidates[n.name]
                    self._broadcast(winner, block)
                    return winner.name, block

    def _broadcast(self, winner, block):
        for n in self.nodes:
            chain = n.blockchain.chain
            ok = (
                block.index == chain[-1].index + 1
                and block.previous_hash == chain[-1].hash
                and block.hash == block.calculate_hash()
                and block.is_hash_valid()
            )
            if ok:
                chain.append(copy.deepcopy(block))

    def consensus(self):
        best = None
        for n in self.nodes:
            valid, _ = Blockchain.validate_chain(n.blockchain.chain)
            if valid and (best is None or len(n.blockchain.chain) > len(best)):
                best = n.blockchain.chain
        replaced = []
        for n in self.nodes:
            if n.blockchain.chain is not best and (
                not Blockchain.validate_chain(n.blockchain.chain)[0]
                or len(n.blockchain.chain) < len(best)
            ):
                n.blockchain.chain = copy.deepcopy(best)
                replaced.append(n.name)
        return replaced
