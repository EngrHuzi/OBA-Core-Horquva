const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

function buildFullOntology(data) {
  const entities = new Map()
  const relationships = []
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
    entities.set(`human_${person.toLowerCase().replace(/ /g, '_')}`, {
      id: `human_${person.toLowerCase().replace(/ /g, '_')}`,
      name: person,
      entityType: 'human',
      properties: { name: person },
      owner: null,
      criticality: 'medium',
      documented: false,
      department: null
    })
  }

  for (const agent of (data.agents || [])) {
    entities.set(agent.id, {
      id: agent.id,
      name: agent.name,
      entityType: 'agent',
      properties: agent,
      owner: agent.owner,
      criticality: agent.criticality || 'medium',
      documented: agent.documented || false,
      department: agent.department
    })
  }

  for (const tool of (data.ai_tools || [])) {
    entities.set(tool.id, {
      id: tool.id,
      name: tool.name,
      entityType: 'system',
      properties: tool,
      owner: tool.access_owner,
      criticality: tool.criticality || 'medium',
      documented: tool.documented || false,
      department: null
    })
  }

  for (const wf of (data.workflows || [])) {
    entities.set(wf.id, {
      id: wf.id,
      name: wf.name,
      entityType: 'workflow',
      properties: wf,
      owner: wf.owner,
      criticality: wf.criticality || 'medium',
      documented: wf.documented || false,
      department: wf.department
    })
  }

  for (const policy of (data.governance_policies || [])) {
    entities.set(policy.id, {
      id: policy.id,
      name: policy.name,
      entityType: 'knowledge',
      properties: policy,
      owner: policy.created_by,
      criticality: policy.compliance_required ? 'high' : 'medium',
      documented: true,
      department: null
    })
  }

  for (const agent of (data.agents || [])) {
    if (agent.owner) {
      relationships.push({
        sourceId: `human_${agent.owner.toLowerCase().replace(/ /g, '_')}`,
        targetId: agent.id,
        type: 'owns'
      })
    }
    if (agent.backup_owner) {
      relationships.push({
        sourceId: `human_${agent.backup_owner.toLowerCase().replace(/ /g, '_')}`,
        targetId: agent.id,
        type: 'owns'
      })
    }
  }

  for (const dep of (data.dependencies || [])) {
    relationships.push({ sourceId: dep.from, targetId: dep.to, type: dep.type || 'depends_on' })
  }

  for (const tool of (data.ai_tools || [])) {
    for (const agentId of (tool.agents_using || [])) {
      relationships.push({ sourceId: agentId, targetId: tool.id, type: 'uses' })
    }
  }

  for (const wf of (data.workflows || [])) {
    for (const step of (wf.steps || [])) {
      if (step.actor === 'tool') {
        const tool = [...entities.values()].find(e => e.entityType === 'system' && e.name === step.name)
        if (tool) relationships.push({ sourceId: wf.id, targetId: tool.id, type: 'uses' })
      } else if (step.actor === 'agent') {
        relationships.push({ sourceId: wf.id, targetId: step.name, type: 'triggers' })
      } else if (step.actor === 'human') {
        relationships.push({
          sourceId: `human_${step.name.toLowerCase().replace(/ /g, '_')}`,
          targetId: wf.id,
          type: 'participates_in'
        })
      }
    }
  }

  for (const policy of (data.governance_policies || [])) {
    for (const targetId of (policy.applies_to || [])) {
      if (entities.has(targetId)) {
        relationships.push({ sourceId: policy.id, targetId, type: 'governs' })
      }
    }
  }

  return { entities: Object.fromEntries(entities), relationships }
}

function buildGraph(ontology) {
  const adjacency = {}
  const reverseAdj = {}
  for (const id of Object.keys(ontology.entities)) {
    adjacency[id] = []
    reverseAdj[id] = []
  }
  for (const rel of ontology.relationships) {
    if (adjacency[rel.sourceId]) adjacency[rel.sourceId].push(rel.targetId)
    if (reverseAdj[rel.targetId]) reverseAdj[rel.targetId].push(rel.sourceId)
  }
  return { adjacency, reverseAdj }
}

function buildEntityContext(entity, ontology, graph) {
  const related = []
  const riskIndicators = []

  for (const targetId of (graph.adjacency[entity.id] || [])) {
    const target = ontology.entities[targetId]
    if (target) related.push({ name: target.name, type: target.entityType, direction: 'outgoing' })
  }
  for (const sourceId of (graph.reverseAdj[entity.id] || [])) {
    const source = ontology.entities[sourceId]
    if (source) related.push({ name: source.name, type: source.entityType, direction: 'incoming' })
  }

  if (!entity.owner && ['agent', 'workflow'].includes(entity.entityType)) {
    riskIndicators.push('No owner assigned')
  }
  if (!entity.documented && entity.entityType !== 'knowledge') {
    riskIndicators.push('Not documented')
  }
  if (entity.criticality === 'critical') {
    riskIndicators.push('Criticality: CRITICAL')
  }

  const incoming = (graph.reverseAdj[entity.id] || []).length
  if (entity.entityType === 'agent' && incoming >= 3) {
    riskIndicators.push(`High dependency load (${incoming} incoming)`)
  }

  let governanceStatus = 'GOVERNED'
  if (['agent', 'workflow', 'system'].includes(entity.entityType)) {
    const policies = ontology.relationships.filter(r => r.targetId === entity.id && r.type === 'governs')
    if (policies.length === 0) governanceStatus = 'NO GOVERNANCE'
  }

  let summary = `${entity.name} is a ${entity.entityType}`
  if (entity.owner) summary += ` owned by ${entity.owner}`
  summary += ` with criticality ${entity.criticality}.`
  if (riskIndicators.length > 0) summary += ` Risks: ${riskIndicators.join(', ')}.`

  return {
    entityId: entity.id,
    entityName: entity.name,
    entityType: entity.entityType,
    owner: entity.owner,
    department: entity.department,
    criticality: entity.criticality,
    documented: entity.documented,
    relatedEntities: related,
    riskIndicators,
    governanceStatus,
    summary
  }
}

function buildPersonContext(person, ontology, graph) {
  const ownedAgents = []
  const ownedWorkflows = []
  const backupFor = []
  const coverageGaps = []

  for (const rel of ontology.relationships) {
    if (rel.sourceId === person.id && rel.type === 'owns') {
      const target = ontology.entities[rel.targetId]
      if (target) {
        if (target.entityType === 'agent') ownedAgents.push(target.name)
        else if (target.entityType === 'workflow') ownedWorkflows.push(target.name)
      }
    }
  }

  for (const agentId of ownedAgents) {
    const agent = Object.values(ontology.entities).find(e => e.name === agentId && e.entityType === 'agent')
    if (agent && !agent.properties.backup_owner) {
      coverageGaps.push(`${agentId} has no backup owner`)
    }
  }

  const total = ownedAgents.length + ownedWorkflows.length
  let riskLevel = 'LOW'
  if (total === 0) riskLevel = 'NONE'
  else if (ownedAgents.length >= 4) riskLevel = 'CRITICAL'
  else if (ownedAgents.length >= 3) riskLevel = 'HIGH'
  else if (coverageGaps.length > 0) riskLevel = 'MEDIUM'

  return {
    personId: person.id,
    personName: person.name,
    ownedAgents,
    ownedWorkflows,
    backupFor,
    coverageGaps,
    totalResponsibilities: total,
    riskLevel,
    summary: `${person.name} owns ${ownedAgents.length} agents and ${ownedWorkflows.length} workflows. Risk: ${riskLevel}.`
  }
}

function buildOrganizationContext(data, ontology, entityContexts) {
  const typeCounts = {}
  for (const e of Object.values(ontology.entities)) {
    typeCounts[e.entityType] = (typeCounts[e.entityType] || 0) + 1
  }

  const criticalAssets = entityContexts.filter(e => e.criticality === 'critical').map(e => e.entityName)
  const orphaned = entityContexts.filter(e => e.entityType === 'agent' && !e.owner).map(e => e.entityName)
  const undocumented = entityContexts.filter(e => !e.documented && ['agent', 'workflow', 'system'].includes(e.entityType)).map(e => e.entityName)

  let healthScore = 100
  healthScore -= orphaned.length * 8
  healthScore -= undocumented.length * 3
  healthScore = Math.max(0, healthScore)

  const healthLabel = healthScore >= 80 ? 'HEALTHY' : healthScore >= 60 ? 'WARNING' : healthScore >= 40 ? 'AT RISK' : 'CRITICAL'

  return {
    company: data.company,
    totalEntities: Object.keys(ontology.entities).length,
    totalRelationships: ontology.relationships.length,
    entityTypeCounts: typeCounts,
    criticalAssets,
    orphanedAssets: orphaned,
    undocumentedAssets: undocumented,
    healthSummary: `${healthScore}/100 — ${healthLabel}`,
    executiveBrief: `${data.company} has ${Object.keys(ontology.entities).length} entities and ${ontology.relationships.length} relationships. ${orphaned.length} orphaned, ${undocumented.length} undocumented. Health: ${healthScore}/100 (${healthLabel}).`
  }
}

function buildVoiceModels(ontology) {
  return Object.values(ontology.entities).map(entity => ({
    entityId: entity.id,
    entityName: entity.name,
    entityType: entity.entityType,
    aliases: [entity.name.toLowerCase()],
    semanticDescription: `${entity.name} is a ${entity.entityType} with ${entity.criticality} criticality`,
    conversationalTriggers: [`who owns ${entity.name}`, `what does ${entity.name} do`]
  }))
}

router.get('/', (req, res) => {
  const data = loadData()
  const ontology = buildFullOntology(data)
  const graph = buildGraph(ontology)

  const entityContexts = Object.values(ontology.entities).map(e => buildEntityContext(e, ontology, graph))
  const persons = Object.values(ontology.entities).filter(e => e.entityType === 'human')
  const personContexts = persons.map(p => buildPersonContext(p, ontology, graph))
  const orgContext = buildOrganizationContext(data, ontology, entityContexts)
  const voiceModels = buildVoiceModels(ontology)

  res.json({
    organizationContext: orgContext,
    entityContexts,
    personContexts,
    voiceModels,
    voiceContext: {
      intentUnderstanding: [
        { intent: 'risk_assessment', description: 'User wants to understand organizational risks', triggerWords: ['risk', 'danger', 'threat'] },
        { intent: 'ownership_query', description: 'User wants to know who owns what', triggerWords: ['owner', 'responsible', 'who owns'] },
        { intent: 'dependency_analysis', description: 'User wants to understand dependencies', triggerWords: ['depend', 'break', 'cascade'] },
        { intent: 'health_check', description: 'User wants organizational health status', triggerWords: ['health', 'score', 'status'] },
        { intent: 'simulation', description: 'User wants to simulate disruption scenarios', triggerWords: ['what if', 'simulate', 'scenario'] },
        { intent: 'recommendation', description: 'User wants actionable recommendations', triggerWords: ['recommend', 'fix', 'improve'] }
      ],
      entityResolution: Object.fromEntries(
        Object.values(ontology.entities).map(e => [e.name.toLowerCase(), e.id])
      ),
      organizationalSummary: orgContext.executiveBrief
    }
  })
})

router.get('/entity/:id', (req, res) => {
  const data = loadData()
  const ontology = buildFullOntology(data)
  const graph = buildGraph(ontology)
  const entity = ontology.entities[req.params.id]

  if (!entity) return res.status(404).json({ error: 'Entity not found' })

  const context = buildEntityContext(entity, ontology, graph)
  res.json(context)
})

router.get('/person/:id', (req, res) => {
  const data = loadData()
  const ontology = buildFullOntology(data)
  const graph = buildGraph(ontology)
  const person = ontology.entities[req.params.id]

  if (!person || person.entityType !== 'human') return res.status(404).json({ error: 'Person not found' })

  const context = buildPersonContext(person, ontology, graph)
  res.json(context)
})

router.get('/voice', (req, res) => {
  const data = loadData()
  const ontology = buildFullOntology(data)
  const voiceModels = buildVoiceModels(ontology)

  res.json({
    entityResolution: Object.fromEntries(
      Object.values(ontology.entities).map(e => [e.name.toLowerCase(), e.id])
    ),
    voiceModels,
    intentUnderstanding: [
      { intent: 'risk_assessment', description: 'User wants to understand organizational risks', triggerWords: ['risk', 'danger', 'threat'] },
      { intent: 'ownership_query', description: 'User wants to know who owns what', triggerWords: ['owner', 'responsible', 'who owns'] },
      { intent: 'dependency_analysis', description: 'User wants to understand dependencies', triggerWords: ['depend', 'break', 'cascade'] },
      { intent: 'health_check', description: 'User wants organizational health status', triggerWords: ['health', 'score', 'status'] },
      { intent: 'simulation', description: 'User wants to simulate disruption scenarios', triggerWords: ['what if', 'simulate', 'scenario'] },
      { intent: 'recommendation', description: 'User wants actionable recommendations', triggerWords: ['recommend', 'fix', 'improve'] }
    ]
  })
})

module.exports = router
