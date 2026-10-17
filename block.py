import json
import hashlib
import time

class Block:
    def __init__(self, index, events, previous_hash, difficulty, timestamp=None):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.events = events
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "events": self.events,
                "previous_hash": self.previous_hash,
                "difficulty": self.difficulty,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def is_hash_valid(self):
        return self.hash.startswith("0" * self.difficulty)

    def mine(self):
        while not self.is_hash_valid():
            self.nonce += 1
            self.hash = self.calculate_hash()
        return (self.nonce, self.hash)



class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain = [self._genesis()]

    def _genesis(self):
        g = Block(0, ["GENESIS"], "0" * 64, self.difficulty, timestamp=0)
        g.mine()
        return g

    @property
    def last(self):
        return self.chain[-1]

    def new_block(self, events):
        return Block(self.last.index + 1, events, self.last.hash, self.difficulty)

    @staticmethod
    def validate_chain(chain):
        for i in range(1, len(chain)):
            cur, prev = chain[i], chain[i - 1]
            if cur.hash != cur.calculate_hash():
                return False, cur.index
            if cur.previous_hash != prev.hash:
                return False, cur.index
            if not cur.is_hash_valid():
                return False, cur.index
        return True, None