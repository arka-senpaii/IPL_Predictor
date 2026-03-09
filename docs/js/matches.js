/**
 * IPL Prediction Website — Matches JS
 * Handles: matches table, filtering, pagination, match detail page
 */

const MATCHES_PER_PAGE = 20;
let filteredMatches = [];
let currentPage = 1;

// ─── Matches Page ─────────────────────────────────────────
async function initMatchesPage() {
  await loadAllData();
  filteredMatches = [...allMatches];
  populateFilters();
  renderMatchesTable();
  setupMatchSearch();
}

function populateFilters() {
  const seasons = [...new Set(allMatches.map(m => m.season))].sort();
  const teams = [...new Set(allMatches.flatMap(m => [m.team1, m.team2]))].sort();
  const venues = [...new Set(allMatches.map(m => m.venue))].sort();

  fillSelect("filter-season", seasons.map(s => ({ val: s, label: s })));
  fillSelect("filter-team", teams.map(t => ({ val: t, label: t })));
  fillSelect("filter-venue", venues.map(v => ({ val: v, label: v })));

  ["filter-season", "filter-team", "filter-venue"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", applyFilters);
  });
}

function fillSelect(id, items) {
  const sel = document.getElementById(id);
  if (!sel) return;
  items.forEach(({ val, label }) => {
    const o = document.createElement("option");
    o.value = val; o.textContent = label;
    sel.appendChild(o);
  });
}

function setupMatchSearch() {
  const inp = document.getElementById("match-search");
  if (inp) inp.addEventListener("input", applyFilters);
}

function applyFilters() {
  const query = document.getElementById("match-search")?.value.toLowerCase() || "";
  const season = document.getElementById("filter-season")?.value || "";
  const team = document.getElementById("filter-team")?.value || "";
  const venue = document.getElementById("filter-venue")?.value || "";

  filteredMatches = allMatches.filter(m => {
    if (season && m.season !== season) return false;
    if (team && m.team1 !== team && m.team2 !== team) return false;
    if (venue && m.venue !== venue) return false;
    if (query) {
      const haystack = `${m.team1} ${m.team2} ${m.venue} ${m.winner} ${m.date} ${m.season}`.toLowerCase();
      if (!haystack.includes(query)) return false;
    }
    return true;
  });
  currentPage = 1;
  renderMatchesTable();
}

function renderMatchesTable() {
  const tbody = document.getElementById("matches-tbody");
  const countEl = document.getElementById("match-count");
  if (!tbody) return;

  const start = (currentPage - 1) * MATCHES_PER_PAGE;
  const pageData = filteredMatches.slice(start, start + MATCHES_PER_PAGE);

  if (countEl) countEl.textContent = `${filteredMatches.length} matches`;

  tbody.innerHTML = pageData.map(m => {
    const t1Meta = getTeamMeta(m.team1);
    const t2Meta = getTeamMeta(m.team2);
    const winnerMeta = getTeamMeta(m.winner);

    // Score string
    const score1 = m.team1_score
      ? `${m.team1_score}/${m.team1_wickets}`
      : "—";
    const score2 = m.team2_score
      ? `${m.team2_score}/${m.team2_wickets}`
      : "—";

    return `
      <tr onclick="viewMatch(${m.match_id})" title="Click to view match details">
        <td style="color:var(--text-muted)">${formatDate(m.date)}</td>
        <td style="color:var(--text-muted);font-size:0.8rem">${m.season}</td>
        <td>
          <span class="team-cell">
            <img src="${t1Meta.logo}" width="22" height="22" 
              style="object-fit:contain;border-radius:3px" 
              onerror="this.style.display='none'"
              alt="${m.team1}">
            ${m.team1}
          </span>
          <span style="color:var(--text-muted);margin:0 0.4rem;font-size:0.8rem">vs</span>
          <span class="team-cell">
            <img src="${t2Meta.logo}" width="22" height="22"
              style="object-fit:contain;border-radius:3px"
              onerror="this.style.display='none'"
              alt="${m.team2}">
            ${m.team2}
          </span>
        </td>
        <td style="font-size:0.82rem">
          <span style="color:${t1Meta.color};font-weight:700">${score1}</span>
          &nbsp;/&nbsp;
          <span style="color:${t2Meta.color};font-weight:700">${score2}</span>
        </td>
        <td>
          <span class="team-cell">
            <img src="${winnerMeta.logo}" width="18" height="18"
              style="object-fit:contain;border-radius:3px"
              onerror="this.style.display='none'"
              alt="${m.winner}">
            <span style="color:var(--accent-green);font-weight:700">${m.winner}</span>
          </span>
          ${m.win_outcome ? `<span style="color:var(--text-muted);font-size:0.75rem;display:block">${m.win_outcome}</span>` : ""}
        </td>
        <td style="color:var(--text-muted);font-size:0.8rem;max-width:160px;overflow:hidden;text-overflow:ellipsis">${m.venue}</td>
        <td style="color:var(--text-muted);font-size:0.8rem">${m.stage || ""}</td>
      </tr>`;
  }).join("");

  renderPagination();
}

function renderPagination() {
  const container = document.getElementById("pagination");
  if (!container) return;
  const totalPages = Math.ceil(filteredMatches.length / MATCHES_PER_PAGE);

  let html = "";
  const maxBtns = 7;
  let start = Math.max(1, currentPage - Math.floor(maxBtns / 2));
  let end = Math.min(totalPages, start + maxBtns - 1);
  if (end - start < maxBtns - 1) start = Math.max(1, end - maxBtns + 1);

  if (currentPage > 1) html += `<button class="page-btn" onclick="goPage(${currentPage - 1})">‹</button>`;
  if (start > 1) html += `<button class="page-btn" onclick="goPage(1)">1</button><span style="color:var(--text-muted);padding:0 0.25rem">…</span>`;

  for (let i = start; i <= end; i++) {
    html += `<button class="page-btn ${i === currentPage ? "active" : ""}" onclick="goPage(${i})">${i}</button>`;
  }

  if (end < totalPages) html += `<span style="color:var(--text-muted);padding:0 0.25rem">…</span><button class="page-btn" onclick="goPage(${totalPages})">${totalPages}</button>`;
  if (currentPage < totalPages) html += `<button class="page-btn" onclick="goPage(${currentPage + 1})">›</button>`;

  container.innerHTML = html;
}

function goPage(p) {
  currentPage = p;
  renderMatchesTable();
  document.getElementById("matches-table-section")?.scrollIntoView({ behavior: "smooth" });
}

function viewMatch(matchId) {
  window.location.href = `match.html?id=${matchId}`;
}

// ─── Match Detail Page ────────────────────────────────────
async function initMatchDetailPage() {
  await loadAllData();
  const params = new URLSearchParams(location.search);
  const matchId = parseInt(params.get("id"));
  const match = allMatches.find(m => m.match_id === matchId);
  if (!match) {
    document.getElementById("match-detail-root").innerHTML = `<div class="container" style="padding:4rem 0;text-align:center;color:var(--text-muted)">Match not found.<br><a href="matches.html" class="btn btn-outline" style="margin-top:1rem">← Back to Matches</a></div>`;
    return;
  }

  document.title = `${match.team1} vs ${match.team2} — IPL Predictor`;
  renderMatchDetail(match);
}

function renderMatchDetail(m) {
  const root = document.getElementById("match-detail-root");
  if (!root) return;

  const t1Meta = getTeamMeta(m.team1);
  const t2Meta = getTeamMeta(m.team2);
  const winnerMeta = getTeamMeta(m.winner);

  root.innerHTML = `
    <div class="container">
      <div class="match-header fade-in">
        <a href="matches.html" class="btn btn-outline" style="margin-bottom:1.5rem;display:inline-flex">← All Matches</a>
        <div class="match-meta">
          <span class="pill">📅 ${formatDate(m.date)}</span>
          <span class="pill">🏟️ ${m.venue}</span>
          <span class="pill">🏆 ${m.season}</span>
          ${m.stage ? `<span class="pill">📋 ${m.stage}</span>` : ""}
          ${m.toss_winner ? `<span class="pill">🪙 Toss: ${m.toss_winner} (${m.toss_decision})</span>` : ""}
        </div>

        <div class="card">
          <div class="scorecard">
            <div class="scorecard-team">
              <img class="team-logo-lg" 
                src="${t1Meta.logo}" 
                alt="${m.team1}"
                onerror="this.style.display='none'">
              <div class="sc-name">${m.team1}</div>
              <div class="sc-score">${m.team1_score}/${m.team1_wickets}</div>
              <div class="sc-detail">${calcOvers(m.team1_wickets)} overs</div>
            </div>
            <div class="scorecard-vs">
              <div style="font-size:0.65rem;color:var(--text-muted);margin-bottom:0.3rem">MATCH</div>
              <div style="font-size:1.5rem;font-weight:900;">VS</div>
              <div style="font-size:0.65rem;color:var(--text-muted);margin-top:0.3rem">#${m.match_id}</div>
            </div>
            <div class="scorecard-team">
              <img class="team-logo-lg"
                src="${t2Meta.logo}"
                alt="${m.team2}"
                onerror="this.style.display='none'">
              <div class="sc-name">${m.team2}</div>
              <div class="sc-score">${m.team2_score}/${m.team2_wickets}</div>
              <div class="sc-detail">${calcOvers(m.team2_wickets)} overs</div>
            </div>
          </div>

          <div class="winner-announce">
            🏆 ${m.winner} won 
            ${m.win_outcome ? `by <strong>${m.win_outcome}</strong>` : ""}
          </div>
          ${m.player_of_match ? `<div style="text-align:center;margin-top:0.75rem;font-size:0.85rem;color:var(--text-muted)">⭐ Player of the Match: <strong style="color:var(--accent-gold)">${m.player_of_match}</strong></div>` : ""}
        </div>
      </div>

      <!-- Charts -->
      <h2 style="font-size:1.3rem;font-weight:800;margin:2.5rem 0 1.25rem">
        Match Analysis <span style="color:var(--accent-gold)">Charts</span>
      </h2>

      <div class="charts-grid">
        <div class="chart-card">
          <h3>📈 Score Progression</h3>
          <div class="chart-container"><canvas id="chart-progression" height="220"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>🏏 Runs Per Over</h3>
          <div class="chart-container"><canvas id="chart-runs-over" height="220"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>🎯 Wickets Per Over</h3>
          <div class="chart-container"><canvas id="chart-wickets" height="220"></canvas></div>
        </div>
        <div class="chart-card" style="display:flex;flex-direction:column;justify-content:center">
          <h3>📊 Head-to-Head</h3>
          <canvas id="chart-h2h" height="160"></canvas>
        </div>
      </div>
    </div>`;

  // Render charts after DOM updated
  requestAnimationFrame(() => {
    renderScoreProgression(m, "chart-progression");
    renderRunsPerOver(m, "chart-runs-over");
    renderWicketsChart(m, "chart-wickets");

    // H2H
    const key1 = `${m.team1}||${m.team2}`;
    const key2 = `${m.team2}||${m.team1}`;
    const h2h = DATA.h2h?.[key1] || DATA.h2h?.[key2];
    if (h2h) {
      const t1wins = h2h.team1 === m.team1 ? h2h.team1_wins : h2h.team2_wins;
      const t2wins = h2h.team1 === m.team1 ? h2h.team2_wins : h2h.team1_wins;
      renderH2HChart(m.team1, m.team2, t1wins, t2wins, "chart-h2h");
    }
  });
}

function calcOvers(wickets) {
  return wickets >= 10 ? "20.0" : "~20.0";
}
