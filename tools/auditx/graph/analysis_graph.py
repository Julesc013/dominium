"""Shared AuditX graph model."""

from dataclasses import dataclass, field
from typing import Dict, List
import hashlib
import json


@dataclass
class AnalysisNode:
    node_id: str
    node_type: str
    label: str
    data: Dict[str, object] = field(default_factory=dict)


@dataclass
class AnalysisEdge:
    edge_type: str
    src: str
    dst: str
    data: Dict[str, object] = field(default_factory=dict)


@dataclass
class AnalysisGraph:
    nodes: Dict[str, AnalysisNode] = field(default_factory=dict)
    edges: List[AnalysisEdge] = field(default_factory=list)

    def add_node(self, node_type, label, data=None):
        data = dict(data or {})
        node_id = "{}:{}".format(node_type, label)
        if node_id not in self.nodes:
            self.nodes[node_id] = AnalysisNode(
                node_id=node_id,
                node_type=node_type,
                label=label,
                data=data,
            )
        else:
            self.nodes[node_id].data.update(data)
        return node_id

    def add_edge(self, edge_type, src, dst, data=None):
        self.edges.append(
            AnalysisEdge(
                edge_type=edge_type,
                src=src,
                dst=dst,
                data=dict(data or {}),
            )
        )

    def to_payload(self):
        node_records = []
        for node in sorted(self.nodes.values(), key=lambda item: item.node_id):
            node_records.append(
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "label": node.label,
                    "data": dict(sorted(node.data.items())),
                }
            )

        edge_records = []
        for edge in sorted(
            self.edges,
            key=lambda item: (item.edge_type, item.src, item.dst, json.dumps(item.data, sort_keys=True)),
        ):
            edge_records.append(
                {
                    "edge_type": edge.edge_type,
                    "src": edge.src,
                    "dst": edge.dst,
                    "data": dict(sorted(edge.data.items())),
                }
            )
        return {
            "nodes": node_records,
            "edges": edge_records,
        }

    def stable_hash(self):
        payload = self.to_payload()
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

