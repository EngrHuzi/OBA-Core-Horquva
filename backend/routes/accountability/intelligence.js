const express = require('express')
const router = express.Router()
const path = require('path')
const fs = require('fs')

const DATA_PATH = path.join(__dirname, '../../data/sunrise_care.json')

function loadData() {
  return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'))
}

function assessAccountability(link, entityType) {
  let score = 100
  const issues = []

  if (!link.responsible) {
    score -= 30
    issues.push('No responsible person assigned')
  }
  if (!link.accountable) {
    score -= 25
    issues.push('No accountable person designated')
  }
  if (link.responsible && link.accountable && link.responsible === link.accountable) {
    score -= 10
    issues.push('Responsible and accountable are the same person')
  }
  if (link.consulted.length === 0 && (entityType === 'agent' || entityType === 'workflow')) {
    score -= 10
    issues.push('No consultation defined')
  }
  if (link.informed.length === 0) {
    score -= 5
    issues.push('No informed parties')
  }
  if (!link.decisionAuthority) {
    score -= 15
    issues.push('No clear decision authority')
  }
  if (link.approvalChain.length <= 1) {
    score -= 10
    issues.push('Single-person approval chain')
  }

  score = Math.max(0, Math.min(100, score))
  const hasRaci = !!(link.responsible && link.accountable)

  return { score, hasRaci, issues }
}

router.get('/', (req, res) => {
  const data = loadData()

  const agents = data.agents || []
  const links = []

  for (const agent of agents) {
    if (agent.owner) {
      links.push({
        entityId: agent.id,
        entityName: agent.name,
        entityType: 'agent',
        responsible: agent.owner,
        accountable: agent.backup_owner || agent.owner,
        consulted: [],
        informed: agent.backup_owner ? [agent.backup_owner] : [],
        decisionAuthority: agent.owner,
        approvalChain: [agent.owner, ...(agent.backup_owner ? [agent.backup_owner] : [])]
      })
    }
  }

  const results = links.map(link => {
    const { score, hasRaci, issues } = assessAccountability(link, link.entityType)
    return {
      entityId: link.entityId,
      entityName: link.entityName,
      entityType: link.entityType,
      responsible: link.responsible,
      accountable: link.accountable,
      consulted: link.consulted,
      informed: link.informed,
      decisionAuthority: link.decisionAuthority,
      approvalChain: link.approvalChain,
      hasRaci,
      accountabilityScore: score,
      issues
    }
  })

  results.sort((a, b) => a.accountabilityScore - b.accountabilityScore)

  const overallScore = results.length > 0
    ? Math.round(results.reduce((sum, r) => sum + r.accountabilityScore, 0) / results.length)
    : 100

  let overallLevel
  if (overallScore >= 80) overallLevel = 'HEALTHY'
  else if (overallScore >= 60) overallLevel = 'WARNING'
  else if (overallScore >= 40) overallLevel = 'AT RISK'
  else overallLevel = 'CRITICAL'

  const personMap = {}
  for (const r of results) {
    for (const person of [r.responsible, r.accountable]) {
      if (person) {
        if (!personMap[person]) personMap[person] = { responsible: 0, accountable: 0 }
        if (person === r.responsible) personMap[person].responsible++
        if (person === r.accountable) personMap[person].accountable++
      }
    }
  }

  const chains = Object.entries(personMap).map(([person, data]) => {
    const owned = results.filter(r => r.responsible === person).map(r => r.entityName)
    const accountableFor = results.filter(r => r.accountable === person).map(r => r.entityName)
    const consultedIn = results.filter(r => r.consulted.includes(person)).map(r => r.entityName)
    const informedOf = results.filter(r => r.informed.includes(person)).map(r => r.entityName)

    return {
      person,
      ownedEntities: [...new Set(owned)],
      accountableFor: [...new Set(accountableFor)],
      consultedIn: [...new Set(consultedIn)],
      informedOf: [...new Set(informedOf)],
      totalResponsibilities: owned.length + accountableFor.length + consultedIn.length + informedOf.length
    }
  })

  chains.sort((a, b) => b.totalResponsibilities - a.totalResponsibilities)

  res.json({
    accountabilityScore: overallScore,
    accountabilityLevel: overallLevel,
    totalEntities: results.length,
    criticalCount: results.filter(r => r.accountabilityScore < 40).length,
    atRiskCount: results.filter(r => r.accountabilityScore >= 40 && r.accountabilityScore < 60).length,
    noRaciCount: results.filter(r => !r.hasRaci).length,
    samePersonCount: results.filter(r => r.responsible === r.accountable && r.responsible).length,
    results,
    chains,
    personCoverage: personMap
  })
})

module.exports = router
