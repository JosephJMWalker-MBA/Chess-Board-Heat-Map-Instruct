const PIECE_URLS = {
  'p': 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg',
  'n': 'https://upload.wikimedia.org/wikipedia/commons/e/e5/Chess_ndt45.svg',
  'b': 'https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg',
  'r': 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg',
  'q': 'https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg',
  'k': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg',
  'P': 'https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg',
  'N': 'https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg',
  'B': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg',
  'R': 'https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg',
  'Q': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg',
  'K': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg'
};

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

let currentData = null;
let currentSquare = null;

// DOM Elements
const boardEl = document.getElementById('board');
const fileInput = document.getElementById('file-upload');
const modeSelect = document.getElementById('mode-select');
const roleSelect = document.getElementById('role-select');
const metricSelect = document.getElementById('metric-select');
const inspectorContent = document.getElementById('inspector-content');
const provenanceContent = document.getElementById('provenance-content');

// Init board HTML
function initBoard() {
  boardEl.innerHTML = '';
  for (let rank = 8; rank >= 1; rank--) {
    for (let fileIdx = 0; fileIdx < 8; fileIdx++) {
      const file = FILES[fileIdx];
      const sq = `${file}${rank}`;

      const isLight = (rank + fileIdx) % 2 !== 0;

      const div = document.createElement('div');
      div.className = `square ${isLight ? 'light' : 'dark'}`;
      div.id = `sq-${sq}`;
      div.dataset.sq = sq;

      const pieceDiv = document.createElement('div');
      pieceDiv.className = 'piece';
      pieceDiv.id = `piece-${sq}`;

      const overlayDiv = document.createElement('div');
      overlayDiv.className = 'overlay';
      overlayDiv.id = `overlay-${sq}`;

      div.appendChild(overlayDiv);
      div.appendChild(pieceDiv);

      div.addEventListener('click', () => selectSquare(sq));

      boardEl.appendChild(div);
    }
  }
}

// Render FEN
function renderFen(fen) {
  document.querySelectorAll('.piece').forEach(el => el.style.backgroundImage = 'none');

  if (!fen) return;
  const boardPart = fen.split(' ')[0];
  let rank = 8;
  let fileIdx = 0;

  for (let i = 0; i < boardPart.length; i++) {
    const char = boardPart[i];
    if (char === '/') {
      rank--;
      fileIdx = 0;
    } else if (/\d/.test(char)) {
      fileIdx += parseInt(char, 10);
    } else {
      const sq = `${FILES[fileIdx]}${rank}`;
      const pieceEl = document.getElementById(`piece-${sq}`);
      if (pieceEl && PIECE_URLS[char]) {
        pieceEl.style.backgroundImage = `url(${PIECE_URLS[char]})`;
      }
      fileIdx++;
    }
  }
}

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (ev) => {
    try {
      const data = JSON.parse(ev.target.result);
      loadData(data);
    } catch (err) {
      alert("Invalid JSON file");
      console.error(err);
    }
  };
  reader.readAsText(file);
}

function loadData(data) {
  currentData = data;
  const isPaired = !!data.transition_move;

  if (data.layer === 'recurrence') {
    provenanceContent.innerHTML = `
      <div class="data-row"><span class="data-label">Type:</span> <span>Recurrence Record</span></div>
      <div class="data-row"><span class="data-label">Policy:</span> <span>${JSON.stringify(data.candidate_policy)}</span></div>
      <div class="data-row"><span class="data-label">Engine:</span> <span>${data.engine_name}</span></div>
    `;
    modeSelect.value = 'recurrence';
  } else if (isPaired) {
    provenanceContent.innerHTML = `
      <div class="data-row"><span class="data-label">Type:</span> <span>Paired Transition</span></div>
      <div class="data-row"><span class="data-label">Move:</span> <span>${data.transition_move}</span></div>
      <div class="data-row"><span class="data-label">Comparison Perspective:</span> <span>${data.comparison_perspective}</span></div>
      <div class="data-row"><span class="data-label">Engine:</span> <span>${data.before_record.engine_name}</span></div>
    `;
    if (!['before', 'after', 'delta'].includes(modeSelect.value)) modeSelect.value = 'before';
  } else {
    provenanceContent.innerHTML = `
      <div class="data-row"><span class="data-label">Type:</span> <span>Single Record</span></div>
      <div class="data-row"><span class="data-label">Perspective:</span> <span>${data.root_side}</span></div>
      <div class="data-row"><span class="data-label">Engine:</span> <span>${data.engine_name}</span></div>
    `;
    modeSelect.value = 'before';
  }

  updateVisualization();
  if (currentSquare) {
    selectSquare(currentSquare);
  }
}

function filterMoves(moves, roleFilter) {
  if (roleFilter === 'all') return moves;
  return moves.filter(m => m.roles.includes(roleFilter));
}

function calculateMetric(moves, metricFilter) {
  if (moves.length === 0) return null;
  if (metricFilter === 'move_count') return moves.length;
  if (metricFilter === 'mate_count') return moves.filter(m => m.outcome.type === 'mate').length;

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

function getColor(value, metricFilter) {
  if (metricFilter.includes('regret')) {
    const capped = Math.max(0, Math.min(200, value));
    return `rgba(229, 62, 62, ${(capped / 200) * 0.8})`;
  }
  if (metricFilter.includes('outcome')) {
    if (value > 0) return `rgba(49, 130, 206, ${(Math.min(300, value) / 300) * 0.7})`;
    return `rgba(229, 62, 62, ${(Math.min(300, Math.abs(value)) / 300) * 0.7})`;
  }
  if (metricFilter === 'move_count') {
    return `rgba(128, 90, 213, ${0.2 + (Math.min(15, value) / 15) * 0.6})`;
  }
  if (metricFilter === 'mate_count') {
    return value > 0 ? `rgba(221, 107, 32, 0.7)` : 'transparent';
  }
  return 'transparent';
}

function getMetricValence(metricFilter) {
  if (metricFilter.includes('regret')) return 'inverse';
  if (metricFilter.includes('cp')) return 'positive';
  return 'neutral';
}

function getDeltaColor(delta, metricFilter) {
  if (delta === 0 || delta === null) return 'transparent';

  const valence = getMetricValence(metricFilter);
  const scaleLimit = metricFilter.includes('cp') ? 100 : 5;
  const intensity = Math.min(1.0, Math.abs(delta) / scaleLimit);

  if (valence === 'positive') {
    // Increase is good (blue), decrease is bad (red)
    return delta > 0 ? `rgba(49, 130, 206, ${intensity * 0.8})` : `rgba(229, 62, 62, ${intensity * 0.8})`;
  } else if (valence === 'inverse') {
    // Increase is bad (red), decrease is good (blue)
    return delta > 0 ? `rgba(229, 62, 62, ${intensity * 0.8})` : `rgba(49, 130, 206, ${intensity * 0.8})`;
  } else {
    // Neutral valence (purple for increase, orange for decrease, or just monochromatic)
    return delta > 0 ? `rgba(128, 90, 213, ${intensity * 0.8})` : `rgba(221, 107, 32, ${intensity * 0.8})`;
  }
}

function getStateColor(state) {
  if (state === 'appeared') return 'rgba(237, 137, 54, 0.6)';
  if (state === 'disappeared') return 'rgba(160, 174, 192, 0.6)';
  return 'transparent';
}

function getRecurrenceColor(value, metricFilter) {
  if (value === null || value === undefined || value === 0) return 'transparent';
  if (metricFilter === 'distinct_line_count' || metricFilter === 'visit_count') {
    return `rgba(56, 161, 105, ${0.2 + (Math.min(10, value) / 10) * 0.7})`; // Greenish
  }
  if (metricFilter === 'line_fraction') {
    return `rgba(56, 161, 105, ${0.2 + value * 0.7})`; // Greenish
  }
  if (metricFilter === 'earliest_ply') {
    // Lower ply is hotter (more immediate)
    return `rgba(214, 158, 46, ${1.0 - (Math.min(10, value) / 10) * 0.8})`; // Yellowish
  }
  return 'transparent';
}

function updateVisualization() {
  if (!currentData) return;

  const mode = modeSelect.value;
  const role = roleSelect.value;
  const metric = metricSelect.value;
  const isPaired = !!currentData.transition_move;

  let fen = currentData.fen;
  let attributions = currentData.attributions || {};

  if (isPaired) {
    if (mode === 'before') {
      fen = currentData.source_fen;
      attributions = currentData.before_attributions || {};
    } else if (mode === 'after' || mode === 'delta') {
      fen = currentData.resulting_fen;
      attributions = currentData.after_attributions || {};
    }
  }

  renderFen(fen);

  for (let rank = 1; rank <= 8; rank++) {
    for (let fileIdx = 0; fileIdx < 8; fileIdx++) {
      const sq = `${FILES[fileIdx]}${rank}`;
      const overlayEl = document.getElementById(`overlay-${sq}`);
      overlayEl.style.backgroundColor = 'transparent';
      overlayEl.style.border = 'none';

      if (mode === 'recurrence') {
        const sqRec = currentData.recurrence && currentData.recurrence[sq];
        if (sqRec) {
          const recData = role === 'all' ? sqRec.overall : sqRec.by_role[role];
          if (recData && recData[metric] !== undefined && recData[metric] !== null) {
            overlayEl.style.backgroundColor = getRecurrenceColor(recData[metric], metric);
          }
        }
      } else if (mode === 'delta' && isPaired) {
        const sqDelta = currentData.deltas[sq]?.roles[role]?.metrics[metric];
        if (sqDelta) {
          if (sqDelta.state === 'persisted' && sqDelta.delta !== null && sqDelta.delta !== 0) {
            overlayEl.style.backgroundColor = getDeltaColor(sqDelta.delta, metric);
          } else if (sqDelta.state === 'appeared' || sqDelta.state === 'disappeared') {
            overlayEl.style.backgroundColor = getStateColor(sqDelta.state);
          }
        }
      } else {
        if (attributions[sq]) {
          const val = calculateMetric(filterMoves(attributions[sq].implicated_moves || [], role), metric);
          if (val !== null) overlayEl.style.backgroundColor = getColor(val, metric);
        }
      }
    }
  }
}

function selectSquare(sq) {
  currentSquare = sq;
  document.querySelectorAll('.square').forEach(el => el.classList.remove('selected'));
  document.getElementById(`sq-${sq}`).classList.add('selected');

  if (!currentData) return;

  const mode = modeSelect.value;
  const role = roleSelect.value;
  const metric = metricSelect.value;
  const isPaired = !!currentData.transition_move;

  let html = `<h3>Square: ${sq}</h3>`;
  html += `<div class="data-row"><span class="data-label">Layer:</span> <span>${role} -> ${metric}</span></div>`;

  if (mode === 'recurrence') {
    const sqRec = currentData.recurrence && currentData.recurrence[sq];
    if (sqRec) {
       const recData = role === 'all' ? sqRec.overall : sqRec.by_role[role];
       if (recData) {
         html += `<div class="data-row"><span class="data-label">Distinct Lines:</span> <span>${recData.distinct_line_count}</span></div>`;
         html += `<div class="data-row"><span class="data-label">Line Fraction:</span> <span>${recData.line_fraction.toFixed(2)}</span></div>`;
         html += `<div class="data-row"><span class="data-label">Visit Count:</span> <span>${recData.visit_count}</span></div>`;
         html += `<div class="data-row"><span class="data-label">Earliest Ply:</span> <span>${recData.earliest_ply !== null ? recData.earliest_ply : 'none'}</span></div>`;
       } else {
         html += `<div class="data-row"><span class="data-label">Displayed value:</span> <span>no data</span></div>`;
       }
    } else {
       html += `<div class="data-row"><span class="data-label">Displayed value:</span> <span>no data</span></div>`;
    }
  } else if (mode === 'delta' && isPaired) {
    let attributions = currentData.attributions || {};
    if (isPaired) {
      attributions = mode === 'before' ? currentData.before_attributions : currentData.after_attributions;
    }

    if (attributions[sq]) {
      const moves = attributions[sq].implicated_moves || [];
      const filteredMoves = filterMoves(moves, role);
      const val = calculateMetric(filteredMoves, metric);

      html += `<div class="data-row"><span class="data-label">Displayed value:</span> <span>${val !== null ? val : 'no data'}</span></div>`;

      html += `<h3 style="margin-top: 15px;">Implicated Moves (${filteredMoves.length})</h3>`;
      html += `<div class="move-list">`;
      filteredMoves.forEach(m => {
        html += `<div class="move-item">`;
        html += `<div class="move-item-header">${m.uci}${m.promotion ? m.promotion : ''}</div>`;
        html += `<div class="data-row"><span class="data-label">Roles:</span> <span>${m.roles.join(', ')}</span></div>`;
        let outcomeStr = m.outcome.type === 'cp' ? `${m.outcome.value} cp` : `mate in ${m.outcome.value}`;
        html += `<div class="data-row"><span class="data-label">Outcome:</span> <span>${outcomeStr}</span></div>`;
        if (m.regret) {
          let regretStr = m.regret.type === 'cp' ? `${m.regret.value} cp` : m.regret.type;
          html += `<div class="data-row"><span class="data-label">Regret:</span> <span>${regretStr}</span></div>`;
        }
        html += `</div>`;
      });
      html += `</div>`;
    } else {
      html += `<div class="data-row"><span class="data-label">Displayed value:</span> <span>no data</span></div>`;
    }
  }

  inspectorContent.innerHTML = html;
}

// Setup listeners
fileInput.addEventListener('change', handleFileUpload);
['mode-select', 'role-select', 'metric-select'].forEach(id => {
  document.getElementById(id).addEventListener('change', () => {
    updateVisualization();
    if (currentSquare) selectSquare(currentSquare);
  });
});

initBoard();
