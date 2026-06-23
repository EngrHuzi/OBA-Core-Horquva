const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

router.get('/', (req, res) => {
  const data = loadData()
  const agents = data.agents || []
  const workflows = data.workflows || []
  const tools = data.ai_tools || []
  const policies = data.governance_policies || []
  const deps = data.dependencies || []

  const criticalAssets = agents.filter(a => a.criticality === 'critical').map(a => a.name)
  const orphaned = agents.filter(a => !a.owner).map(a => a.name)
  const undocumented = [...agents, ...workflows].filter(a => !a.documented).map(a => a.name)

  const ownerCounts = {}
  for (const a of agents) {
    if (a.owner) ownerCounts[a.owner] = (ownerCounts[a.owner] || 0) + 1
  }
  const humanSpofs = Object.entries(ownerCounts).filter(([, c]) => c >= 3).map(([name, count]) => ({ name, agentCount: count }))

  const ungoverned = agents.filter(a => {
    const applicablePolicies = policies.filter(p => (p.applies_to || []).includes(a.id))
    return applicablePolicies.length === 0
  }).map(a => a.name)

  let healthScore = 100
  healthScore -= orphaned.length * 8
  healthScore -= undocumented.length * 3
  healthScore -= humanSpofs.length * 10
  healthScore = Math.max(0, healthScore)

  const healthLabel = healthScore >= 80 ? 'HEALTHY' : healthScore >= 60 ? 'WARNING' : healthScore >= 40 ? 'AT RISK' : 'CRITICAL'

  const actions = []
  if (orphaned.length > 0) actions.push({ priority: 'URGENT', action: `Assign owners to: ${orphaned.join(', ')}` })
  if (humanSpofs.length > 0) actions.push({ priority: 'HIGH', action: `Redistribute ${humanSpofs[0].name}'s workload (${humanSpofs[0].agentCount} agents)` })
  if (undocumented.length > 0) actions.push({ priority: 'MEDIUM', action: `Document ${undocumented.length} undocumented assets` })
  if (ungoverned.length > 0) actions.push({ priority: 'MEDIUM', action: `Establish governance for ${ungoverned.length} ungoverned entities` })

  res.json({
    organization: data.company,
    executiveSummary: `${data.company} has ${agents.length} agents, ${tools.length} tools, ${workflows.length} workflows. Health: ${healthScore}/100 (${healthLabel}).`,
    keyMetrics: {
      healthScore: `${healthScore}/100 — ${healthLabel}`,
      totalAgents: agents.length,
      totalTools: tools.length,
      totalWorkflows: workflows.length,
      totalPolicies: policies.length,
      criticalAssets: criticalAssets.length,
      orphanedAssets: orphaned.length,
      undocumentedAssets: undocumented.length,
      humanSpofs: humanSpofs.length,
      totalDependencies: deps.length,
    },
    topRisks: [
      ...orphaned.map(a => `${a}: No owner assigned (CRITICAL)`),
      ...humanSpofs.map(h => `${h.name}: Human SPOF — ${h.agentCount} agents (HIGH)`),
      ...undocumented.slice(0, 3).map(a => `${a}: Undocumented (MEDIUM)`),
    ],
    recommendedActions: actions,
    sections: [
      { title: 'Asset Risk Overview', priority: 'CRITICAL', content: `${criticalAssets.length} critical assets. ${orphaned.length} orphaned.`, items: criticalAssets.slice(0, 5) },
      { title: 'Documentation Gaps', priority: 'HIGH', content: `${undocumented.length} assets lack documentation.`, items: undocumented.slice(0, 5) },
      { title: 'Human SPOFs', priority: 'CRITICAL', content: `${humanSpofs.length} individuals are critical to operations.`, items: humanSpofs.map(h => `${h.name}: ${h.agentCount} agents`) },
      { title: 'Governance Coverage', priority: 'WARNING', content: `${policies.length} policies. ${ungoverned.length} entities without governance.`, items: ungoverned.slice(0, 3) },
    ],
  })
})

router.get('/entity/:id', (req, res) => {
  const data = loadData()
  const allAgents = data.agents || []
  const allTools = data.ai_tools || []
  const allWorkflows = data.workflows || []

  const entity = [...allAgents, ...allTools, ...allWorkflows].find(e => e.id === req.params.id)
  if (!entity) return res.status(404).json({ error: 'Entity not found' })

  const deps = (data.dependencies || []).filter(d => d.from === entity.id || d.to === entity.id)
  const policies = (data.governance_policies || []).filter(p => (p.applies_to || []).includes(entity.id))

  res.json({
    entity,
    dependencies: deps,
    governancePolicies: policies,
    riskLevel: !entity.owner ? 'CRITICAL' : entity.criticality === 'critical' ? 'HIGH' : 'MEDIUM',
  })
})

module.exports = router
