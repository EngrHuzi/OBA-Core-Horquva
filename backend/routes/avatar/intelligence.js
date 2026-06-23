const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

const INTENT_SIGNALS = {
  risk_assessment: ['risk', 'danger', 'threat', 'vulnerable', 'at risk', 'critical'],
  ownership_query: ['owner', 'responsible', 'who owns', 'accountable', 'assigned to'],
  dependency_analysis: ['depend', 'break', 'cascade', 'impact', 'if', 'fails', 'downstream'],
  health_check: ['health', 'score', 'status', 'overall', 'how are we doing'],
  simulation: ['what if', 'simulate', 'scenario', 'leaves', 'quits', 'goes down'],
  recommendation: ['recommend', 'fix', 'improve', 'action', 'should we', 'next steps'],
  governance: ['governance', 'policy', 'compliance', 'audit'],
  accountability: ['accountability', 'raci', 'approval', 'decision'],
}

function detectIntent(query) {
  const q = query.toLowerCase()
  let best = 'general_query'
  let bestScore = 0
  for (const [intent, signals] of Object.entries(INTENT_SIGNALS)) {
    const score = signals.filter(s => q.includes(s)).length
    if (score > bestScore) { bestScore = score; best = intent }
  }
  return { intent: best, confidence: Math.min(0.95, 0.4 + bestScore * 0.15) }
}

function extractEntities(query, ontology) {
  const q = query.toLowerCase()
  const found = []
  for (const e of Object.values(ontology)) {
    if (e.name.toLowerCase().split(' ').some(w => q.includes(w)) || q.includes(e.name.toLowerCase())) {
      found.push(e.name)
    }
  }
  return [...new Set(found)]
}

function buildOntology(data) {
  const entities = {}
  const people = new Set()

  for (const agent of (data.agents || [])) {
    if (agent.owner) people.add(agent.owner)
    if (agent.backup_owner) people.add(agent.backup_owner)
  }
  for (const wf of (data.workflows || [])) {
    if (wf.owner) people.add(wf.owner)
    if (wf.backup_owner) people.add(wf.backup_owner)
    for (const step of (wf.steps || [])) if (step.actor === 'human') people.add(step.name)
  }
  for (const tool of (data.ai_tools || [])) {
    if (tool.access_owner) people.add(tool.access_owner)
    for (const u of (tool.users || [])) people.add(u)
  }
  for (const p of (data.governance_policies || [])) if (p.created_by) people.add(p.created_by)

  for (const person of [...people].sort()) {
    entities[`human_${person.toLowerCase().replace(/ /g, '_')}`] = { id: `human_${person.toLowerCase().replace(/ /g, '_')}`, name: person, entityType: 'human' }
  }
  for (const a of (data.agents || [])) entities[a.id] = { id: a.id, name: a.name, entityType: 'agent', owner: a.owner, criticality: a.criticality, documented: a.documented, department: a.department }
  for (const t of (data.ai_tools || [])) entities[t.id] = { id: t.id, name: t.name, entityType: 'system', owner: t.access_owner, criticality: t.criticality }
  for (const w of (data.workflows || [])) entities[w.id] = { id: w.id, name: w.name, entityType: 'workflow', owner: w.owner, criticality: w.criticality, documented: w.documented }
  for (const p of (data.governance_policies || [])) entities[p.id] = { id: p.id, name: p.name, entityType: 'knowledge', owner: p.created_by }

  return entities
}

router.post('/query', (req, res) => {
  const data = loadData()
  const { query } = req.body
  if (!query) return res.status(400).json({ error: 'query required' })

  const ontology = buildOntology(data)
  const { intent, confidence } = detectIntent(query)
  const entities = extractEntities(query, ontology)

  let response = ''
  if (intent === 'health_check') {
    response = `Organization: ${data.company}. ${data.agents.length} agents, ${data.workflows.length} workflows.`
  } else if (intent === 'ownership_query' && entities.length > 0) {
    const e = Object.values(ontology).find(o => o.name === entities[0])
    response = e ? `${e.name} is owned by ${e.owner || 'no one'}.` : 'Entity not found.'
  } else if (intent === 'recommendation') {
    const orphaned = data.agents.filter(a => !a.owner).map(a => a.name)
    response = orphaned.length > 0 ? `Assign owners to: ${orphaned.join(', ')}` : 'No urgent actions needed.'
  } else {
    response = `${data.company}: ${Object.keys(ontology).length} entities in the organizational graph.`
  }

  res.json({ query, intent, confidence, entities, response })
})

router.post('/batch', (req, res) => {
  const data = loadData()
  const { queries } = req.body
  if (!queries || !Array.isArray(queries)) return res.status(400).json({ error: 'queries array required' })

  const ontology = buildOntology(data)
  const results = queries.map(query => {
    const { intent, confidence } = detectIntent(query)
    const entities = extractEntities(query, ontology)
    return { query, intent, confidence, entities }
  })

  res.json({ total: results.length, results })
})

module.exports = router
