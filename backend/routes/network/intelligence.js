const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')
function loadData() { return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8')) }

router.get('/', (req, res) => {
  const data = loadData()
  const agents = data.agents || []
  const tools = data.ai_tools || []
  const deps = data.dependencies || []

  const nodes = [...agents.map(a => ({ id: a.id, name: a.name, type: 'agent' })),
                 ...tools.map(t => ({ id: t.id, name: t.name, type: 'system' }))]

  const degree = {}
  for (const n of nodes) degree[n.id] = 0
  for (const d of deps) {
    if (degree[d.from] !== undefined) degree[d.from]++
    if (degree[d.to] !== undefined) degree[d.to]++
  }

  const influencers = nodes
    .map(n => ({ ...n, degree: degree[n.id] || 0 }))
    .sort((a, b) => b.degree - a.degree)
    .slice(0, 5)

  const isolates = nodes.filter(n => (degree[n.id] || 0) === 0).map(n => n.name)

  res.json({
    totalNodes: nodes.length,
    avgDegree: (Object.values(degree).reduce((a, b) => a + b, 0) / nodes.length).toFixed(2),
    influencers,
    isolates,
    clusters: 1,
  })
})

module.exports = router
