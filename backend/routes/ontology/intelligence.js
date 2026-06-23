const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

const ENTITY_TYPES = {
  human: {
    name: 'human',
    description: 'A person in the organization — employee, contractor, or stakeholder',
    requiredProperties: ['name'],
    optionalProperties: ['department', 'role', 'email'],
    validRelationships: ['owns', 'collaborates_with', 'reports_to', 'consulted_by'],
    constraints: [
      'A human can own zero or more agents',
      'A human can own zero or more workflows',
      'A human can be a backup owner for agents and workflows'
    ]
  },
  team: {
    name: 'team',
    description: 'A functional group of people organized around a business domain',
    requiredProperties: ['name'],
    optionalProperties: ['department', 'lead', 'size'],
    validRelationships: ['contains', 'collaborates_with', 'governs'],
    constraints: [
      'A team contains one or more humans',
      'A team can own agents and workflows'
    ]
  },
  agent: {
    name: 'agent',
    description: 'An AI agent operating within the organization — performs automated tasks',
    requiredProperties: ['name', 'criticality'],
    optionalProperties: ['owner', 'backup_owner', 'department', 'documented'],
    validRelationships: ['depends_on', 'owned_by', 'uses', 'monitored_by', 'governed_by'],
    constraints: [
      'An agent should have at least one owner',
      'An agent should have a backup owner for resilience',
      'An agent can depend on other agents, tools, or workflows'
    ]
  },
  system: {
    name: 'system',
    description: 'An AI tool, platform, or external system used by the organization',
    requiredProperties: ['name', 'criticality'],
    optionalProperties: ['vendor', 'category', 'users', 'departments', 'monthly_cost_usd', 'backup_tool', 'access_owner', 'documented'],
    validRelationships: ['used_by', 'depends_on', 'backed_up_by', 'governed_by'],
    constraints: [
      'A system should have an access owner',
      'Critical systems should have a backup tool defined'
    ]
  },
  workflow: {
    name: 'workflow',
    description: 'A business process — a sequence of steps involving humans, agents, and tools',
    requiredProperties: ['name', 'criticality'],
    optionalProperties: ['owner', 'backup_owner', 'department', 'documented', 'steps'],
    validRelationships: ['owned_by', 'uses', 'triggers', 'governed_by'],
    constraints: [
      'A workflow should have at least one owner',
      'A workflow should be documented for recoverability'
    ]
  },
  knowledge: {
    name: 'knowledge',
    description: 'Organizational knowledge — policies, documentation, runbooks, institutional memory',
    requiredProperties: ['name', 'domain'],
    optionalProperties: ['status', 'applies_to', 'created_by', 'compliance_required'],
    validRelationships: ['governs', 'documented_by', 'owned_by'],
    constraints: [
      'Knowledge should have a defined domain',
      'Compliance knowledge should be reviewed on a regular cycle'
    ]
  }
}

const RELATIONSHIP_TYPES = {
  owns: {
    name: 'owns',
    description: 'A person has primary ownership and accountability for an entity',
    sourceTypes: ['human'],
    targetTypes: ['agent', 'workflow', 'system', 'knowledge'],
    cardinality: 'one-to-many',
    inverse: 'owned_by'
  },
  owned_by: {
    name: 'owned_by',
    description: 'An entity is owned and accountable to a person',
    sourceTypes: ['agent', 'workflow', 'system', 'knowledge'],
    targetTypes: ['human'],
    cardinality: 'many-to-one',
    inverse: 'owns'
  },
  depends_on: {
    name: 'depends_on',
    description: 'An entity requires another entity to function — failure of the target impacts the source',
    sourceTypes: ['agent', 'system', 'workflow'],
    targetTypes: ['agent', 'system', 'workflow'],
    cardinality: 'many-to-many',
    inverse: 'depended_on_by'
  },
  uses: {
    name: 'uses',
    description: 'A workflow or agent utilizes a system or tool to perform its function',
    sourceTypes: ['workflow', 'agent'],
    targetTypes: ['system'],
    cardinality: 'many-to-many',
    inverse: 'used_by'
  },
  monitors: {
    name: 'monitors',
    description: 'An entity observes or checks the health/status of another entity',
    sourceTypes: ['agent', 'human'],
    targetTypes: ['agent', 'system', 'workflow'],
    cardinality: 'one-to-many',
    inverse: 'monitored_by'
  },
  feeds: {
    name: 'feeds',
    description: 'An entity provides output or data that another entity consumes',
    sourceTypes: ['agent', 'system', 'workflow'],
    targetTypes: ['agent', 'system', 'workflow'],
    cardinality: 'many-to-many',
    inverse: 'fed_by'
  },
  triggers: {
    name: 'triggers',
    description: 'An entity initiates or activates another entity\'s execution',
    sourceTypes: ['agent', 'workflow', 'human'],
    targetTypes: ['agent', 'workflow'],
    cardinality: 'one-to-many',
    inverse: 'triggered_by'
  },
  backs_up: {
    name: 'backs_up',
    description: 'An entity serves as a failover or redundancy for another entity',
    sourceTypes: ['agent', 'human', 'system'],
    targetTypes: ['agent', 'system', 'workflow'],
    cardinality: 'many-to-one',
    inverse: 'backed_up_by'
  },
  governs: {
    name: 'governs',
    description: 'A knowledge entity (policy, rule, framework) applies governance to an entity',
    sourceTypes: ['knowledge'],
    targetTypes: ['agent', 'system', 'workflow', 'human'],
    cardinality: 'many-to-many',
    inverse: 'governed_by'
  },
  collaborates_with: {
    name: 'collaborates_with',
    description: 'Two entities work together on shared objectives',
    sourceTypes: ['human', 'agent', 'team'],
    targetTypes: ['human', 'agent', 'team'],
    cardinality: 'many-to-many',
    inverse: 'collaborates_with'
  },
  sequential: {
    name: 'sequential',
    description: 'Two agents execute in sequence — the first must complete before the second starts',
    sourceTypes: ['agent'],
    targetTypes: ['agent'],
    cardinality: 'many-to-many',
    inverse: 'preceded_by'
  },
  participates_in: {
    name: 'participates_in',
    description: 'A human or agent takes part in a workflow step',
    sourceTypes: ['human', 'agent', 'system'],
    targetTypes: ['workflow'],
    cardinality: 'many-to-many',
    inverse: 'has_participant'
  }
}

function buildOntology(data) {
  const entities = []
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
    const departments = new Set()
    for (const agent of (data.agents || [])) {
      if ((agent.owner === person || agent.backup_owner === person) && agent.department) {
        departments.add(agent.department)
      }
    }
    for (const wf of (data.workflows || [])) {
      if (wf.owner === person && wf.department) departments.add(wf.department)
    }

    entities.push({
      id: `human_${person.toLowerCase().replace(/ /g, '_')}`,
      name: person,
      entityType: 'human',
      properties: {
        name: person,
        department: departments.size > 0 ? [...departments].sort().join(', ') : null
      },
      validationErrors: []
    })
  }

  for (const agent of (data.agents || [])) {
    entities.push({
      id: agent.id,
      name: agent.name,
      entityType: 'agent',
      properties: {
        name: agent.name,
        owner: agent.owner || null,
        backup_owner: agent.backup_owner || null,
        department: agent.department || null,
        criticality: agent.criticality || 'medium',
        documented: agent.documented || false
      },
      validationErrors: []
    })
  }

  for (const tool of (data.ai_tools || [])) {
    entities.push({
      id: tool.id,
      name: tool.name,
      entityType: 'system',
      properties: {
        name: tool.name,
        vendor: tool.vendor,
        category: tool.category,
        users: tool.users || [],
        departments: tool.departments || [],
        monthly_cost_usd: tool.monthly_cost_usd || 0,
        criticality: tool.criticality || 'medium',
        documented: tool.documented || false,
        backup_tool: tool.backup_tool || null,
        access_owner: tool.access_owner || null
      },
      validationErrors: []
    })
  }

  for (const wf of (data.workflows || [])) {
    entities.push({
      id: wf.id,
      name: wf.name,
      entityType: 'workflow',
      properties: {
        name: wf.name,
        owner: wf.owner || null,
        backup_owner: wf.backup_owner || null,
        department: wf.department || null,
        criticality: wf.criticality || 'medium',
        documented: wf.documented || false,
        steps: wf.steps || []
      },
      validationErrors: []
    })
  }

  for (const policy of (data.governance_policies || [])) {
    entities.push({
      id: policy.id,
      name: policy.name,
      entityType: 'knowledge',
      properties: {
        name: policy.name,
        domain: policy.domain,
        status: policy.status,
        applies_to: policy.applies_to || [],
        created_by: policy.created_by,
        compliance_required: policy.compliance_required || false
      },
      validationErrors: []
    })
  }

  for (const agent of (data.agents || [])) {
    if (agent.owner) {
      relationships.push({
        sourceId: `human_${agent.owner.toLowerCase().replace(/ /g, '_')}`,
        sourceName: agent.owner,
        targetId: agent.id,
        targetName: agent.name,
        relationshipType: 'owns',
        metadata: { role: 'primary_owner' }
      })
    }
    if (agent.backup_owner) {
      relationships.push({
        sourceId: `human_${agent.backup_owner.toLowerCase().replace(/ /g, '_')}`,
        sourceName: agent.backup_owner,
        targetId: agent.id,
        targetName: agent.name,
        relationshipType: 'owns',
        metadata: { role: 'backup_owner' }
      })
    }
  }

  for (const dep of (data.dependencies || [])) {
    let relType = dep.type || 'depends_on'
    if (!RELATIONSHIP_TYPES[relType]) relType = 'depends_on'

    const source = entities.find(e => e.id === dep.from)
    const target = entities.find(e => e.id === dep.to)

    relationships.push({
      sourceId: dep.from,
      sourceName: source ? source.name : dep.from,
      targetId: dep.to,
      targetName: target ? target.name : dep.to,
      relationshipType: relType,
      metadata: { originalType: dep.type }
    })
  }

  for (const tool of (data.ai_tools || [])) {
    for (const agentId of (tool.agents_using || [])) {
      const agent = entities.find(e => e.id === agentId)
      if (agent) {
        relationships.push({
          sourceId: agentId,
          sourceName: agent.name,
          targetId: tool.id,
          targetName: tool.name,
          relationshipType: 'uses',
          metadata: {}
        })
      }
    }
  }

  for (const wf of (data.workflows || [])) {
    for (const step of (wf.steps || [])) {
      if (step.actor === 'tool') {
        const tool = entities.find(e => e.entityType === 'system' && e.name === step.name)
        if (tool) {
          relationships.push({
            sourceId: wf.id,
            sourceName: wf.name,
            targetId: tool.id,
            targetName: step.name,
            relationshipType: 'uses',
            metadata: { step: step.step, action: step.action }
          })
        }
      } else if (step.actor === 'agent') {
        relationships.push({
          sourceId: wf.id,
          sourceName: wf.name,
          targetId: step.name,
          targetName: step.name,
          relationshipType: 'triggers',
          metadata: { step: step.step, action: step.action }
        })
      } else if (step.actor === 'human') {
        relationships.push({
          sourceId: `human_${step.name.toLowerCase().replace(/ /g, '_')}`,
          sourceName: step.name,
          targetId: wf.id,
          targetName: wf.name,
          relationshipType: 'participates_in',
          metadata: { step: step.step, action: step.action }
        })
      }
    }
  }

  for (const policy of (data.governance_policies || [])) {
    for (const targetId of (policy.applies_to || [])) {
      const target = entities.find(e => e.id === targetId)
      if (target) {
        relationships.push({
          sourceId: policy.id,
          sourceName: policy.name,
          targetId: targetId,
          targetName: target.name,
          relationshipType: 'governs',
          metadata: {}
        })
      }
    }
  }

  const entitiesByType = {}
  for (const e of entities) {
    entitiesByType[e.entityType] = (entitiesByType[e.entityType] || 0) + 1
  }

  const relationshipsByType = {}
  for (const r of relationships) {
    relationshipsByType[r.relationshipType] = (relationshipsByType[r.relationshipType] || 0) + 1
  }

  return {
    entities,
    relationships,
    entityTypes: ENTITY_TYPES,
    relationshipTypes: RELATIONSHIP_TYPES,
    entitiesByType,
    relationshipsByType
  }
}

router.get('/', (req, res) => {
  const data = loadData()
  const ontology = buildOntology(data)

  const entityTypeSummary = Object.entries(ontology.entityTypes).map(([name, def]) => ({
    name,
    description: def.description,
    requiredProperties: def.requiredProperties,
    optionalProperties: def.optionalProperties,
    validRelationships: def.validRelationships,
    constraints: def.constraints,
    count: ontology.entitiesByType[name] || 0
  }))

  const relationshipTypeSummary = Object.entries(ontology.relationshipTypes).map(([name, def]) => ({
    name,
    description: def.description,
    sourceTypes: def.sourceTypes,
    targetTypes: def.targetTypes,
    cardinality: def.cardinality,
    inverse: def.inverse,
    count: ontology.relationshipsByType[name] || 0
  }))

  res.json({
    totalEntityTypes: Object.keys(ontology.entityTypes).length,
    totalRelationshipTypes: Object.keys(ontology.relationshipTypes).length,
    totalEntities: ontology.entities.length,
    totalRelationships: ontology.relationships.length,
    entitiesByType: ontology.entitiesByType,
    relationshipsByType: ontology.relationshipsByType,
    entityTypeSummary,
    relationshipTypeSummary,
    entities: ontology.entities,
    relationships: ontology.relationships
  })
})

router.get('/entities', (req, res) => {
  const data = loadData()
  const ontology = buildOntology(data)
  const type = req.query.type

  if (type) {
    const filtered = ontology.entities.filter(e => e.entityType === type)
    return res.json({ entityType: type, count: filtered.length, entities: filtered })
  }

  res.json({ totalEntities: ontology.entities.length, entities: ontology.entities })
})

router.get('/entities/:id', (req, res) => {
  const data = loadData()
  const ontology = buildOntology(data)
  const entity = ontology.entities.find(e => e.id === req.params.id)

  if (!entity) return res.status(404).json({ error: 'Entity not found' })

  const relationships = ontology.relationships.filter(
    r => r.sourceId === entity.id || r.targetId === entity.id
  )

  res.json({ entity, relationships })
})

router.get('/relationships', (req, res) => {
  const data = loadData()
  const ontology = buildOntology(data)
  const type = req.query.type

  if (type) {
    const filtered = ontology.relationships.filter(r => r.relationshipType === type)
    return res.json({ relationshipType: type, count: filtered.length, relationships: filtered })
  }

  res.json({ totalRelationships: ontology.relationships.length, relationships: ontology.relationships })
})

router.get('/types', (req, res) => {
  const entityTypeSummary = Object.entries(ENTITY_TYPES).map(([name, def]) => ({
    name,
    description: def.description,
    requiredProperties: def.requiredProperties,
    optionalProperties: def.optionalProperties,
    validRelationships: def.validRelationships,
    constraints: def.constraints
  }))

  const relationshipTypeSummary = Object.entries(RELATIONSHIP_TYPES).map(([name, def]) => ({
    name,
    description: def.description,
    sourceTypes: def.sourceTypes,
    targetTypes: def.targetTypes,
    cardinality: def.cardinality,
    inverse: def.inverse
  }))

  res.json({
    entityTypes: entityTypeSummary,
    relationshipTypes: relationshipTypeSummary
  })
})

module.exports = router
