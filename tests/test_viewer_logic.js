const fs = require('fs');
const assert = require('assert');

// Simulate the viewer logic we are auditing
function filterMoves(moves, roleFilter) {
  if (roleFilter === 'all') return moves;
  return moves.filter(m => m.roles.includes(roleFilter));
}

function calculateMetric(moves, metricFilter) {
  if (moves.length === 0) return null;

  if (metricFilter === 'move_count') return moves.length;

  if (metricFilter === 'mate_count') {
    return moves.filter(m => m.outcome.type === 'mate').length;
  }

  const cpOutcomes = moves.filter(m => m.outcome.type === 'cp').map(m => m.outcome.value);
  const cpRegrets = moves.filter(m => m.regret && m.regret.type === 'cp' && m.regret.value !== null).map(m => m.regret.value);

  if (metricFilter.includes('outcome')) {
    if (cpOutcomes.length === 0) return null;
    if (metricFilter === 'best_cp') return Math.max(...cpOutcomes);
    if (metricFilter === 'worst_cp') return Math.min(...cpOutcomes);
    if (metricFilter === 'mean_cp') return cpOutcomes.reduce((a,b)=>a+b,0) / cpOutcomes.length;
  }

  if (metricFilter.includes('regret')) {
    if (cpRegrets.length === 0) return null;
    if (metricFilter === 'min_cp_regret') return Math.min(...cpRegrets);
    if (metricFilter === 'max_cp_regret') return Math.max(...cpRegrets);
    if (metricFilter === 'mean_cp_regret') return cpRegrets.reduce((a,b)=>a+b,0) / cpRegrets.length;
  }

  return null;
}

// 1. "changing the viewer's role filter does not change an implicated move's regret;"
// 2. "role-specific min/max/mean operations use stored move-level regret;"
function test_javascript_semantics() {
  const mockMoves = [
    {
      uci: 'd2d4',
      roles: ['origin'],
      outcome: { type: 'cp', value: 34, perspective: 'white' },
      regret: { type: 'cp', value: 4, perspective: 'white' }
    },
    {
      uci: 'd2d3',
      roles: ['origin'],
      outcome: { type: 'cp', value: -6, perspective: 'white' },
      regret: { type: 'cp', value: 44, perspective: 'white' }
    }
  ];

  // The regret object itself is immutable in the filter process
  const filtered = filterMoves(mockMoves, 'origin');
  assert.strictEqual(filtered[0].regret.value, 4);
  assert.strictEqual(filtered[1].regret.value, 44);

  // Role-specific operations use stored move-level regret
  const minRegret = calculateMetric(filtered, 'min_cp_regret');
  const maxRegret = calculateMetric(filtered, 'max_cp_regret');
  const meanRegret = calculateMetric(filtered, 'mean_cp_regret');

  assert.strictEqual(minRegret, 4);
  assert.strictEqual(maxRegret, 44);
  assert.strictEqual(meanRegret, 24); // (4 + 44) / 2

  // Singleton destination
  const mockDestMoves = [
    {
      uci: 'd2d4',
      roles: ['destination'],
      outcome: { type: 'cp', value: 34, perspective: 'white' },
      regret: { type: 'cp', value: 4, perspective: 'white' }
    }
  ];

  const destMinRegret = calculateMetric(filterMoves(mockDestMoves, 'destination'), 'min_cp_regret');
  // Must preserve 4, not 0
  assert.strictEqual(destMinRegret, 4);

  console.log("JavaScript semantics tests passed.");
}

function getMetricValence(metricFilter) {
  if (metricFilter.includes('regret')) return 'inverse';
  if (metricFilter.includes('cp')) return 'positive';
  return 'neutral';
}

function test_valence_semantics() {
  assert.strictEqual(getMetricValence('min_cp_regret'), 'inverse');
  assert.strictEqual(getMetricValence('max_cp_regret'), 'inverse');
  assert.strictEqual(getMetricValence('best_cp'), 'positive');
  assert.strictEqual(getMetricValence('worst_cp'), 'positive');
  assert.strictEqual(getMetricValence('move_count'), 'neutral');
  assert.strictEqual(getMetricValence('mate_count'), 'neutral');
  console.log("JavaScript valence tests passed.");
}

test_javascript_semantics();
test_valence_semantics();
