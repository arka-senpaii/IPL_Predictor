/**
 * IPL Prediction Website — Charts (Chart.js)
 */

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { labels: { color: "#8892b0", font: { family: "Outfit", size: 11, weight: "600" } } },
    tooltip: {
      backgroundColor: "#141929",
      titleColor: "#f0f4ff",
      bodyColor: "#8892b0",
      borderColor: "rgba(255,255,255,0.1)",
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
    }
  },
  scales: {
    x: { ticks: { color: "#4a5568", font: { family: "Outfit", size: 10 } }, grid: { color: "rgba(255,255,255,0.04)" } },
    y: { ticks: { color: "#4a5568", font: { family: "Outfit", size: 10 } }, grid: { color: "rgba(255,255,255,0.04)" } },
  }
};

function mergeDefaults(cfg) {
  return {
    ...cfg,
    options: {
      ...CHART_DEFAULTS,
      ...(cfg.options || {}),
      plugins: { ...CHART_DEFAULTS.plugins, ...(cfg.options?.plugins || {}) },
      scales: { ...CHART_DEFAULTS.scales, ...(cfg.options?.scales || {}) },
    }
  };
}

const chartInstances = {};

function destroyChart(id) {
  if (chartInstances[id]) { chartInstances[id].destroy(); delete chartInstances[id]; }
}

// ─── Score Progression Chart ──────────────────────────────
function renderScoreProgression(matchData, canvasId) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const inn1 = matchData.over_progression?.innings1 || [];
  const inn2 = matchData.over_progression?.innings2 || [];
  const maxOvers = Math.max(inn1.length, inn2.length, 1);
  const labels = Array.from({ length: maxOvers }, (_, i) => `Ov ${i + 1}`);

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: `${matchData.team1} (Inn 1)`,
          data: inn1.map(o => o.cumulative_runs),
          borderColor: getTeamColor(matchData.team1),
          backgroundColor: getTeamColor(matchData.team1) + "22",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2.5,
        },
        {
          label: `${matchData.team2} (Inn 2)`,
          data: inn2.map(o => o.cumulative_runs),
          borderColor: getTeamColor(matchData.team2),
          backgroundColor: getTeamColor(matchData.team2) + "22",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2.5,
        },
      ]
    },
    options: {
      plugins: { legend: { display: true } },
      scales: {
        y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: "Runs", color: "#4a5568", font: { size: 10 } } }
      }
    }
  }));
}

// ─── Runs per Over (bar) ─────────────────────────────────
function renderRunsPerOver(matchData, canvasId) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const inn1 = matchData.over_progression?.innings1 || [];
  const inn2 = matchData.over_progression?.innings2 || [];
  const maxOvers = Math.max(inn1.length, inn2.length, 1);
  const labels = Array.from({ length: maxOvers }, (_, i) => `${i + 1}`);

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: matchData.team1,
          data: labels.map((_, i) => inn1[i]?.runs ?? 0),
          backgroundColor: getTeamColor(matchData.team1) + "cc",
          borderRadius: 4,
          borderSkipped: false,
        },
        {
          label: matchData.team2,
          data: labels.map((_, i) => inn2[i]?.runs ?? 0),
          backgroundColor: getTeamColor(matchData.team2) + "cc",
          borderRadius: 4,
          borderSkipped: false,
        },
      ]
    },
    options: {
      plugins: { legend: { display: true } },
      scales: { y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: "Runs", color: "#4a5568" } } }
    }
  }));
}

// ─── Wickets per Over ────────────────────────────────────
function renderWicketsChart(matchData, canvasId) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const inn1 = matchData.over_progression?.innings1 || [];
  const inn2 = matchData.over_progression?.innings2 || [];
  const labels = Array.from({ length: Math.max(inn1.length, inn2.length, 1) }, (_, i) => `${i + 1}`);

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: `${matchData.team1} wkts`,
          data: labels.map((_, i) => inn1[i]?.wickets ?? 0),
          backgroundColor: getTeamColor(matchData.team1) + "aa",
          borderRadius: 4,
        },
        {
          label: `${matchData.team2} wkts`,
          data: labels.map((_, i) => inn2[i]?.wickets ?? 0),
          backgroundColor: getTeamColor(matchData.team2) + "aa",
          borderRadius: 4,
        },
      ]
    },
    options: {
      plugins: { legend: { display: true } },
      scales: {
        y: { ...CHART_DEFAULTS.scales.y, ticks: { ...CHART_DEFAULTS.scales.y.ticks, stepSize: 1 } }
      }
    }
  }));
}

// ─── Team Win Rate Doughnut ──────────────────────────────
function renderTeamWinRate(teamName, teamData, canvasId) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const color = getTeamColor(teamName);
  chartInstances[canvasId] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Wins", "Losses"],
      datasets: [{
        data: [teamData.wins, teamData.losses],
        backgroundColor: [color + "dd", "#1a2035"],
        borderColor: [color, "#1a2035"],
        borderWidth: 2,
        hoverOffset: 6,
      }]
    },
    options: {
      ...CHART_DEFAULTS,
      cutout: "72%",
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { display: false },
      },
      scales: {},
    }
  });
}

// ─── Season Performance Bar Chart ───────────────────────
function renderSeasonPerf(teamData, canvasId, teamColor) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const seasons = Object.entries(teamData.seasons || {}).sort((a, b) => a[0].localeCompare(b[0]));
  const labels = seasons.map(s => s[0]);
  const winData = seasons.map(s => s[1].wins);
  const matchData = seasons.map(s => s[1].matches);

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Wins",
          data: winData,
          backgroundColor: (teamColor || "#4a9eff") + "bb",
          borderRadius: 4,
        },
        {
          label: "Matches",
          data: matchData,
          backgroundColor: "rgba(255,255,255,0.06)",
          borderRadius: 4,
        },
      ]
    },
    options: { plugins: { legend: { display: true } } }
  }));
}

// ─── H2H Bar Chart ─────────────────────────────────────
function renderH2HChart(t1, t2, t1wins, t2wins, canvasId) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartInstances[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [t1, t2],
      datasets: [{
        label: "Wins",
        data: [t1wins, t2wins],
        backgroundColor: [getTeamColor(t1) + "cc", getTeamColor(t2) + "cc"],
        borderRadius: 8,
      }]
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: "y",
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: {
        x: CHART_DEFAULTS.scales.x,
        y: { ticks: { color: "#f0f4ff", font: { size: 11, weight: "700" } }, grid: { display: false } }
      }
    }
  });
}

// ─── Top Batsmen Bar chart ────────────────────────────────
function renderTopBatsmen(players, canvasId, color) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "bar",
    data: {
      labels: players.map(p => p.name),
      datasets: [{
        label: "Runs",
        data: players.map(p => p.runs),
        backgroundColor: (color || "#f5a623") + "cc",
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: {
        x: CHART_DEFAULTS.scales.x,
        y: { ticks: { color: "#f0f4ff", font: { size: 10, weight: "600" } }, grid: { display: false } }
      }
    }
  }));
}

// ─── Top Bowlers Bar chart ───────────────────────────────
function renderTopBowlers(players, canvasId, color) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "bar",
    data: {
      labels: players.map(p => p.name),
      datasets: [{
        label: "Wickets",
        data: players.map(p => p.wickets),
        backgroundColor: (color || "#7c5cbf") + "cc",
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: {
        x: CHART_DEFAULTS.scales.x,
        y: { ticks: { color: "#f0f4ff", font: { size: 10, weight: "600" } }, grid: { display: false } }
      }
    }
  }));
}

// ─── Season Champions Bar ────────────────────────────────
function renderChampionsBar(seasonsData, canvasId) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const champCount = {};
  Object.values(seasonsData).forEach(s => {
    if (s.champion && s.champion !== "Unknown") {
      champCount[s.champion] = (champCount[s.champion] || 0) + 1;
    }
  });
  const sorted = Object.entries(champCount).sort((a, b) => b[1] - a[1]);

  chartInstances[canvasId] = new Chart(ctx, mergeDefaults({
    type: "bar",
    data: {
      labels: sorted.map(s => s[0]),
      datasets: [{
        label: "Titles",
        data: sorted.map(s => s[1]),
        backgroundColor: sorted.map(s => getTeamColor(s[0]) + "cc"),
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: "y",
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: {
        x: { ...CHART_DEFAULTS.scales.x, ticks: { ...CHART_DEFAULTS.scales.x.ticks, stepSize: 1 } },
        y: { ticks: { color: "#f0f4ff", font: { size: 10, weight: "600" } }, grid: { display: false } }
      }
    }
  }));
}
