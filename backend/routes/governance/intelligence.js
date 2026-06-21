const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

function assessGovernance(entity, policies) {
  let score = 100
  const issues = []

  if (!entity.owner) {
    score -= 40
    issues.push('No owner assigned')
  }
  if (!entity.documented) {
    score -= 20
    issues.push('Not documented')
  }

  const applicable = policies.filter(p => (p.applies_to || []).includes(entity.id))
  if (applicable.length === 0) {
    score -= 25
    issues.push('No governance policy applies')
  } else {
    const expired = applicable.filter(p => p.status === 'expired')
    if (expired.length > 0) {
      score -= 15
      issues.push(`${expired.length} governance policy expired`)
    }
    const active = applicable.filter(p => p.status === 'active' || p.status === 'enforced')
    if (active.length === 0) {
      score -= 10
      issues.push('No active governance policy')
    }
    const enforced = applicable.filter(p => p.status === 'enforced')
    if (enforced.length === 0 && (entity.criticality === 'critical' || entity.criticality === 'high')) {
      score -= 10
      issues.push('Critical entity lacks enforced governance')
    }
  }

  const critBonus = { critical: -10, high: -5, medium: 0, low: 5 }
  score += critBonus[entity.criticality] || 0

  if ((entity.criticality === 'critical' || entity.criticality === 'high') && applicable.length === 0) {
    score -= 15
    issues.push('High-criticality entity with zero governance coverage')
  }

  score = Math.max(0, Math.min(100, score))

  let level
  if (score >= 80) level = 'HEALTHY'
  else if (score >= 60) level = 'WARNING'
  else if (score >= 40) level = 'AT RISK'
  else level = 'CRITICAL'

  return { score, level, issues }
}

router.get('/', (req, res) => {
  const data = loadData()
  const policies = data.governance_policies || []

  const entities = []

  for (const agent of (data.agents || [])) {
    entities.push({
      id: agent.id,
      name: agent.name,
      type: 'agent',
      owner: agent.owner,
      department: agent.department || 'N/A',
      criticality: agent.criticality || 'medium',
      documented: agent.documented || false
    })
  }
  for (const tool of (data.ai_tools || [])) {
    entities.push({
      id: tool.id,
      name: tool.name,
      type: 'tool',
      owner: tool.access_owner,
      department: 'N/A',
      criticality: tool.criticality || 'medium',
      documented: tool.documented || false
    })
  }
  for (const wf of (data.workflows || [])) {
    entities.push({
      id: wf.id,
      name: wf.name,
      type: 'workflow',
      owner: wf.owner,
      department: wf.department || 'N/A',
      criticality: wf.criticality || 'medium',
      documented: wf.documented || false
    })
  }

  const results = entities.map(entity => {
    const { score, level, issues } = assessGovernance(entity, policies)
    const policyCount = policies.filter(p => (p.applies_to || []).includes(entity.id)).length

    return {
      entityId: entity.id,
      entityName: entity.name,
      entityType: entity.type,
      department: entity.department,
      owner: entity.owner,
      criticality: entity.criticality,
      documented: entity.documented,
      governanceScore: score,
      governanceLevel: level,
      policyCount,
      issues
    }
  })

  results.sort((a, b) => a.governanceScore - b.governanceScore)

  const overallScore = results.length > 0
    ? Math.round(results.reduce((sum, r) => sum + r.governanceScore, 0) / results.length)
    : 100

  let overallLevel
  if (overallScore >= 80) overallLevel = 'HEALTHY'
  else if (overallScore >= 60) overallLevel = 'WARNING'
  else if (overallScore >= 40) overallLevel = 'AT RISK'
  else overallLevel = 'CRITICAL'

  const deptHeatmap = {}
  for (const r of results) {
    const dept = r.department
    if (!deptHeatmap[dept]) deptHeatmap[dept] = { scores: [], critical: 0, total: 0 }
    deptHeatmap[dept].scores.push(r.governanceScore)
    deptHeatmap[dept].total++
    if (r.governanceLevel === 'CRITICAL') deptHeatmap[dept].critical++
  }

  const departmentSummary = Object.entries(deptHeatmap).map(([dept, info]) => ({
    department: dept,
    avgScore: Math.round(info.scores.reduce((a, b) => a + b, 0) / info.scores.length),
    entityCount: info.total,
    criticalGaps: info.critical,
    health: info.scores.reduce((a, b) => a + b, 0) / info.scores.length >= 80 ? 'HEALTHY'
      : info.scores.reduce((a, b) => a + b, 0) / info.scores.length >= 60 ? 'WARNING'
      : info.scores.reduce((a, b) => a + b, 0) / info.scores.length >= 40 ? 'AT RISK'
      : 'CRITICAL'
  }))

  const risks = results
    .filter(r => r.governanceLevel === 'CRITICAL' || r.governanceLevel === 'AT RISK')
    .map(r => ({
      entityName: r.entityName,
      riskType: r.issues[0] || 'Governance Weakness',
      severity: r.governanceLevel === 'CRITICAL' ? 'CRITICAL' : 'HIGH',
      description: r.issues.join('; '),
      remediation: `Address governance gaps for ${r.entityName}`
    }))

  res.json({
    governanceScore: overallScore,
    governanceLevel: overallLevel,
    totalEntities: results.length,
    criticalGaps: results.filter(r => r.governanceLevel === 'CRITICAL').length,
    results,
    departmentSummary,
    risks
  })
})

module.exports = router
