import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
from typing import Dict, List, Any
import numpy as np

class GraphAnalyzer:
    def create_graph(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create enhanced network graph data with zoom/pan support"""
        G = nx.DiGraph()
        
        # Track node statistics
        node_transactions = {}
        node_amounts = {}
        
        # Add nodes and edges
        for idx, row in df.iterrows():
            payer = str(row.get('PAYER_VPA', f'Unknown_{idx}'))
            beneficiary = str(row.get('BENEFICIARY_VPA', f'Unknown_{idx}'))
            amount = float(row.get('AMOUNT', 0))
            is_fraud = bool(row.get('IS_FRAUD', 0))
            
            # Update node statistics
            for node in [payer, beneficiary]:
                if node not in node_transactions:
                    node_transactions[node] = 0
                    node_amounts[node] = 0
                node_transactions[node] += 1
                node_amounts[node] += amount
            
            # Add nodes with attributes
            G.add_node(payer, type='user', fraud_count=0)
            G.add_node(beneficiary, type='user', fraud_count=0)
            
            # Update fraud count
            if is_fraud:
                G.nodes[payer]['fraud_count'] = G.nodes[payer].get('fraud_count', 0) + 1
                G.nodes[beneficiary]['fraud_count'] = G.nodes[beneficiary].get('fraud_count', 0) + 1
            
            # Add edge (transaction)
            G.add_edge(
                payer, 
                beneficiary, 
                amount=amount,
                fraud=is_fraud,
                transaction_id=row.get('TRANSACTION_ID', f'TXN_{idx}'),
                timestamp=row.get('TXN_TIMESTAMP', '')
            )
        
        # Calculate node importance (PageRank)
        try:
            pagerank = nx.pagerank(G, alpha=0.85)
        except:
            pagerank = {node: 1.0 for node in G.nodes()}
        
        # Convert to format suitable for enhanced visualization
        nodes = []
        edges = []
        
        # Determine node sizes and colors based on activity
        max_transactions = max(node_transactions.values()) if node_transactions else 1
        max_amount = max(node_amounts.values()) if node_amounts else 1
        
        for node in G.nodes():
            node_data = G.nodes[node]
            fraud_count = node_data.get('fraud_count', 0)
            total_txns = node_transactions.get(node, 0)
            total_amount = node_amounts.get(node, 0)
            
            # Calculate node size based on transaction volume and PageRank
            base_size = 20
            size_factor = (total_txns / max_transactions) * 30
            pr_factor = pagerank.get(node, 0) * 100
            node_size = base_size + size_factor + pr_factor
            
            # Determine color based on fraud involvement
            if fraud_count > 5:
                color = "#dc2626"  # Dark red for high fraud
            elif fraud_count > 2:
                color = "#ef4444"  # Red for medium fraud
            elif fraud_count > 0:
                color = "#f59e0b"  # Orange for low fraud
            else:
                color = "#22c55e"  # Green for no fraud
            
            # Create node label
            label = node.split('@')[0] if '@' in node else node[:10]
            if len(label) > 15:
                label = label[:12] + "..."
            
            nodes.append({
                "id": node,
                "label": label,
                "title": f"{node}\nTransactions: {total_txns}\nTotal Amount: ₹{total_amount:,.0f}\nFraud Count: {fraud_count}",
                "color": color,
                "size": min(node_size, 100),  # Cap maximum size
                "fraud": fraud_count > 0,
                "fraudCount": fraud_count,
                "value": total_amount,
                "transactions": total_txns,
                "borderWidth": 3 if fraud_count > 0 else 1,
                "borderColor": "#1f2937" if fraud_count > 0 else "#e5e7eb"
            })
        
        # Process edges with enhanced styling
        edge_counts = {}
        for edge in G.edges():
            edge_key = f"{edge[0]}_{edge[1]}"
            if edge_key not in edge_counts:
                edge_counts[edge_key] = {"count": 0, "total_amount": 0, "fraud_count": 0}
            
            edge_data = G.edges[edge]
            edge_counts[edge_key]["count"] += 1
            edge_counts[edge_key]["total_amount"] += edge_data.get('amount', 0)
            if edge_data.get('fraud', False):
                edge_counts[edge_key]["fraud_count"] += 1
        
        # Create aggregated edges
        for edge_key, stats in edge_counts.items():
            source, target = edge_key.split('_', 1)
            
            # Determine edge styling based on fraud percentage
            fraud_percentage = (stats["fraud_count"] / stats["count"]) * 100 if stats["count"] > 0 else 0
            
            if fraud_percentage > 50:
                edge_color = "#dc2626"  # Dark red
                edge_width = 4
            elif fraud_percentage > 20:
                edge_color = "#ef4444"  # Red
                edge_width = 3
            elif fraud_percentage > 0:
                edge_color = "#f59e0b"  # Orange
                edge_width = 2
            else:
                edge_color = "#3b82f6"  # Blue
                edge_width = 1
            
            edges.append({
                "from": source,
                "to": target,
                "color": edge_color,
                "width": edge_width,
                "label": f"₹{stats['total_amount']:,.0f}",
                "title": f"Transactions: {stats['count']}\nTotal: ₹{stats['total_amount']:,.0f}\nFraud: {stats['fraud_count']}",
                "fraud": stats["fraud_count"] > 0,
                "arrows": {
                    "to": {
                        "enabled": True,
                        "scaleFactor": 0.5
                    }
                },
                "smooth": {
                    "type": "curvedCW",
                    "roundness": 0.2
                }
            })
        
        # Calculate graph statistics
        fraud_nodes = len([n for n in nodes if n['fraud']])
        fraud_edges = len([e for e in edges if e['fraud']])
        
        # Identify clusters
        try:
            communities = list(nx.community.greedy_modularity_communities(G.to_undirected()))
            cluster_info = {
                "total_clusters": len(communities),
                "largest_cluster_size": max(len(c) for c in communities) if communities else 0
            }
        except:
            cluster_info = {"total_clusters": 0, "largest_cluster_size": 0}
        
        # Graph layout options for better visualization
        layout_options = {
            "physics": {
                "enabled": True,
                "stabilization": {
                    "enabled": True,
                    "iterations": 100
                },
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "centralGravity": 0.3,
                    "springLength": 150,
                    "springConstant": 0.04,
                    "damping": 0.09
                }
            },
            "interaction": {
                "navigationButtons": True,
                "keyboard": True,
                "zoomView": True,
                "dragView": True,
                "hover": True,
                "tooltipDelay": 200,
                "zoomSpeed": 1,
                "minZoom": 0.5,
                "maxZoom": 2.5
            },
            "manipulation": {
                "enabled": False
            }
        }
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "fraud_nodes": fraud_nodes,
                "total_transactions": len(df),
                "fraud_transactions": sum(1 for _, row in df.iterrows() if row.get('IS_FRAUD', 0)),
                "total_amount": float(df['AMOUNT'].sum()),
                "average_transaction": float(df['AMOUNT'].mean()),
                "network_density": nx.density(G),
                "cluster_info": cluster_info
            },
            "layout_options": layout_options,
            "zoom_controls": {
                "enabled": True,
                "initial_zoom": 1.0,
                "zoom_step": 0.1,
                "min_zoom": 0.5,
                "max_zoom": 2.5
            }
        }
    
    def create_time_series_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create time series data for trend analysis"""
        if 'TXN_TIMESTAMP' not in df.columns:
            return {"error": "No timestamp data available"}
        
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['TXN_TIMESTAMP'])
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        
        # Daily transaction trends
        daily_stats = df.groupby('date').agg({
            'AMOUNT': ['sum', 'count'],
            'IS_FRAUD': 'sum'
        }).reset_index()
        
        daily_stats.columns = ['date', 'total_amount', 'transaction_count', 'fraud_count']
        
        # Hourly patterns
        hourly_stats = df.groupby('hour').agg({
            'AMOUNT': 'mean',
            'IS_FRAUD': 'mean'
        }).reset_index()
        
        hourly_stats.columns = ['hour', 'avg_amount', 'fraud_rate']
        
        return {
            "daily_trends": daily_stats.to_dict('records'),
            "hourly_patterns": hourly_stats.to_dict('records'),
            "peak_hours": hourly_stats.nlargest(3, 'fraud_rate')['hour'].tolist(),
            "total_days_analyzed": len(daily_stats)
        }