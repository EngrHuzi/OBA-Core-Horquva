const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')
function loadData() { return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8')) }

router.get('/', (req, res) => {
  const data = loadData()
  const agents = data.agents || []
  const deps = data.dependencies || []

  const downstream = {}
  const upstream = {}
  for (const a of agents) { downstream[a.id] = 0; upstream[a.id] = 0 }
  for (const d of deps) {
    if (downstream[d.from] !== undefined) downstream[d.from]++
    if (upstream[d.to] !== undefined) upstream[d.to]++
  }

  const spof = agents.filter(a => downstream[a.id] >= 3).map(a => ({
    id: a.id, name: a.name, type: 'agent', downstream: downstream[a.id], upstream: upstream[a.id],
    spofScore: Math.min(1, downstream[a.id] / 10)
  }))

  res.json({
    totalNodes: agents.length,
    totalEdges: deps.length,
    spofCount: spof.length,
    spof,
    maxCascadeDepth: 5,
  })
})

module.exports = router
