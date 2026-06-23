const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

function buildOntologyGraph(data) {
  const nodes = new Map()
  const edges = []
  const people = new Set()

  for (const agent of (data.agents || [])) {
    if (agent.owner) people.add(agent.owner)
    if (agent.backup_owner) people.add(agent.backup_owner)
  }
  for (const wf of (data.workflows || [])) {
    if (wf.owner) people.add(wf.owner)
    if (wf.backup_owner) people.add(wf.backup_owner)
    for (const step of (wf.steps || [])) {
      if (step.actor === 'human') people.add(step.name)
    }
  }
  for (const tool of (data.ai_tools || [])) {
    if (tool.access_owner) people.add(tool.access_owner)
    for (const user of (tool.users || [])) people.add(user)
  }
  for (const policy of (data.governance_policies || [])) {
    if (policy.created_by) people.add(policy.created_by)
  }

  for (const person of [...people].sort()) {
    nodes.set(`human_${person.toLowerCase().replace(/ /g, '_')}`, {
      id: `human_${person.toLowerCase().replace(/ /g, '_')}`,
      name: person,
      entityType: 'human',
      inDegree: 0,
      outDegree: 0,
      totalDegree: 0,
      neighborsIn: [],
      neighborsOut: []
    })
  }

  for (const agent of (data.agents || [])) {
    nodes.set(agent.id, {
      id: agent.id,
      name: agent.name,
      entityType: 'agent',
      inDegree: 0,
      outDegree: 0,
      totalDegree: 0,
      neighborsIn: [],
      neighborsOut: []
    })
  }

  for (const tool of (data.ai_tools || [])) {
    nodes.set(tool.id, {
      id: tool.id,
      name: tool.name,
      entityType: 'system',
      inDegree: 0,
      outDegree: 0,
      totalDegree: 0,
      neighborsIn: [],
      neighborsOut: []
    })
  }

  for (const wf of (data.workflows || [])) {
    nodes.set(wf.id, {
      id: wf.id,
      name: wf.name,
      entityType: 'workflow',
      inDegree: 0,
      outDegree: 0,
      totalDegree: 0,
      neighborsIn: [],
      neighborsOut: []
    })
  }

  for (const policy of (data.governance_policies || [])) {
    nodes.set(policy.id, {
      id: policy.id,
      name: policy.name,
      entityType: 'knowledge',
      inDegree: 0,
      outDegree: 0,
      totalDegree: 0,
      neighborsIn: [],
      neighborsOut: []
    })
  }

  function addEdge(sourceId, targetId, relType) {
    if (!nodes.has(sourceId) || !nodes.has(targetId)) return
    edges.push({ sourceId, targetId, relationshipType: relType })
    const source = nodes.get(sourceId)
    const target = nodes.get(targetId)
    source.outDegree++
    source.totalDegree++
    source.neighborsOut.push(targetId)
    target.inDegree++
    target.totalDegree++
    target.neighborsIn.push(sourceId)
  }

  for (const agent of (data.agents || [])) {
    if (agent.owner) {
      addEdge(`human_${agent.owner.toLowerCase().replace(/ /g, '_')}`, agent.id, 'owns')
    }
    if (agent.backup_owner) {
      addEdge(`human_${agent.backup_owner.toLowerCase().replace(/ /g, '_')}`, agent.id, 'owns')
    }
  }

  for (const dep of (data.dependencies || [])) {
    let relType = dep.type || 'depends_on'
    addEdge(dep.from, dep.to, relType)
  }

  for (const tool of (data.ai_tools || [])) {
    for (const agentId of (tool.agents_using || [])) {
      addEdge(agentId, tool.id, 'uses')
    }
  }

  for (const wf of (data.workflows || [])) {
    for (const step of (wf.steps || [])) {
      if (step.actor === 'tool') {
        const tool = [...nodes.values()].find(n => n.entityType === 'system' && n.name === step.name)
        if (tool) addEdge(wf.id, tool.id, 'uses')
      } else if (step.actor === 'agent') {
        addEdge(wf.id, step.name, 'triggers')
      } else if (step.actor === 'human') {
        addEdge(`human_${step.name.toLowerCase().replace(/ /g, '_')}`, wf.id, 'participates_in')
      }
    }
  }

  for (const policy of (data.governance_policies || [])) {
    for (const targetId of (policy.applies_to || [])) {
      if (nodes.has(targetId)) {
        addEdge(policy.id, targetId, 'governs')
      }
    }
  }

  return { nodes: Object.fromEntries(nodes), edges }
}

function analyzeGraph(graph) {
  const { nodes, edges } = graph
  const nodeList = Object.values(nodes)
  const nodeIds = nodeList.map(n => n.id)

  const adjacency = {}
  const reverseAdj = {}
  for (const node of nodeList) {
    adjacency[node.id] = []
    reverseAdj[node.id] = []
  }
  for (const edge of edges) {
    adjacency[edge.sourceId].push(edge.targetId)
    reverseAdj[edge.targetId].push(edge.sourceId)
  }

  function bfs(start, end) {
    if (!nodes[start] || !nodes[end]) return null
    const visited = new Set([start])
    const queue = [[start, [start]]]
    while (queue.length > 0) {
      const [current, path] = queue.shift()
      if (current === end) return path
      for (const neighbor of adjacency[current] || []) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor)
          queue.push([neighbor, [...path, neighbor]])
        }
      }
    }
    return null
  }

  function findAllPaths(start, end, maxDepth = 6) {
    if (!nodes[start] || !nodes[end]) return []
    const allPaths = []
    function dfs(current, path, visited) {
      if (path.length > maxDepth) return
      if (current === end && path.length > 1) {
        allPaths.push([...path])
        return
      }
      for (const neighbor of adjacency[current] || []) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor)
          path.push(neighbor)
          dfs(neighbor, path, visited)
          path.pop()
          visited.delete(neighbor)
        }
      }
    }
    dfs(start, new Set([start]), [start])
    return allPaths
  }

  let totalPaths = 0
  const betweenness = {}
  for (const id of nodeIds) betweenness[id] = 0

  for (const source of nodeIds) {
    for (const target of nodeIds) {
      if (source === target) continue
      const paths = findAllPaths(source, target, 6)
      totalPaths += paths.length
      for (const path of paths) {
        for (let i = 1; i < path.length - 1; i++) {
          betweenness[path[i]] += 1 / paths.length
        }
      }
    }
  }

  const maxB = Math.max(...Object.values(betweenness), 1)
  for (const id of nodeIds) betweenness[id] /= maxB

  const connected = new Set()
  let components = 0
  for (const id of nodeIds) {
    if (!connected.has(id)) {
      components++
      const queue = [id]
      while (queue.length > 0) {
        const curr = queue.shift()
        if (connected.has(curr)) continue
        connected.add(curr)
        for (const n of [...(adjacency[curr] || []), ...(reverseAdj[curr] || [])]) {
          if (!connected.has(n)) queue.push(n)
        }
      }
    }
  }

  const isolated = nodeList.filter(n => n.totalDegree === 0).map(n => n.name)
  const degrees = nodeList.map(n => n.totalDegree)
  const avgDegree = degrees.length > 0 ? (degrees.reduce((a, b) => a + b, 0) / degrees.length).toFixed(2) : 0
  const n = nodeList.length
  const maxEdges = n * (n - 1)
  const density = maxEdges > 0 ? (edges.length / maxEdges).toFixed(4) : 0

  let crossType = 0, intraType = 0
  for (const edge of edges) {
    const s = nodes[edge.sourceId]
    const t = nodes[edge.targetId]
    if (s && t) {
      if (s.entityType === t.entityType) intraType++
      else crossType++
    }
  }

  const bottlenecks = nodeList
    .filter(n => betweenness[n.id] > 0)
    .map(n => ({
      entityName: n.name,
      entityType: n.entityType,
      betweennessScore: parseFloat(betweenness[n.id].toFixed(4)),
      pathsThrough: Math.round(betweenness[n.id] * totalPaths)
    }))
    .sort((a, b) => b.betweennessScore - a.betweennessScore)
    .slice(0, 5)

  const topByDegree = [...nodeList].sort((a, b) => b.totalDegree - a.totalDegree).slice(0, 5)
  const topByIn = [...nodeList].sort((a, b) => b.inDegree - a.inDegree).slice(0, 5)
  const topByOut = [...nodeList].sort((a, b) => b.outDegree - a.outDegree).slice(0, 5)

  return {
    connectivity: {
      totalNodes: nodeList.length,
      totalEdges: edges.length,
      connectedComponents: components,
      isolatedNodes: isolated,
      avgDegree: parseFloat(avgDegree),
      density: parseFloat(density)
    },
    bottlenecks,
    topNodesByDegree: topByDegree,
    topNodesByInDegree: topByIn,
    topNodesByOutDegree: topByOut,
    crossTypeEdges: crossType,
    intraTypeEdges: intraType
  }
}

router.get('/', (req, res) => {
  const data = loadData()
  const graph = buildOntologyGraph(data)
  const analysis = analyzeGraph(graph)

  res.json({
    ...analysis,
    nodes: Object.values(graph.nodes),
    edges: graph.edges
  })
})

router.get('/nodes', (req, res) => {
  const data = loadData()
  const graph = buildOntologyGraph(data)
  const type = req.query.type

  let nodes = Object.values(graph.nodes)
  if (type) nodes = nodes.filter(n => n.entityType === type)

  res.json({ count: nodes.length, nodes })
})

router.get('/nodes/:id', (req, res) => {
  const data = loadData()
  const graph = buildOntologyGraph(data)
  const node = graph.nodes[req.params.id]

  if (!node) return res.status(404).json({ error: 'Node not found' })

  const outgoing = graph.edges.filter(e => e.sourceId === node.id)
  const incoming = graph.edges.filter(e => e.targetId === node.id)

  res.json({ node, outgoing, incoming })
})

router.get('/paths', (req, res) => {
  const data = loadData()
  const graph = buildOntologyGraph(data)
  const { source, target } = req.query

  if (!source || !target) return res.status(400).json({ error: 'source and target query params required' })

  const adjacency = {}
  for (const node of Object.values(graph.nodes)) adjacency[node.id] = []
  for (const edge of graph.edges) adjacency[edge.sourceId].push(edge.targetId)

  function findAllPaths(start, end, maxDepth = 6) {
    if (!graph.nodes[start] || !graph.nodes[end]) return []
    const allPaths = []
    function dfs(current, path, visited) {
      if (path.length > maxDepth) return
      if (current === end && path.length > 1) { allPaths.push([...path]); return }
      for (const neighbor of adjacency[current] || []) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor)
          path.push(neighbor)
          dfs(neighbor, path, visited)
          path.pop()
          visited.delete(neighbor)
        }
      }
    }
    dfs(start, new Set([start]), [start])
    return allPaths
  }

  const paths = findAllPaths(source, target).map(p => ({
    path: p,
    pathNames: p.map(id => graph.nodes[id] ? graph.nodes[id].name : id),
    length: p.length - 1
  }))

  res.json({ source, target, pathCount: paths.length, paths })
})

module.exports = router
