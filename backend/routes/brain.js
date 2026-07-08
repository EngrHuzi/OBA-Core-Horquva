const express = require('express');
const router = express.Router();
const path = require('path');
const { spawn } = require('child_process');

router.get('/intelligence', (req, res) => {
    try {
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const fs = require('fs');
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            res.json({
                status: 'active',
                graph: graphData.summary,
                node_count: Object.keys(graphData.nodes || {}).length,
                edge_count: Object.keys(graphData.edges || {}).length,
                insights: (graphData.insights || []).length,
            });
        } else {
            res.json({
                status: 'not_initialized',
                message: 'Knowledge graph not yet generated. Run: python main.py --brain',
            });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/registry', (req, res) => {
    try {
        const registryPath = path.join(__dirname, '../../data/module_registry.json');
        const fs = require('fs');
        
        if (fs.existsSync(registryPath)) {
            const registryData = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
            res.json(registryData);
        } else {
            res.json({
                status: 'not_initialized',
                message: 'Module registry not yet generated. Run: python main.py --brain',
            });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/graph/nodes', (req, res) => {
    try {
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const fs = require('fs');
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            const nodes = graphData.nodes || {};
            const nodeType = req.query.type;
            
            let filteredNodes = Object.values(nodes);
            if (nodeType) {
                filteredNodes = filteredNodes.filter(n => n.node_type === nodeType);
            }
            
            res.json({
                total: filteredNodes.length,
                nodes: filteredNodes,
            });
        } else {
            res.json({ total: 0, nodes: [] });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/graph/edges', (req, res) => {
    try {
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const fs = require('fs');
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            const edges = graphData.edges || {};
            const edgeType = req.query.type;
            
            let filteredEdges = Object.values(edges);
            if (edgeType) {
                filteredEdges = filteredEdges.filter(e => e.edge_type === edgeType);
            }
            
            res.json({
                total: filteredEdges.length,
                edges: filteredEdges,
            });
        } else {
            res.json({ total: 0, edges: [] });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/graph/insights', (req, res) => {
    try {
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const fs = require('fs');
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            const insights = graphData.insights || [];
            const severity = req.query.severity;
            
            let filteredInsights = insights;
            if (severity) {
                filteredInsights = insights.filter(i => i.severity === severity);
            }
            
            res.json({
                total: filteredInsights.length,
                insights: filteredInsights,
            });
        } else {
            res.json({ total: 0, insights: [] });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/graph/centrality', (req, res) => {
    try {
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const fs = require('fs');
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            res.json({
                top_central_nodes: graphData.summary?.top_central_nodes || [],
            });
        } else {
            res.json({ top_central_nodes: [] });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/graph/path', (req, res) => {
    try {
        const { source, target } = req.query;
        
        if (!source || !target) {
            return res.status(400).json({ error: 'source and target query parameters required' });
        }
        
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const fs = require('fs');
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            const nodes = graphData.nodes || {};
            const edges = graphData.edges || {};
            
            const adjacency = {};
            for (const edge of Object.values(edges)) {
                if (!adjacency[edge.source_id]) adjacency[edge.source_id] = [];
                adjacency[edge.source_id].push(edge.target_id);
            }
            
            const visited = new Set();
            const queue = [[source, [source]]];
            visited.add(source);
            
            while (queue.length > 0) {
                const [current, path] = queue.shift();
                
                if (current === target) {
                    return res.json({
                        found: true,
                        path: path,
                        length: path.length - 1,
                    });
                }
                
                for (const neighbor of (adjacency[current] || [])) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push([neighbor, [...path, neighbor]]);
                    }
                }
            }
            
            res.json({ found: false, path: [], length: -1 });
        } else {
            res.json({ found: false, path: [], length: -1 });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.get('/summary', (req, res) => {
    try {
        const brainPath = path.join(__dirname, '../../data/knowledge_graph.json');
        const registryPath = path.join(__dirname, '../../data/module_registry.json');
        const fs = require('fs');
        
        const summary = {
            brain: { status: 'not_initialized' },
            registry: { status: 'not_initialized' },
        };
        
        if (fs.existsSync(brainPath)) {
            const graphData = JSON.parse(fs.readFileSync(brainPath, 'utf8'));
            summary.brain = {
                status: 'active',
                ...graphData.summary,
            };
        }
        
        if (fs.existsSync(registryPath)) {
            const registryData = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
            summary.registry = registryData;
        }
        
        res.json(summary);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.post('/run', (req, res) => {
    try {
        const pythonProcess = spawn('python', ['main.py', '--brain'], {
            cwd: path.join(__dirname, '../..'),
        });
        
        let output = '';
        let error = '';
        
        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        pythonProcess.stderr.on('data', (data) => {
            error += data.toString();
        });
        
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                res.json({
                    status: 'success',
                    message: 'Organizational Brain pipeline completed',
                    output: output,
                });
            } else {
                res.status(500).json({
                    status: 'error',
                    message: 'Pipeline execution failed',
                    error: error,
                    output: output,
                });
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
