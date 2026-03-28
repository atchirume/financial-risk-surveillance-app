import pandas as pd
import networkx as nx

from config import RANDOM_SEED
from engine.helpers import minmax_scale

def build_graph_features(transactions, customer_networks, corporate_links):
    required_txn_cols = ["customer_id", "counterparty_customer_id", "amount"]
    for col in required_txn_cols:
        if col not in transactions.columns:
            return pd.DataFrame(columns=[
                "customer_id", "graph_in_degree", "graph_out_degree",
                "graph_degree_centrality", "graph_betweenness",
                "graph_pagerank", "graph_clustering", "graph_risk_score",
                "corporate_link_strength",
            ])

    txn_df = transactions[required_txn_cols].copy()
    txn_df = txn_df.dropna(subset=["customer_id", "counterparty_customer_id"])
    txn_df["customer_id"] = pd.to_numeric(txn_df["customer_id"], errors="coerce")
    txn_df["counterparty_customer_id"] = pd.to_numeric(txn_df["counterparty_customer_id"], errors="coerce")
    txn_df["amount"] = pd.to_numeric(txn_df["amount"], errors="coerce").fillna(0)
    txn_df = txn_df.dropna(subset=["customer_id", "counterparty_customer_id"])

    txn_edges = txn_df.groupby(["customer_id", "counterparty_customer_id"], as_index=False).agg(
        edge_amount=("amount", "sum"),
        edge_count=("amount", "size"),
    )

    G = nx.DiGraph()
    for row in txn_edges.to_dict("records"):
        src = int(row["customer_id"])
        dst = int(row["counterparty_customer_id"])
        if src == dst:
            continue
        G.add_edge(src, dst, weight=float(row["edge_amount"]), count=int(row["edge_count"]), relation="txn")

    if customer_networks is not None and len(customer_networks) > 0 and {"from_customer_id", "to_customer_id"}.issubset(customer_networks.columns):
        network_df = customer_networks[["from_customer_id", "to_customer_id"]].dropna().copy()
        network_df["from_customer_id"] = pd.to_numeric(network_df["from_customer_id"], errors="coerce")
        network_df["to_customer_id"] = pd.to_numeric(network_df["to_customer_id"], errors="coerce")
        network_df = network_df.dropna()

        for row in network_df.to_dict("records"):
            src = int(row["from_customer_id"])
            dst = int(row["to_customer_id"])
            if src == dst:
                continue
            if G.has_edge(src, dst):
                G[src][dst]["weight"] += 1.0
                G[src][dst]["count"] += 1
            else:
                G.add_edge(src, dst, weight=1.0, count=1, relation="network")

    if len(G.nodes()) == 0:
        return pd.DataFrame(columns=[
            "customer_id", "graph_in_degree", "graph_out_degree",
            "graph_degree_centrality", "graph_betweenness",
            "graph_pagerank", "graph_clustering", "graph_risk_score",
            "corporate_link_strength",
        ])

    degree_centrality = nx.degree_centrality(G)

    try:
        pagerank = nx.pagerank(G, weight="weight", max_iter=100)
    except Exception:
        pagerank = {node: 0.0 for node in G.nodes()}

    try:
        sample_k = min(120, len(G.nodes()))
        betweenness = (
            nx.betweenness_centrality(G, k=sample_k, normalized=True, seed=RANDOM_SEED)
            if sample_k >= 2 else
            {node: 0.0 for node in G.nodes()}
        )
    except Exception:
        betweenness = {node: 0.0 for node in G.nodes()}

    try:
        clustering = nx.clustering(G.to_undirected()) if len(G.nodes()) <= 12000 else {node: 0.0 for node in G.nodes()}
    except Exception:
        clustering = {node: 0.0 for node in G.nodes()}

    rows = []
    for node in G.nodes():
        rows.append({
            "customer_id": int(node),
            "graph_in_degree": G.in_degree(node),
            "graph_out_degree": G.out_degree(node),
            "graph_degree_centrality": degree_centrality.get(node, 0.0),
            "graph_betweenness": betweenness.get(node, 0.0),
            "graph_pagerank": pagerank.get(node, 0.0),
            "graph_clustering": clustering.get(node, 0.0),
        })

    graph_df = pd.DataFrame(rows)
    graph_df["graph_risk_score"] = (
        minmax_scale(graph_df["graph_in_degree"]) +
        minmax_scale(graph_df["graph_out_degree"]) +
        minmax_scale(graph_df["graph_degree_centrality"]) +
        minmax_scale(graph_df["graph_betweenness"]) +
        minmax_scale(graph_df["graph_pagerank"]) +
        minmax_scale(graph_df["graph_clustering"])
    ) / 6.0

    graph_df["corporate_link_strength"] = 0.0

    if corporate_links is not None and len(corporate_links) > 0 and {"customer_id_1", "customer_id_2", "link_strength"}.issubset(corporate_links.columns):
        corp = corporate_links[["customer_id_1", "customer_id_2", "link_strength"]].copy()
        corp["customer_id_1"] = pd.to_numeric(corp["customer_id_1"], errors="coerce")
        corp["customer_id_2"] = pd.to_numeric(corp["customer_id_2"], errors="coerce")
        corp["link_strength"] = pd.to_numeric(corp["link_strength"], errors="coerce").fillna(0)
        corp = corp.dropna(subset=["customer_id_1", "customer_id_2"])

        link_strength_1 = corp.groupby("customer_id_1", as_index=False)["link_strength"].sum()
        link_strength_1.columns = ["customer_id", "corporate_link_strength_sum"]

        link_strength_2 = corp.groupby("customer_id_2", as_index=False)["link_strength"].sum()
        link_strength_2.columns = ["customer_id", "corporate_link_strength_sum_2"]

        merged_links = link_strength_1.merge(link_strength_2, on="customer_id", how="outer")
        merged_links["corporate_link_strength"] = (
            merged_links["corporate_link_strength_sum"].fillna(0) +
            merged_links["corporate_link_strength_sum_2"].fillna(0)
        )
        merged_links = merged_links[["customer_id", "corporate_link_strength"]]

        graph_df = graph_df.merge(merged_links, on="customer_id", how="left", suffixes=("", "_new"))
        if "corporate_link_strength_new" in graph_df.columns:
            graph_df["corporate_link_strength"] = graph_df["corporate_link_strength_new"].fillna(graph_df["corporate_link_strength"])
            graph_df = graph_df.drop(columns=["corporate_link_strength_new"])

        graph_df["corporate_link_strength"] = graph_df["corporate_link_strength"].fillna(0)
        graph_df["graph_risk_score"] = 0.85 * graph_df["graph_risk_score"] + 0.15 * minmax_scale(graph_df["corporate_link_strength"])

    return graph_df
