/**
 * IPL Prediction Website — Main App JS
 * Handles: data loading, team selection, prediction display
 */

const DATA = {};
let allMatches = [];

// IPL Team metadata: colors, Wikipedia logo URLs, abbreviation
const TEAM_META = {
  "Chennai Super Kings": {
    abbr: "CSK", color: "#f5a623",
    logo: "assets/logos/csk.png"
  },
  "Mumbai Indians": {
    abbr: "MI", color: "#004ba0",
    logo: "assets/logos/mi.png"
  },
  "Royal Challengers Bengaluru": {
    abbr: "RCB", color: "#e01c23",
    logo: "assets/logos/rcb.png"
  },
  "Kolkata Knight Riders": {
    abbr: "KKR", color: "#3a225d",
    logo: "assets/logos/kkr.png"
  },
  "Sunrisers Hyderabad": {
    abbr: "SRH", color: "#f4682c",
    logo: "assets/logos/srh.png"
  },
  "Delhi Capitals": {
    abbr: "DC", color: "#0078bc",
    logo: "assets/logos/dc.png"
  },
  "Rajasthan Royals": {
    abbr: "RR", color: "#e91e8c",
    logo: "assets/logos/rr.png"
  },
  "Punjab Kings": {
    abbr: "PBKS", color: "#ed1b24",
    logo: "assets/logos/pbks.png"
  },
  "Gujarat Titans": {
    abbr: "GT", color: "#1c4887",
    logo: "assets/logos/gt.png"
  },
  "Lucknow Super Giants": {
    abbr: "LSG", color: "#00a4e4",
    logo: "assets/logos/lsg.png"
  },
  "Deccan Chargers": {
    abbr: "DCH", color: "#f05a22",
    logo: "assets/logos/deccan_chargers.png"
  },
  "Rising Pune Supergiant": {
    abbr: "RPS", color: "#6c4b9e",
    logo: "assets/logos/rising_pune.png"
  },
  "Kochi Tuskers Kerala": {
    abbr: "KTK", color: "#f7941e",
    logo: "assets/logos/kochi_tuskers.png"
  },
  "Pune Warriors": {
    abbr: "PW", color: "#1c87c9",
    logo: "assets/logos/pune_warriors.png"
  },
  "Gujarat Lions": {
    abbr: "GL", color: "#e44d26",
    logo: "assets/logos/gujarat_lions.png"
  },
};

function getTeamMeta(name) {
  return TEAM_META[name] || { abbr: name.split(" ").map(w=>w[0]).join("").slice(0,3), color: "#4a9eff", logo: "" };
}

function teamLogo(name, size = 28) {
  const meta = getTeamMeta(name);
  if (meta.logo) {
    // We add an onerror handler that replaces the broken image with our badge
    return `<img src="${meta.logo}" width="${size}" height="${size}" 
             style="object-fit:contain;border-radius:4px" 
             onerror="this.outerHTML = teamAbbrBadgeString('${meta.abbr}', '${meta.color}', ${size})"
             alt="${name}">`;
  }
  return teamAbbrBadgeString(meta.abbr, meta.color, size);
}

// Helper to return HTML string instead of DOM node for easier inline usage
function teamAbbrBadgeString(abbr, color, size = 28) {
  return `<span style="display:inline-flex;align-items:center;justify-content:center;
    width:${size}px;height:${size}px;border-radius:4px;background:${color}20;
    border:1px solid ${color}60;color:${color};font-weight:800;font-size:${Math.floor(size*0.35)}px;">
    ${abbr}
  </span>`;
}

// Keep the DOM node version for places that expect it (like some older code if any)
function teamAbbrBadge(abbr, color, size = 28) {
  const span = document.createElement("span");
  span.innerHTML = teamAbbrBadgeString(abbr, color, size);
  return span.firstElementChild;
}

// ─── Load Data ───────────────────────────────────────────
async function loadData(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Failed to load ${url}`);
  return r.json();
}

async function loadAllData() {
  try {
    const [matches, teams, h2h, seasons, predictions, venues] = await Promise.all([
      loadData("data/matches.json"),
      loadData("data/teams.json"),
      loadData("data/h2h.json"),
      loadData("data/seasons.json"),
      loadData("data/predictions.json").catch(() => ({})),
      loadData("data/venues.json"),
    ]);
    DATA.matches = matches;
    DATA.teams = teams;
    DATA.h2h = h2h;
    DATA.seasons = seasons;
    DATA.predictions = predictions;
    DATA.venues = venues;
    allMatches = matches;
    return true;
  } catch(e) {
    console.error("Data load error:", e);
    return false;
  }
}

// ─── Prediction Logic ─────────────────────────────────────
function getPrediction(team1, team2, venue = "") {
  const pred = DATA.predictions || {};
  const key1 = `${team1} vs ${team2}`;
  const key2 = `${team2} vs ${team1}`;

  if (pred[key1]) {
    const p = pred[key1];
    let t1prob = p.team1_win_prob;
    if (venue && p.by_venue && p.by_venue[venue] !== undefined) {
      t1prob = p.by_venue[venue];
    }
    return { team1prob: t1prob, team2prob: 1 - t1prob };
  }
  if (pred[key2]) {
    const p = pred[key2];
    let t2prob = p.team1_win_prob;
    if (venue && p.by_venue && p.by_venue[venue] !== undefined) {
      t2prob = p.by_venue[venue];
    }
    return { team1prob: 1 - t2prob, team2prob: t2prob };
  }

  // Fallback to team win rates
  const t1stats = DATA.teams?.[team1];
  const t2stats = DATA.teams?.[team2];
  if (t1stats && t2stats) {
    const t1wr = t1stats.win_pct / 100;
    const t2wr = t2stats.win_pct / 100;
    const total = t1wr + t2wr;
    return { team1prob: t1wr / total, team2prob: t2wr / total };
  }
  return { team1prob: 0.5, team2prob: 0.5 };
}

// ─── UI Helpers ───────────────────────────────────────────
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function getTeamColor(name) {
  return getTeamMeta(name).color;
}

// ─── Populate Team Dropdowns ─────────────────────────────
function populateTeamDropdowns(select1Id, select2Id) {
  const teams = Object.keys(DATA.teams || {}).sort();
  [select1Id, select2Id].forEach(id => {
    const sel = document.getElementById(id);
    if (!sel) return;
    sel.innerHTML = '<option value="">Select Team</option>';
    teams.forEach(t => {
      const opt = document.createElement("option");
      opt.value = t; opt.textContent = t;
      sel.appendChild(opt);
    });
  });
}

function populateVenueDropdown(selectId) {
  const venues = Object.keys(DATA.venues || {}).sort();
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = '<option value="">Any Venue</option>';
  venues.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v; opt.textContent = v;
    sel.appendChild(opt);
  });
}

// ─── Number animation ────────────────────────────────────
function animateNumber(el, target, duration = 1200) {
  const start = performance.now();
  const from = parseFloat(el.textContent) || 0;
  function update(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(from + (target - from) * ease);
    if (t < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// Active nav link
document.addEventListener("DOMContentLoaded", () => {
  const path = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a").forEach(a => {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });
});
