from __future__ import annotations
import pickle
from pathlib import Path
import networkx as nx
from app import config
try:
    import torch_geometric
    _HAS_PYG = True
except Exception:
    _HAS_PYG = False

class FraudModel:

    def __init__(self, version: str) -> None:
        self.name = 'fraud'
        self.version = version
        self.algo = 'pyg-gnn' if _HAS_PYG else 'networkx-ppr'
        self._score: dict[str, float] = {}

    def fit(self, txns: list[tuple]) -> 'FraudModel':
        g = nx.Graph()
        seeds: dict[str, float] = {}
        for party_id, mcc, flagged in txns:
            pn, mn = (f'p:{party_id}', f'm:{mcc}')
            w = 3.0 if flagged else 1.0
            if g.has_edge(pn, mn):
                g[pn][mn]['weight'] += w
            else:
                g.add_edge(pn, mn, weight=w)
            if flagged:
                seeds[pn] = seeds.get(pn, 0.0) + 1.0
        if g.number_of_nodes() == 0:
            return self
        personalization = {n: seeds.get(n, 0.0) for n in g.nodes()}
        if sum(personalization.values()) == 0:
            personalization = None
        pr = nx.pagerank(g, alpha=0.85, personalization=personalization, weight='weight')
        party_scores = {n[2:]: v for n, v in pr.items() if n.startswith('p:')}
        if party_scores:
            hi = max(party_scores.values()) or 1.0
            self._score = {k: v / hi for k, v in party_scores.items()}
        return self

    def score(self, party_id: str, flagged_ratio: float, event: dict | None=None) -> float:
        base = self._score.get(party_id, 0.0)
        s = 0.6 * base + 0.4 * min(flagged_ratio * 3.0, 1.0)
        if event and event.get('event_type') == 'large_transfer_attempt':
            s = min(1.0, s + min(event.get('amount', 0.0) / 5000.0, 0.4))
        return round(min(1.0, s), 4)

    def _path(self) -> Path:
        return config.ARTIFACTS_DIR / f'{self.name}.pkl'

    def save(self) -> None:
        with open(self._path(), 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls) -> 'FraudModel':
        with open(config.ARTIFACTS_DIR / 'fraud.pkl', 'rb') as f:
            return pickle.load(f)
