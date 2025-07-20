import React, { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const NetworkGraph = ({ graphData }) => {
  const graphRef = useRef();
  const [graphZoom, setGraphZoom] = useState(1);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });

  useEffect(() => {
    // Handle responsive sizing
    const handleResize = () => {
      const container = document.querySelector('.graph-container');
      if (container) {
        setDimensions({
          width: container.offsetWidth - 40,
          height: 500
        });
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    // Auto-zoom to fit with padding
    if (graphRef.current && graphData.nodes.length > 0) {
      setTimeout(() => {
        graphRef.current.zoomToFit(400, 50);
      }, 500);
    }

    return () => window.removeEventListener('resize', handleResize);
  }, [graphData]);

  // Zoom controls
  const handleZoomIn = () => {
    if (graphRef.current) {
      const newZoom = Math.min(graphZoom * 1.2, 2.5);
      graphRef.current.zoom(newZoom);
      setGraphZoom(newZoom);
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      const newZoom = Math.max(graphZoom * 0.8, 0.5);
      graphRef.current.zoom(newZoom);
      setGraphZoom(newZoom);
    }
  };

  const handleZoomReset = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400, 50);
      setGraphZoom(1);
    }
  };

  const handleCenterGraph = () => {
    if (graphRef.current) {
      graphRef.current.centerAt(0, 0, 1000);
    }
  };

  // Format graph data with enhanced properties
  const graphDataFormatted = {
    nodes: graphData.nodes.map(node => ({
      id: node.id,
      name: node.label,
      title: node.title,
      color: node.color,
      val: node.size / 5,
      fraudCount: node.fraudCount || 0,
      transactions: node.transactions || 0,
      value: node.value || 0
    })),
    links: graphData.edges.map(edge => ({
      source: edge.from,
      target: edge.to,
      color: edge.color,
      width: edge.width,
      label: edge.label,
      title: edge.title,
      curvature: 0.2
    }))
  };

  return (
    <div className="graph-container">
      <div className="graph-header">
        <h3 className="chart-title">
          🔍 Transaction Network Graph
          <span className="graph-subtitle">
            {graphData.statistics.total_nodes} accounts | {graphData.statistics.total_transactions} transactions
          </span>
        </h3>
        
        {/* Zoom Controls */}
        <div className="zoom-controls">
          <button onClick={handleZoomIn} className="zoom-btn" title="Zoom In">
            <span>🔍+</span>
          </button>
          <button onClick={handleZoomOut} className="zoom-btn" title="Zoom Out">
            <span>🔍-</span>
          </button>
          <button onClick={handleZoomReset} className="zoom-btn" title="Reset Zoom">
            <span>⟲</span>
          </button>
          <button onClick={handleCenterGraph} className="zoom-btn" title="Center Graph">
            <span>⊙</span>
          </button>
          <span className="zoom-level">Zoom: {(graphZoom * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="graph-wrapper">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphDataFormatted}
          width={dimensions.width}
          height={dimensions.height}
          nodeLabel={node => node.title}
          nodeColor={node => node.color}
          linkColor={link => link.color}
          linkWidth={link => link.width}
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}
          linkCurvature="curvature"
          backgroundColor="rgba(15, 23, 42, 0.5)"
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name;
            const fontSize = Math.max(12 / globalScale, 2);
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Draw node circle
            ctx.fillStyle = node.color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false);
            ctx.fill();
            
            // Draw border for fraud nodes
            if (node.fraudCount > 0) {
              ctx.strokeStyle = '#1f2937';
              ctx.lineWidth = 3 / globalScale;
              ctx.stroke();
            }
            
            // Draw label with background for better readability
            const labelY = node.y + node.val + fontSize + 2;
            
            // Label background
            ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
            const metrics = ctx.measureText(label);
            const padding = 4;
            ctx.fillRect(
              node.x - metrics.width / 2 - padding,
              labelY - fontSize / 2 - padding / 2,
              metrics.width + padding * 2,
              fontSize + padding
            );
            
            // Label text
            ctx.fillStyle = 'white';
            ctx.fillText(label, node.x, labelY);
            
            // Draw fraud indicator
            if (node.fraudCount > 0) {
              ctx.fillStyle = '#ef4444';
              ctx.font = `bold ${fontSize * 0.8}px Sans-Serif`;
              ctx.fillText(`!${node.fraudCount}`, node.x + node.val, node.y - node.val);
            }
          }}
          linkCanvasObjectMode={() => 'after'}
          linkCanvasObject={(link, ctx) => {
            const start = link.source;
            const end = link.target;
            
            // Draw link label (amount) with background
            if (link.label) {
              const textPos = {
                x: start.x + (end.x - start.x) * 0.5,
                y: start.y + (end.y - start.y) * 0.5
              };
              
              ctx.font = '10px Sans-Serif';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              
              // Label background
              const metrics = ctx.measureText(link.label);
              ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
              const padding = 2;
              ctx.fillRect(
                textPos.x - metrics.width / 2 - padding,
                textPos.y - 5 - padding,
                metrics.width + padding * 2,
                10 + padding * 2
              );
              
              // Label text
              ctx.fillStyle = 'white';
              ctx.fillText(link.label, textPos.x, textPos.y);
            }
          }}
          onNodeClick={(node, event) => {
            // Center on clicked node
            if (graphRef.current) {
              graphRef.current.centerAt(node.x, node.y, 1000);
            }
          }}
          enableZoomInteraction={true}
          enablePanInteraction={true}
          enableNodeDrag={true}
          cooldownTicks={50}
          onEngineStop={() => {
            if (graphRef.current && graphZoom === 1) {
              graphRef.current.zoomToFit(400, 50);
            }
          }}
        />
      </div>

      {/* Legend and Statistics */}
      <div className="graph-footer">
        <div className="graph-legend">
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#ef4444' }}></span>
            High Fraud Risk
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#f59e0b' }}></span>
            Medium Risk
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#22c55e' }}></span>
            Low Risk
          </span>
          <span className="legend-item">
            <span className="legend-line" style={{ backgroundColor: '#3b82f6' }}></span>
            Transaction Flow
          </span>
        </div>
        
        <div className="graph-stats">
          <span className="stat-item">
            <strong>{graphData.statistics.fraud_nodes}</strong> suspicious accounts
          </span>
          <span className="stat-item">
            <strong>{graphData.statistics.fraud_transactions}</strong> fraud transactions
          </span>
          <span className="stat-item">
            <strong>₹{(graphData.statistics.total_amount || 0).toLocaleString('en-IN')}</strong> total volume
          </span>
        </div>
      </div>

      {/* Instructions */}
      <div className="graph-instructions">
        <p>
          <strong>Controls:</strong> 
          🖱️ Drag to pan | 
          🔍 Scroll to zoom | 
          👆 Click node to center | 
          🤏 Drag nodes to rearrange
        </p>
      </div>
    </div>
  );
};

export default NetworkGraph;