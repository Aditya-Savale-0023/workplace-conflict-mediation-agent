
import networkx as nx
from collections import deque


class EvidenceGraph:
    """Graph of claims, evidence, and commitments."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id, node_type, **attributes):
        self.graph.add_node(
            node_id, node_type=node_type, **attributes
        )

    def add_relation(self, source, target, relation):
        self.graph.add_edge(
            source, target, relation=relation
        )

    def add_claim(self, claim_id, person, text):
        self.add_node(
            claim_id, "claim", person=person, text=text
        )

    def add_evidence(self, evidence_id, text, source=None):
        self.add_node(
            evidence_id, "evidence", text=text, source=source
        )

    def add_commitment(self, commitment_id, person, text,
                       fulfilled=False):
        self.add_node(
            commitment_id,
            "commitment",
            person=person,
            text=text,
            fulfilled=fulfilled
        )

    def link_evidence(self, claim_id, evidence_id,
                      supports=True):
        relation = "supports" if supports else "contradicts"
        self.add_relation(evidence_id, claim_id, relation)

    def link_commitment(self, person, commitment_id):
        self.add_node(person, "person")
        self.add_relation(person, commitment_id, "committed_to")

    def search(self, start_node, max_depth=3):
        if start_node not in self.graph:
            return []

        visited = {start_node}
        queue = deque([(start_node, 0)])
        results = []

        while queue:
            node, depth = queue.popleft()

            if depth >= max_depth:
                continue

            for neighbour in self.graph.neighbors(node):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append((neighbour, depth + 1))
                    results.append({
                        "id": neighbour,
                        **self.graph.nodes[neighbour]
                    })

        return results

    def find_related_evidence(self, claim_id):
        if claim_id not in self.graph:
            return []

        results = []

        for node, _, edge in self.graph.in_edges(
            claim_id, data=True
        ):
            attributes = self.graph.nodes[node]

            if attributes.get("node_type") == "evidence":
                results.append({
                    "id": node,
                    "text": attributes.get("text", ""),
                    "relation": edge.get("relation"),
                    "source": attributes.get("source")
                })

        return results

    def get_contradictions(self, claim_id):
        return [
            item for item in self.find_related_evidence(claim_id)
            if item["relation"] == "contradicts"
        ]

    def find_commitments(self, person=None):
        results = []

        for node, attributes in self.graph.nodes(data=True):
            if attributes.get("node_type") != "commitment":
                continue

            if person is None or attributes.get("person") == person:
                results.append({
                    "id": node,
                    **attributes
                })

        return results

    
    def to_dot(self):
        """Export the evidence graph for Streamlit's Graphviz renderer."""
        lines = ["digraph Evidence {"]
        lines.append('  graph [bgcolor="transparent"];')
        lines.append('  node [shape=box, style="rounded,filled", fillcolor="#263449", color="#7da9e8", fontcolor="white"];')
        lines.append('  edge [color="#9aa4b2", fontcolor="white"];')

        for node, data in self.graph.nodes(data=True):
            label = str(data.get("text", node))
            label = label.replace("\\", "\\\\").replace('"', '\\"')
            label = label.replace("\n", " ")
            lines.append(f'  "{node}" [label="{label}"];')

        for source, target, data in self.graph.edges(data=True):
            relation = str(data.get("relation", "related"))
            lines.append(
                f'  "{source}" -> "{target}" [label="{relation}"];'
            )

        lines.append("}")
        return "\n".join(lines)

