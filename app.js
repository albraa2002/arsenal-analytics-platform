/**
 * ══════════════════════════════════════════════════════════════════
 * ARSENAL FC 2025/26 — Football Analytics Dashboard
 * Vanilla JS · Plotly · PapaParse
 * ══════════════════════════════════════════════════════════════════
 */

(function () {
  "use strict";

  // ─── Constants ─────────────────────────────────────────────────
  const RED = "#EF0107";
  const CYAN = "#00F5FF";
  const NAVY = "#0B1020";
  const GOLD = "#9C824A";
  const BG = "#060B18";
  const GRID = "#1A2332";
  const TXT = "#8892B0";
  const WHITE = "#F0F4FF";

  const PLOTLY_LAYOUT = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { color: TXT, family: "Cairo, sans-serif" },
    margin: { l: 50, r: 20, t: 30, b: 40 },
    hovermode: "x unified",
    xaxis: { gridcolor: GRID, zerolinecolor: GRID },
    yaxis: { gridcolor: GRID, zerolinecolor: GRID },
  };

  const PLOTLY_CONFIG = { responsive: true, displayModeBar: false };

  // ─── Synthetic Data Generator ─────────────────────────────────
  function generateData() {
    const players = [
      { name: "Saka", pos: "MID", age: 23, num: 7, apps: 34, mins: 2950,
        xg_90: 0.46, xa_90: 0.27, prog_p: 8.5, prog_c: 6.2, touches_90: 78,
        pass_pct: 86.2, tackles_90: 1.8, interceptions_90: 1.2, def_90: 4.5,
        goals: 18, assists: 10, shots_90: 3.2, key_p_90: 2.4, bonus: 18,
        price: 10.5, owned: 42.3, form: 7.4, ict: 284.5, ppg: 6.2, total_pts: 198 },
      { name: "Odegaard", pos: "MID", age: 26, num: 8, apps: 33, mins: 2850,
        xg_90: 0.34, xa_90: 0.31, prog_p: 10.2, prog_c: 3.8, touches_90: 85,
        pass_pct: 88.5, tackles_90: 1.5, interceptions_90: 0.9, def_90: 3.2,
        goals: 10, assists: 12, shots_90: 2.5, key_p_90: 3.1, bonus: 14,
        price: 8.6, owned: 28.7, form: 6.1, ict: 256.3, ppg: 5.6, total_pts: 172 },
      { name: "Rice", pos: "MID", age: 25, num: 41, apps: 34, mins: 3000,
        xg_90: 0.19, xa_90: 0.14, prog_p: 6.8, prog_c: 4.5, touches_90: 72,
        pass_pct: 91.2, tackles_90: 2.8, interceptions_90: 2.1, def_90: 6.5,
        goals: 6, assists: 5, shots_90: 1.2, key_p_90: 1.1, bonus: 10,
        price: 6.5, owned: 18.2, form: 5.2, ict: 212.8, ppg: 4.8, total_pts: 145 },
      { name: "Havertz", pos: "MID", age: 25, num: 29, apps: 30, mins: 2400,
        xg_90: 0.41, xa_90: 0.22, prog_p: 5.2, prog_c: 3.1, touches_90: 58,
        pass_pct: 84.6, tackles_90: 1.1, interceptions_90: 0.6, def_90: 2.5,
        goals: 12, assists: 7, shots_90: 2.8, key_p_90: 1.8, bonus: 8,
        price: 7.8, owned: 15.6, form: 5.8, ict: 198.4, ppg: 4.6, total_pts: 138 },
      { name: "White", pos: "DF", age: 27, num: 4, apps: 33, mins: 2850,
        xg_90: 0.06, xa_90: 0.11, prog_p: 4.5, prog_c: 3.8, touches_90: 68,
        pass_pct: 89.8, tackles_90: 2.2, interceptions_90: 1.8, def_90: 5.8,
        goals: 2, assists: 4, shots_90: 0.4, key_p_90: 0.8, bonus: 12,
        price: 5.5, owned: 22.1, form: 4.5, ict: 168.7, ppg: 3.6, total_pts: 118 },
      { name: "Saliba", pos: "DF", age: 24, num: 2, apps: 34, mins: 3000,
        xg_90: 0.05, xa_90: 0.05, prog_p: 3.2, prog_c: 2.1, touches_90: 62,
        pass_pct: 92.4, tackles_90: 1.6, interceptions_90: 2.4, def_90: 5.2,
        goals: 3, assists: 1, shots_90: 0.3, key_p_90: 0.3, bonus: 9,
        price: 5.3, owned: 19.5, form: 3.8, ict: 145.6, ppg: 3.3, total_pts: 108 },
      { name: "Gabriel", pos: "DF", age: 27, num: 6, apps: 32, mins: 2880,
        xg_90: 0.11, xa_90: 0.04, prog_p: 2.8, prog_c: 1.5, touches_90: 55,
        pass_pct: 90.1, tackles_90: 1.4, interceptions_90: 1.9, def_90: 5.1,
        goals: 5, assists: 2, shots_90: 0.6, key_p_90: 0.2, bonus: 8,
        price: 5.1, owned: 16.8, form: 4.2, ict: 138.4, ppg: 3.1, total_pts: 98 },
      { name: "Zinchenko", pos: "DF", age: 28, num: 35, apps: 28, mins: 2200,
        xg_90: 0.04, xa_90: 0.12, prog_p: 5.8, prog_c: 4.2, touches_90: 74,
        pass_pct: 87.6, tackles_90: 1.9, interceptions_90: 1.4, def_90: 4.2,
        goals: 1, assists: 5, shots_90: 0.3, key_p_90: 1.0, bonus: 4,
        price: 5.0, owned: 10.2, form: 3.5, ict: 112.3, ppg: 2.8, total_pts: 78 },
      { name: "Martinelli", pos: "FW", age: 23, num: 11, apps: 30, mins: 2400,
        xg_90: 0.33, xa_90: 0.18, prog_p: 4.2, prog_c: 5.5, touches_90: 52,
        pass_pct: 81.2, tackles_90: 0.8, interceptions_90: 0.5, def_90: 1.8,
        goals: 10, assists: 6, shots_90: 2.6, key_p_90: 1.5, bonus: 7,
        price: 7.2, owned: 14.8, form: 5.5, ict: 185.2, ppg: 4.3, total_pts: 128 },
      { name: "Trossard", pos: "FW", age: 30, num: 19, apps: 28, mins: 1800,
        xg_90: 0.31, xa_90: 0.19, prog_p: 3.5, prog_c: 2.8, touches_90: 48,
        pass_pct: 83.4, tackles_90: 0.6, interceptions_90: 0.4, def_90: 1.2,
        goals: 8, assists: 5, shots_90: 2.2, key_p_90: 1.6, bonus: 5,
        price: 6.8, owned: 8.5, form: 4.2, ict: 152.3, ppg: 3.8, total_pts: 105 },
      { name: "Jesus", pos: "FW", age: 28, num: 9, apps: 22, mins: 1500,
        xg_90: 0.69, xa_90: 0.25, prog_p: 3.8, prog_c: 4.2, touches_90: 56,
        pass_pct: 82.8, tackles_90: 0.9, interceptions_90: 0.5, def_90: 2.0,
        goals: 12, assists: 5, shots_90: 3.5, key_p_90: 1.8, bonus: 6,
        price: 8.0, owned: 12.4, form: 4.8, ict: 175.6, ppg: 5.1, total_pts: 112 },
      { name: "Raya", pos: "GK", age: 29, num: 22, apps: 35, mins: 3150,
        xg_90: 0, xa_90: 0.02, prog_p: 1.2, prog_c: 0.5, touches_90: 32,
        pass_pct: 78.5, tackles_90: 0.1, interceptions_90: 0.2, def_90: 0.5,
        goals: 0, assists: 1, shots_90: 0, key_p_90: 0.1, bonus: 15,
        price: 5.2, owned: 25.6, form: 5.0, ict: 122.5, ppg: 4.0, total_pts: 132 },
      { name: "Partey", pos: "MID", age: 31, num: 5, apps: 25, mins: 1850,
        xg_90: 0.09, xa_90: 0.11, prog_p: 4.8, prog_c: 3.5, touches_90: 62,
        pass_pct: 90.5, tackles_90: 2.4, interceptions_90: 1.6, def_90: 5.0,
        goals: 2, assists: 3, shots_90: 0.5, key_p_90: 0.7, bonus: 3,
        price: 5.4, owned: 6.8, form: 3.2, ict: 98.5, ppg: 2.9, total_pts: 72 },
      { name: "Nwaneri", pos: "MID", age: 18, num: 53, apps: 15, mins: 600,
        xg_90: 0.38, xa_90: 0.27, prog_p: 6.5, prog_c: 5.8, touches_90: 55,
        pass_pct: 88.2, tackles_90: 0.6, interceptions_90: 0.4, def_90: 1.2,
        goals: 4, assists: 3, shots_90: 2.1, key_p_90: 1.9, bonus: 2,
        price: 4.5, owned: 3.2, form: 4.8, ict: 65.4, ppg: 2.8, total_pts: 42 },
    ];

    // Generate matches
    const opponents = [
      "Wolves", "Aston Villa", "Bournemouth", "Brighton", "Chelsea",
      "Crystal Palace", "Everton", "Fulham", "Leicester", "Liverpool",
      "Man City", "Man United", "Newcastle", "Nott'm Forest", "Southampton",
      "Tottenham", "West Ham", "Ipswich", "Brentford"
    ];
    const results = [];
    const seed = 42;
    let rng = seed;
    function rand() { rng = (rng * 16807) % 2147483647; return (rng - 1) / 2147483646; }

    for (let i = 0; i < opponents.length; i++) {
      const gf = Math.floor(rand() * 4) + (rand() > 0.6 ? 1 : 0);
      const ga = Math.floor(rand() * 3);
      const xg = +(rand() * 2.5 + 1).toFixed(2);
      const xga = +(rand() * 2.0 + 0.5).toFixed(2);
      const poss = +(rand() * 15 + 50).toFixed(1);
      const shots = Math.floor(rand() * 15 + 8);
      const sot = Math.floor(rand() * 8 + 3);
      const ppda = +(rand() * 6 + 8).toFixed(1);
      const result = gf > ga ? "W" : gf === ga ? "D" : "L";
      results.push({
        match: `M${i + 1}`, opponent: opponents[i],
        gf, ga, xg, xga, poss, shots, sot, ppda, result,
        home: rand() > 0.5, isArsenal: true,
      });
    }

    return { players, matches: results };
  }

  const DATA = generateData();

  // ─── Navigation ────────────────────────────────────────────────
  const navLinks = document.querySelectorAll(".sidebar-nav a");
  const pages = document.querySelectorAll(".page");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const toggleBtn = document.getElementById("mobileToggle");

  function navigate(pageId) {
    pages.forEach(p => p.classList.remove("active"));
    navLinks.forEach(a => a.classList.remove("active"));
    const targetPage = document.getElementById("page-" + pageId);
    const targetLink = document.querySelector(`.sidebar-nav a[data-page="${pageId}"]`);
    if (targetPage) targetPage.classList.add("active");
    if (targetLink) targetLink.classList.add("active");
    // Close sidebar on mobile
    sidebar?.classList.remove("open");
    overlay?.classList.remove("show");
  }

  navLinks.forEach(a => {
    a.addEventListener("click", e => {
      e.preventDefault();
      navigate(a.dataset.page);
    });
  });

  toggleBtn?.addEventListener("click", () => {
    sidebar?.classList.toggle("open");
    overlay?.classList.toggle("show");
  });
  overlay?.addEventListener("click", () => {
    sidebar?.classList.remove("open");
    overlay?.classList.remove("show");
  });

  // ─── Utility ──────────────────────────────────────────────────
  function kpiCard(icon, label, value) {
    return `<div class="kpi-card">
      <div class="kpi-icon">${icon}</div>
      <div class="kpi-value">${value}</div>
      <div class="kpi-label">${label}</div>
    </div>`;
  }

  function el(id) { return document.getElementById(id); }

  // ─── Chart Renderers ──────────────────────────────────────────

  // ── 1. EXECUTIVE OVERVIEW ──
  function renderOverview() {
    const m = DATA.matches;
    const totalW = m.filter(x => x.result === "W").length;
    const totalD = m.filter(x => x.result === "D").length;
    const totalL = m.filter(x => x.result === "L").length;
    const totalGF = m.reduce((s, r) => s + r.gf, 0);
    const totalGA = m.reduce((s, r) => s + r.ga, 0);
    const totalXG = +m.reduce((s, r) => s + r.xg, 0).toFixed(1);
    const totalXGA = +m.reduce((s, r) => s + r.xga, 0).toFixed(1);
    const avgPoss = +(m.reduce((s, r) => s + r.poss, 0) / m.length).toFixed(1);
    const cs = m.filter(r => r.ga === 0).length;
    const winPct = +((totalW / m.length) * 100).toFixed(1);
    const points = totalW * 3 + totalD;
    const xPts = +(points + totalXG - totalXGA).toFixed(1);
    const avgPPDA = +(m.reduce((s, r) => s + r.ppda, 0) / m.length).toFixed(1);

    el("overviewKPIs").innerHTML = [
      kpiCard("🏆", "Points", points),
      kpiCard("🎯", "xPTS", xPts),
      kpiCard("⚽", "Goals For", totalGF),
      kpiCard("🛡️", "Goals Against", totalGA),
      kpiCard("📊", "Win %", winPct + "%"),
      kpiCard("🎯", "xG", totalXG),
      kpiCard("🛡️", "xGA", totalXGA),
      kpiCard("📏", "Possession", avgPoss + "%"),
    ].join("");

    // Form trend
    const matchNums = m.map((_, i) => i + 1);
    const cumPoints = m.reduce((acc, r) => {
      const last = acc.length ? acc[acc.length - 1] : 0;
      acc.push(last + (r.result === "W" ? 3 : r.result === "D" ? 1 : 0));
      return acc;
    }, []);
    Plotly.newPlot("chartFormTrend", [
      { x: matchNums, y: cumPoints, type: "scatter", mode: "lines+markers",
        name: "Points", line: { color: RED, width: 3 },
        marker: { size: 8, color: RED, line: { color: "white", width: 1 } },
        fill: "tozeroy", fillcolor: "rgba(239,1,7,0.08)" }
    ], { ...PLOTLY_LAYOUT, height: 340,
      xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Match" },
      yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Points" } }, PLOTLY_CONFIG);

    // Goals & xG trend
    const cumGF = m.reduce((a, r) => { a.push((a.length ? a[a.length-1] : 0) + r.gf); return a; }, []);
    const cumXG = m.reduce((a, r) => { a.push(+(a.length ? a[a.length-1] : 0) + r.xg).toFixed(1); return a; }, []);
    Plotly.newPlot("chartGoalsTrend", [
      { x: matchNums, y: cumGF, type: "scatter", mode: "lines+markers",
        name: "Goals", line: { color: RED, width: 3 }, marker: { size: 8, color: RED } },
      { x: matchNums, y: cumXG, type: "scatter", mode: "lines+markers",
        name: "xG", line: { color: CYAN, width: 3, dash: "dot" }, marker: { size: 8, color: CYAN } }
    ], { ...PLOTLY_LAYOUT, height: 340,
      xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Match" },
      yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Cumulative" } }, PLOTLY_CONFIG);

    // Result timeline
    const colors = m.map(r => r.result === "W" ? "#00D4AA" : r.result === "D" ? "#FFB347" : "#FF4757");
    Plotly.newPlot("chartResultTimeline", [
      { x: matchNums, y: m.map(r => r.gf), type: "bar", name: "GF",
        marker: { color: RED }, hovertemplate: "GF: %{y}<extra></extra>" },
      { x: matchNums, y: m.map(r => r.ga), type: "bar", name: "GA",
        marker: { color: "#4A5568" }, hovertemplate: "GA: %{y}<extra></extra>" },
    ], { ...PLOTLY_LAYOUT, height: 350, barmode: "group",
       xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Match", dtick: 1 },
       yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Goals" } }, PLOTLY_CONFIG);

    // Result split pie
    Plotly.newPlot("chartResultSplit", [{
      labels: ["Wins", "Draws", "Losses"], values: [totalW, totalD, totalL],
      type: "pie", marker: { colors: ["#00D4AA", "#FFB347", "#FF4757"] },
      hole: 0.6, textinfo: "label+percent", textfont: { color: "white", size: 13 },
      hovertemplate: "%{label}: %{value}<extra></extra>",
    }], { ...PLOTLY_LAYOUT, height: 350, showlegend: false,
       annotations: [{ text: `${totalW}W/${totalD}D/${totalL}L`,
         x: 0.5, y: 0.5, font: { size: 16, color: "white" }, showarrow: false }]
    }, PLOTLY_CONFIG);

    // Goal analysis gauge
    Plotly.newPlot("chartGoalAnalysis", [{
      type: "indicator", mode: "number+gauge+delta",
      value: totalGF, delta: { reference: totalGA, position: "top" },
      title: { text: "GF vs GA", font: { size: 14, color: TXT } },
      gauge: { axis: { range: [0, Math.max(totalGF, totalGA) + 5] },
               bar: { color: RED }, bgcolor: "rgba(0,0,0,0)",
               steps: [{ range: [0, totalGA], color: "rgba(239,1,7,0.12)" }],
               threshold: { line: { color: CYAN, width: 4 }, thickness: 0.75, value: totalGA } }
    }], { ...PLOTLY_LAYOUT, height: 260 }, PLOTLY_CONFIG);

    // xG vs Actual
    Plotly.newPlot("chartXgActual", [{
      x: ["xG", "Goals"], y: [totalXG, totalGF],
      type: "bar", marker: { color: [CYAN, RED] },
      text: [totalXG.toFixed(1), totalGF], textposition: "outside",
      textfont: { size: 16, color: "white" },
    }], { ...PLOTLY_LAYOUT, height: 260, showlegend: false,
       yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Total" } }, PLOTLY_CONFIG);

    // Defensive summary
    Plotly.newPlot("chartDefensive", [{
      type: "indicator", mode: "number+gauge+delta",
      value: cs, delta: { reference: m.length - cs, position: "top" },
      title: { text: "Clean Sheets", font: { size: 14, color: TXT } },
      gauge: { axis: { range: [0, m.length] },
               bar: { color: "#00D4AA" }, bgcolor: "rgba(0,0,0,0)",
               steps: [{ range: [0, Math.floor(m.length/2)], color: "rgba(0,212,170,0.1)" }],
               threshold: { line: { color: RED, width: 4 }, thickness: 0.75, value: m.length } }
    }], { ...PLOTLY_LAYOUT, height: 260 }, PLOTLY_CONFIG);

    // Populate tactical match selector
    const sel = el("tacticalMatch");
    if (sel) {
      sel.innerHTML = '<option value="all">All Matches</option>' +
        m.map((r, i) => `<option value="${i}">M${i + 1} vs ${r.opponent}</option>`).join("");
    }
    // Populate match selector
    const ms = el("matchSelector");
    if (ms) {
      ms.innerHTML = m.map((r, i) =>
        `<option value="${i}">M${i + 1}: Arsenal ${r.gf}-${r.ga} ${r.opponent}</option>`).join("");
      ms.value = m.length - 1;
    }
  }

  // ── 2. TACTICAL ANALYSIS ──
  function renderTactical() {
    const players = DATA.players;
    const m = DATA.matches;

    // Passing network — simulated positions
    const posMap = {
      "Raya": { x: 5, y: 34 }, "White": { x: 22, y: 55 }, "Saliba": { x: 22, y: 40 },
      "Gabriel": { x: 22, y: 28 }, "Zinchenko": { x: 22, y: 12 },
      "Partey": { x: 38, y: 22 }, "Rice": { x: 38, y: 45 }, "Odegaard": { x: 42, y: 34 },
      "Saka": { x: 58, y: 55 }, "Havertz": { x: 60, y: 34 }, "Martinelli": { x: 58, y: 12 },
      "Trossard": { x: 56, y: 18 }, "Jesus": { x: 62, y: 42 }, "Nwaneri": { x: 42, y: 28 }
    };

    // Network nodes & edges
    const pitchPlayers = players.filter(p => posMap[p.name]);
    const nodes = pitchPlayers.map(p => ({
      name: p.name, x: posMap[p.name].x, y: posMap[p.name].y,
      size: (p.prog_p || 5) * 2 + 15,
    }));

    const edges = [];
    // Create realistic pass connections
    const connections = [
      ["Raya", "White", 28], ["Raya", "Saliba", 25], ["Raya", "Gabriel", 22],
      ["White", "Saka", 35], ["White", "Rice", 20], ["White", "Odegaard", 15],
      ["Saliba", "Rice", 30], ["Saliba", "White", 18], ["Saliba", "Gabriel", 22],
      ["Gabriel", "Zinchenko", 32], ["Gabriel", "Rice", 18], ["Gabriel", "Partey", 15],
      ["Zinchenko", "Martinelli", 28], ["Zinchenko", "Rice", 12], ["Zinchenko", "Odegaard", 14],
      ["Rice", "Odegaard", 38], ["Rice", "Saka", 22], ["Rice", "White", 16],
      ["Partey", "Odegaard", 25], ["Partey", "Zinchenko", 18], ["Partey", "Rice", 20],
      ["Odegaard", "Saka", 42], ["Odegaard", "Havertz", 35], ["Odegaard", "Martinelli", 28],
      ["Saka", "Havertz", 28], ["Saka", "Odegaard", 20],
      ["Martinelli", "Havertz", 18], ["Martinelli", "Odegaard", 16],
      ["Havertz", "Saka", 22], ["Havertz", "Odegaard", 20],
    ];

    const nodeMap = {};
    nodes.forEach((n, i) => { nodeMap[n.name] = i; });

    const edgeTraces = connections.map(c => {
      const src = nodeMap[c[0]], tgt = nodeMap[c[1]];
      if (src === undefined || tgt === undefined) return null;
      return {
        x: [nodes[src].x, nodes[tgt].x],
        y: [nodes[src].y, nodes[tgt].y],
        type: "scatter", mode: "lines",
        line: { color: RED, width: Math.min(c[2] * 0.15, 4), opacity: 0.25 },
        hoverinfo: "none", showlegend: false,
      };
    }).filter(Boolean);

    const nodeTrace = {
      x: nodes.map(n => n.x), y: nodes.map(n => n.y),
      type: "scatter", mode: "markers+text",
      marker: { size: nodes.map(n => Math.min(n.size, 50)), color: CYAN,
                line: { color: "white", width: 1.5 } },
      text: nodes.map(n => n.name), textposition: "bottom center",
      textfont: { color: "white", size: 9, family: "IBM Plex Mono" },
      hoverinfo: "text", showlegend: false,
    };

    const passLayout = {
      ...PLOTLY_LAYOUT, height: 420,
      xaxis: { range: [0, 120], showgrid: false, zeroline: false, visible: false },
      yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
      shapes: [
        { type: "rect", x0: 0, y0: 0, x1: 120, y1: 80,
          line: { color: GRID, width: 1 }, fillcolor: "rgba(0,0,0,0)" },
        // Centre line
        { type: "line", x0: 60, y0: 0, x1: 60, y1: 80,
          line: { color: GRID, width: 1, dash: "dash" } },
        // Penalty areas
        { type: "rect", x0: 102, y0: 18, x1: 120, y1: 62,
          line: { color: GRID, width: 1 }, fillcolor: "rgba(0,0,0,0)" },
        { type: "rect", x0: 0, y0: 18, x1: 18, y1: 62,
          line: { color: GRID, width: 1 }, fillcolor: "rgba(0,0,0,0)" },
      ]
    };
    Plotly.newPlot("chartPassNetwork", [...edgeTraces, nodeTrace], passLayout, PLOTLY_CONFIG);

    // Average positions — scatter with touch counts
    const apNodes = pitchPlayers.map(p => ({
      name: p.name, x: posMap[p.name].x, y: posMap[p.name].y,
      touches: p.touches_90 || 50,
    }));

    Plotly.newPlot("chartAvgPositions", [{
      x: apNodes.map(n => n.x), y: apNodes.map(n => n.y),
      type: "scatter", mode: "markers+text",
      marker: {
        size: apNodes.map(n => Math.min(n.touches * 0.6, 55)),
        color: RED, line: { color: "white", width: 1.5 }, opacity: 0.8,
      },
      text: apNodes.map(n => n.name), textposition: "bottom center",
      textfont: { color: "white", size: 8, family: "IBM Plex Mono" },
      hoverinfo: "text", showlegend: false,
    }], {
      ...PLOTLY_LAYOUT, height: 420,
      xaxis: { range: [0, 120], showgrid: false, zeroline: false, visible: false },
      yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
      shapes: [
        { type: "rect", x0: 0, y0: 0, x1: 120, y1: 80, line: { color: GRID, width: 1 } },
        { type: "line", x0: 60, y0: 0, x1: 60, y1: 80, line: { color: GRID, width: 1, dash: "dash" } },
        { type: "rect", x0: 102, y0: 18, x1: 120, y1: 62, line: { color: GRID, width: 1 } },
        { type: "rect", x0: 0, y0: 18, x1: 18, y1: 62, line: { color: GRID, width: 1 } },
        // Zone shading
        { type: "rect", x0: 0, y0: 0, x1: 25, y1: 80,
          fillcolor: "rgba(0,245,255,0.03)", line: { width: 0 } },
        { type: "rect", x0: 25, y0: 0, x1: 55, y1: 80,
          fillcolor: "rgba(255,255,255,0.02)", line: { width: 0 } },
        { type: "rect", x0: 55, y0: 0, x1: 80, y1: 80,
          fillcolor: "rgba(0,245,255,0.03)", line: { width: 0 } },
        { type: "rect", x0: 80, y0: 0, x1: 120, y1: 80,
          fillcolor: "rgba(239,1,7,0.03)", line: { width: 0 } },
      ]
    }, PLOTLY_CONFIG);

    // Heatmap — simulated event density using 2D histogram
    const numEvents = 400;
    const hx = [], hy = [];
    for (let i = 0; i < numEvents; i++) {
      // More events in attacking areas
      const r = Math.random();
      if (r < 0.25) { hx.push(Math.random() * 35); hy.push(Math.random() * 80); }
      else if (r < 0.55) { hx.push(35 + Math.random() * 30); hy.push(Math.random() * 80); }
      else { hx.push(65 + Math.random() * 55); hy.push(Math.random() * 80); }
    }

    Plotly.newPlot("chartHeatmap", [{
      x: hx, y: hy, type: "histogram2dcontour",
      colorscale: [["0", BG], ["0.3", "#8B0000"], ["0.6", RED], ["1", "#FFD700"]],
      contours: { coloring: "heatmap", showlabels: true },
      showscale: false, hoverinfo: "skip",
    }], {
      ...PLOTLY_LAYOUT, height: 380,
      xaxis: { range: [0, 120], showgrid: false, zeroline: false, visible: false },
      yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
    }, PLOTLY_CONFIG);

    // Pressing intensity
    const px_ = [], py_ = [];
    for (let i = 0; i < 200; i++) {
      px_.push(Math.random() * 60 + 10);
      py_.push(Math.random() * 80);
    }
    Plotly.newPlot("chartPressing", [{
      x: px_, y: py_, type: "histogram2dcontour",
      colorscale: [["0", BG], ["0.4", "#1a5276"], ["0.7", CYAN], ["1", "white"]],
      contours: { coloring: "heatmap" },
      showscale: false, hoverinfo: "skip",
    }, {
      x: px_, y: py_, type: "scatter", mode: "markers",
      marker: { size: 6, color: CYAN, opacity: 0.3 }, hoverinfo: "skip", showlegend: false,
    }], {
      ...PLOTLY_LAYOUT, height: 380,
      xaxis: { range: [0, 120], showgrid: false, zeroline: false, visible: false },
      yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
    }, PLOTLY_CONFIG);

    // Progressive passes
    const topProg = players.filter(p => p.prog_p).sort((a, b) => b.prog_p - a.prog_p).slice(0, 8);
    Plotly.newPlot("chartProgPasses", [{
      y: topProg.map(p => p.name), x: topProg.map(p => p.prog_p),
      type: "bar", orientation: "h",
      marker: { color: RED, line: { color: CYAN, width: 1 } },
      text: topProg.map(p => p.prog_p), textposition: "outside",
      textfont: { color: "white", size: 11, family: "IBM Plex Mono" },
    }], { ...PLOTLY_LAYOUT, height: 320, showlegend: false,
       xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Progressive Passes /90" },
       yaxis: { ...PLOTLY_LAYOUT.yaxis } }, PLOTLY_CONFIG);

    // Zone 14 entries
    const zoneData = m.slice(0, 10).map((r, i) => ({
      match: `M${i + 1}`,
      entries: Math.floor(Math.random() * 18 + 6),
    }));
    Plotly.newPlot("chartZone14", [{
      x: zoneData.map(d => d.match), y: zoneData.map(d => d.entries),
      type: "scatter", mode: "lines+markers",
      line: { color: CYAN, width: 3 }, marker: { size: 10, color: CYAN, line: { color: "white", width: 1 } },
      fill: "tozeroy", fillcolor: "rgba(0,245,255,0.08)",
    }], { ...PLOTLY_LAYOUT, height: 320, showlegend: false,
       xaxis: { ...PLOTLY_LAYOUT.xaxis }, yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Entries" } }, PLOTLY_CONFIG);

    // PPDA bar chart
    const ppdaData = m.slice(0, 10).map((r, i) => ({
      match: `M${i + 1}`, ppda: r.ppda,
    }));
    const ppdaColors = ppdaData.map(d => d.ppda < 11 ? "#00D4AA" : d.ppda < 13 ? "#FFB347" : "#FF4757");
    Plotly.newPlot("chartPPDA", [{
      x: ppdaData.map(d => d.match), y: ppdaData.map(d => d.ppda),
      type: "bar", marker: { color: ppdaColors },
      text: ppdaData.map(d => d.ppda.toFixed(1)), textposition: "outside",
      textfont: { color: "white", size: 11, family: "IBM Plex Mono" },
    }, {
      type: "scatter", x: ppdaData.map(d => d.match), y: ppdaData.map(() => 11),
      mode: "lines", line: { color: "#00D4AA", dash: "dash", width: 2 },
      name: "Good pressing", hoverinfo: "skip",
    }, {
      type: "scatter", x: ppdaData.map(d => d.match), y: ppdaData.map(() => 13),
      mode: "lines", line: { color: "#FF4757", dash: "dash", width: 2 },
      name: "Poor pressing", hoverinfo: "skip",
    }], { ...PLOTLY_LAYOUT, height: 320,
       xaxis: { ...PLOTLY_LAYOUT.xaxis }, yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "PPDA" } }, PLOTLY_CONFIG);
  }

  // ── 3. MATCH ANALYSIS ──
  function renderMatch(matchIdx) {
    const m = DATA.matches;
    const idx = parseInt(matchIdx) || m.length - 1;
    const match = m[idx];
    if (!match) return;

    // Match info card
    el("matchTitle").textContent = `Arsenal vs ${match.opponent}`;
    el("matchScore").textContent = `${match.gf} - ${match.ga}`;
    const badge = el("matchResultBadge");
    if (match.result === "W")
      badge.innerHTML = '<span class="badge-win">WIN</span>';
    else if (match.result === "D")
      badge.innerHTML = '<span class="badge-draw">DRAW</span>';
    else
      badge.innerHTML = '<span class="badge-loss">LOSS</span>';

    // xG Timeline — simulated shots
    const seed = idx * 137;
    let rng = seed;
    function rand() { rng = (rng * 16807) % 2147483647; return (rng - 1) / 2147483646; }

    const homeShots = [], awayShots = [];
    for (let i = 0; i < (match.gf + match.ga + 6); i++) {
      const isHome = rand() > 0.45;
      const min = Math.floor(rand() * 95);
      const xg = +(rand() * 0.35).toFixed(3);
      const goal = isHome ? (rand() > 0.85) : (rand() > 0.92);
      if (isHome) homeShots.push({ minute: min, xg: Math.min(xg + 0.05, 0.5), goal: goal && rand() > 0.3 });
      else awayShots.push({ minute: min, xg: Math.min(xg, 0.35), goal: goal });
    }
    homeShots.sort((a, b) => a.minute - b.minute);
    awayShots.sort((a, b) => a.minute - b.minute);

    const homeCum = homeShots.reduce((a, s) => { a.push((a.length ? a[a.length-1] : 0) + s.xg); return a; }, []);
    const awayCum = awayShots.reduce((a, s) => { a.push((a.length ? a[a.length-1] : 0) + s.xg); return a; }, []);

    const xgTimelineData = [
      { x: homeShots.map(s => s.minute), y: homeShots.map(s => s.xg),
        type: "bar", name: "Arsenal", marker: { color: RED, opacity: 0.8 },
        hovertemplate: "Min %{x}<br>xG: %{y:.3f}<extra></extra>" },
      { x: awayShots.map(s => s.minute), y: awayShots.map(s => s.xg),
        type: "bar", name: "Opponent", marker: { color: CYAN, opacity: 0.5 },
        hovertemplate: "Min %{x}<br>xG: %{y:.3f}<extra></extra>" },
    ];
    if (homeShots.length) {
      xgTimelineData.push({
        x: homeShots.map(s => s.minute), y: homeCum,
        type: "scatter", mode: "lines", name: "Arsenal (cum)",
        line: { color: RED, width: 2, dash: "dot" }, yaxis: "y2",
      });
    }
    if (awayShots.length) {
      xgTimelineData.push({
        x: awayShots.map(s => s.minute), y: awayCum,
        type: "scatter", mode: "lines", name: "Opponent (cum)",
        line: { color: CYAN, width: 2, dash: "dot" }, yaxis: "y2",
      });
    }

    Plotly.newPlot("chartXgTimeline", xgTimelineData, {
      ...PLOTLY_LAYOUT, height: 380, barmode: "overlay",
      xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Minute", range: [0, 96] },
      yaxis: { title: "xG", gridcolor: GRID, side: "left" },
      yaxis2: { title: "Cumulative xG", overlaying: "y", side: "right", showgrid: false },
    }, PLOTLY_CONFIG);

    // Shot map — scatter on pitch
    const shotMapData = [];
    homeShots.forEach(s => {
      shotMapData.push({
        x: [75 + Math.random() * 43], y: [8 + Math.random() * 62],
        type: "scatter", mode: "markers",
        marker: { size: Math.min(Math.max(s.xg * 120, 20), 60), color: RED,
                  line: { color: s.goal ? "#FFD700" : RED, width: 2 }, opacity: 0.7 },
        hoverinfo: "text", showlegend: false,
        text: `xG: ${s.xg.toFixed(3)}<br>Min: ${s.minute}'<br>${s.goal ? "⚽ GOAL" : "Shot"}`,
      });
    });
    awayShots.forEach(s => {
      shotMapData.push({
        x: [75 + Math.random() * 43], y: [8 + Math.random() * 62],
        type: "scatter", mode: "markers",
        marker: { size: Math.min(Math.max(s.xg * 100, 18), 50), color: CYAN,
                  line: { color: s.goal ? "#FFD700" : CYAN, width: 1.5 }, opacity: 0.5 },
        hoverinfo: "text", showlegend: false,
        text: `xG: ${s.xg.toFixed(3)}<br>Min: ${s.minute}'<br>${s.goal ? "⚽ GOAL" : "Shot"}`,
      });
    });

    Plotly.newPlot("chartShotMapMatch", shotMapData, {
      ...PLOTLY_LAYOUT, height: 380,
      xaxis: { range: [60, 120], showgrid: false, zeroline: false, visible: false },
      yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
      shapes: [
        { type: "rect", x0: 102, y0: 18, x1: 120, y1: 62,
          line: { color: GRID, width: 1 }, fillcolor: "rgba(0,0,0,0)" },
        { type: "rect", x0: 90, y0: 18, x1: 102, y1: 62,
          line: { color: GRID, width: 0.5, dash: "dash" }, fillcolor: "rgba(0,0,0,0)" },
      ],
      hovermode: "closest",
    }, PLOTLY_CONFIG);

    // Shot outcome pie
    const outcomes = ["Goal", "Saved", "Blocked", "Off Target", "Woodwork"];
    const nShots = homeShots.length + awayShots.length;
    const outCounts = [
      homeShots.filter(s => s.goal).length + awayShots.filter(s => s.goal).length,
      Math.floor(nShots * 0.32), Math.floor(nShots * 0.24),
      Math.floor(nShots * 0.24), Math.floor(nShots * 0.03),
    ];
    Plotly.newPlot("chartShotOutcome", [{
      labels: outcomes, values: outCounts,
      type: "pie", hole: 0.5,
      marker: { colors: ["#FFD700", RED, "#4A5568", "#2D3748", CYAN] },
      textinfo: "label+percent", textfont: { color: "white", size: 10 },
    }], { ...PLOTLY_LAYOUT, height: 280, showlegend: false }, PLOTLY_CONFIG);

    // Body part
    const bodyParts = ["Right Foot", "Left Foot", "Head"];
    const bodyCounts = [Math.floor(nShots * 0.58), Math.floor(nShots * 0.28), Math.floor(nShots * 0.14)];
    Plotly.newPlot("chartBodyPart", [{
      labels: bodyParts, values: bodyCounts,
      type: "pie", hole: 0.5,
      marker: { colors: [RED, CYAN, GOLD] },
      textinfo: "label+percent", textfont: { color: "white", size: 10 },
    }], { ...PLOTLY_LAYOUT, height: 280, showlegend: false }, PLOTLY_CONFIG);

    // Situation
    const sitLabels = ["Open Play", "Set Piece", "Counter", "Penalty"];
    const sitCounts = [Math.floor(nShots * 0.62), Math.floor(nShots * 0.18), Math.floor(nShots * 0.12), Math.floor(nShots * 0.04)];
    Plotly.newPlot("chartSituation", [{
      labels: sitLabels, values: sitCounts,
      type: "pie", hole: 0.5,
      marker: { colors: [RED, CYAN, "#00D4AA", "#FFB347"] },
      textinfo: "label+percent", textfont: { color: "white", size: 10 },
    }], { ...PLOTLY_LAYOUT, height: 280, showlegend: false }, PLOTLY_CONFIG);
  }

  // ── 4. PLAYER ANALYSIS ──
  function renderPlayer(playerName) {
    const players = DATA.players;
    const p = players.find(x => x.name === playerName) || players[0];
    if (!p) return;

    // Player info card
    el("playerAvatar").textContent = p.name.charAt(0);
    el("playerName").textContent = p.name;
    el("playerMeta").textContent = `${p.pos} · Age ${p.age} · #${p.num}`;
    el("playerQuickStats").innerHTML = [
      { label: "Apps", val: p.apps },
      { label: "Mins", val: p.mins },
      { label: "Goals", val: p.goals },
      { label: "Assists", val: p.assists },
      { label: "xG/90", val: p.xg_90.toFixed(2) },
      { label: "PPG", val: p.ppg || "—" },
    ].map(s => `<div class="stat-item">
      <div class="stat-value">${s.val}</div>
      <div class="stat-label">${s.label}</div>
    </div>`).join("");

    // Radar chart
    const categories = ["xG/90", "xA/90", "Prog Pass", "Prog Carry", "Touches/90", "Pass%", "Tackles/90", "Def/90"];
    const values = [p.xg_90, p.xa_90, p.prog_p / 12 * 100, p.prog_c / 8 * 100,
                    p.touches_90 / 90 * 100, p.pass_pct, p.tackles_90 / 4 * 100, p.def_90 / 8 * 100];
    // Compare with average
    const avgVals = categories.map(() => 50);

    Plotly.newPlot("chartPlayerRadar", [
      { r: values.map(v => Math.min(v * 100, 100)), theta: categories,
        fill: "toself", name: p.name,
        line: { color: RED, width: 2 },
        fillcolor: "rgba(239,1,7,0.15)" },
      { r: avgVals, theta: categories,
        fill: "toself", name: "Squad Avg",
        line: { color: CYAN, width: 2, dash: "dot" },
        fillcolor: "rgba(0,245,255,0.08)" },
    ], { ...PLOTLY_LAYOUT, height: 380,
       polar: { bgcolor: "rgba(13,17,23,0.4)",
                angularaxis: { color: TXT, gridcolor: GRID },
                radialaxis: { color: TXT, gridcolor: GRID, range: [0, 100], showticklabels: false } }
    }, PLOTLY_CONFIG);

    // Per-90 metric bars
    const metrics = [
      { label: "xG/90", val: p.xg_90 },
      { label: "xA/90", val: p.xa_90 },
      { label: "Shots/90", val: p.shots_90 },
      { label: "Key P/90", val: p.key_p_90 },
      { label: "Prog P/90", val: p.prog_p },
      { label: "Prog C/90", val: p.prog_c },
      { label: "Touches/90", val: p.touches_90 / 10 },
      { label: "Def/90", val: p.def_90 },
    ];

    Plotly.newPlot("chartPer90", [{
      x: metrics.map(m => m.label), y: metrics.map(m => m.val),
      type: "bar", marker: { color: metrics.map((_, i) => i % 2 === 0 ? RED : CYAN) },
      text: metrics.map(m => m.val.toFixed(2)), textposition: "outside",
      textfont: { color: "white", size: 10, family: "IBM Plex Mono" },
    }], { ...PLOTLY_LAYOUT, height: 320, showlegend: false,
       yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Per 90" } }, PLOTLY_CONFIG);

    // Shot map
    const shots = [];
    const nShots = Math.floor(15 + Math.random() * 25);
    for (let i = 0; i < nShots; i++) {
      const goal = Math.random() > 0.88;
      shots.push({ x: 75 + Math.random() * 43, y: 8 + Math.random() * 62,
                   xg: Math.random() * 0.4, goal });
    }
    Plotly.newPlot("chartPlayerShotMap", [{
      x: shots.map(s => s.x), y: shots.map(s => s.y),
      type: "scatter", mode: "markers",
      marker: {
        size: shots.map(s => Math.min(Math.max(s.xg * 120, 20), 55)),
        color: RED, line: { color: shots.map(s => s.goal ? "#FFD700" : RED), width: 2 },
        opacity: 0.75,
      },
      hoverinfo: "skip", showlegend: false,
    }], { ...PLOTLY_LAYOUT, height: 350,
       xaxis: { range: [60, 120], showgrid: false, zeroline: false, visible: false },
       yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
       shapes: [
         { type: "rect", x0: 102, y0: 18, x1: 120, y1: 62, line: { color: GRID, width: 1 } },
         { type: "rect", x0: 90, y0: 18, x1: 102, y1: 62, line: { color: GRID, width: 0.5, dash: "dash" } },
       ]
    }, PLOTLY_CONFIG);

    // Heatmap
    const hx = [], hy = [];
    const posBias = p.pos === "GK" ? 0 : p.pos === "DF" ? 1 : p.pos === "MID" ? 2 : 3;
    for (let i = 0; i < 300; i++) {
      const r = Math.random();
      if (posBias === 0) { hx.push(Math.random() * 25); hy.push(20 + Math.random() * 40); }
      else if (posBias === 1) { hx.push(5 + Math.random() * 50); hy.push(Math.random() * 80); }
      else if (posBias === 2) { hx.push(20 + Math.random() * 65); hy.push(Math.random() * 80); }
      else { hx.push(40 + Math.random() * 75); hy.push(10 + Math.random() * 60); }
    }
    Plotly.newPlot("chartPlayerHeatmap", [{
      x: hx, y: hy, type: "histogram2dcontour",
      colorscale: [["0", BG], ["0.4", "#5c0000"], ["0.7", RED], ["1", "#FFD700"]],
      contours: { coloring: "heatmap" }, showscale: false, hoverinfo: "skip",
    }], { ...PLOTLY_LAYOUT, height: 350,
       xaxis: { range: [0, 120], showgrid: false, zeroline: false, visible: false },
       yaxis: { range: [0, 80], showgrid: false, zeroline: false, visible: false },
    }, PLOTLY_CONFIG);

    // Performance trend (rolling 5-match)
    const weeks = Array.from({ length: 20 }, (_, i) => i + 1);
    let seed2 = p.name.length * 42;
    function rand2() { seed2 = (seed2 * 16807) % 2147483647; return (seed2 - 1) / 2147483646; }
    const trendXg = weeks.map(() => +(rand2() * 0.6 + 0.1).toFixed(2));
    const trendXa = weeks.map(() => +(rand2() * 0.4 + 0.05).toFixed(2));

    function rollingAvg(arr, w) {
      return arr.map((_, i) => {
        const start = Math.max(0, i - w + 1);
        const slice = arr.slice(start, i + 1);
        return +(slice.reduce((s, v) => s + v, 0) / slice.length).toFixed(3);
      });
    }

    Plotly.newPlot("chartPlayerTrend", [
      { x: weeks, y: rollingAvg(trendXg, 5), type: "scatter", mode: "lines+markers",
        name: "xG/90 (rolling)", line: { color: RED, width: 3 },
        marker: { size: 8, color: RED } },
      { x: weeks, y: rollingAvg(trendXa, 5), type: "scatter", mode: "lines+markers",
        name: "xA/90 (rolling)", line: { color: CYAN, width: 3 },
        marker: { size: 8, color: CYAN } },
    ], { ...PLOTLY_LAYOUT, height: 320,
       xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Gameweek" },
       yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Value /90" } }, PLOTLY_CONFIG);

    // Populate comparison selector
    const compSel = el("playerCompare");
    if (compSel) {
      const current = compSel.value;
      compSel.innerHTML = '<option value="none">vs — None</option>' +
        players.filter(x => x.name !== p.name)
          .map(x => `<option value="${x.name}">${x.name}</option>`).join("");
      if (current && players.find(x => x.name === current)) compSel.value = current;
    }
  }

  // ── 5. FPL INTELLIGENCE ──
  function renderFPL() {
    const players = DATA.players.filter(p => p.price);
    if (!players.length) return;

    const totalVal = players.reduce((s, p) => s + p.price, 0);
    const totalPts = players.reduce((s, p) => s + (p.total_pts || 0), 0);
    const avgPpg = +(players.reduce((s, p) => s + (p.ppg || 0), 0) / players.length).toFixed(1);
    const mostOwned = players.reduce((a, b) => a.owned > b.owned ? a : b);
    const topScorer = players.reduce((a, b) => (a.total_pts || 0) > (b.total_pts || 0) ? a : b);

    el("fplKPIs").innerHTML = [
      kpiCard("💰", "Total Value", "£" + totalVal.toFixed(1) + "m"),
      kpiCard("📊", "Total Points", totalPts),
      kpiCard("📈", "Avg PPG", avgPpg.toFixed(1)),
      kpiCard("👥", "Most Owned", mostOwned.name + " (" + mostOwned.owned.toFixed(1) + "%)"),
      kpiCard("🏆", "Top Scorer", topScorer.name + " (" + (topScorer.total_pts || 0) + "pts)"),
    ].join("");

    // Price vs Points scatter
    Plotly.newPlot("chartFplValue", [{
      x: players.map(p => p.price), y: players.map(p => p.total_pts || 0),
      type: "scatter", mode: "markers+text",
      text: players.map(p => p.name), textposition: "top center",
      textfont: { color: "white", size: 9 },
      marker: {
        size: players.map(p => Math.sqrt(p.owned) * 4 + 10),
        color: players.map(p => p.ppg || 3),
        colorscale: [[0, "#FF4757"], [0.5, "#FFB347"], [1, "#00D4AA"]],
        showscale: true, colorbar: { title: "PPG", tickfont: { color: TXT } },
        line: { color: "white", width: 1 },
      },
      hovertemplate: "<b>%{text}</b><br>Price: £%{x:.1f}m<br>Points: %{y}<br>Owned: %{marker.size:.1f}%<extra></extra>",
    }], { ...PLOTLY_LAYOUT, height: 380,
       xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Price (£m)" },
       yaxis: { ...PLOTLY_LAYOUT.yaxis, title: "Total Points" },
       hovermode: "closest" }, PLOTLY_CONFIG);

    // Ownership bar
    const sorted = [...players].sort((a, b) => b.owned - a.owned);
    Plotly.newPlot("chartFplOwnership", [{
      y: sorted.map(p => p.name), x: sorted.map(p => p.owned),
      type: "bar", orientation: "h",
      marker: { color: RED, line: { color: CYAN, width: 1 } },
      text: sorted.map(p => p.owned.toFixed(1) + "%"),
      textposition: "outside", textfont: { color: TXT, size: 10 },
    }], { ...PLOTLY_LAYOUT, height: 420, showlegend: false,
       xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Ownership %" } }, PLOTLY_CONFIG);

    // Predicted points (next 3 GW)
    const predData = [];
    players.forEach(p => {
      let base = p.ppg || 3;
      for (let gw = 1; gw <= 3; gw++) {
        const noise = (Math.random() - 0.5) * 2.5;
        predData.push({
          name: p.name, gw: "GW" + gw,
          pts: Math.max(0, +(base + noise + gw * 0.15).toFixed(1)),
        });
      }
    });

    const gwNames = ["GW1", "GW2", "GW3"];
    const predTop = [...players].sort((a, b) => (b.ppg || 0) - (a.ppg || 0)).slice(0, 8);
    const predTraces = gwNames.map(gw => {
      const vals = predTop.map(p => {
        const entry = predData.find(d => d.name === p.name && d.gw === gw);
        return entry ? entry.pts : 0;
      });
      return {
        y: predTop.map(p => p.name), x: vals,
        type: "bar", orientation: "h", name: gw,
        marker: { color: gw === "GW1" ? RED : gw === "GW2" ? CYAN : GOLD },
        marker_line: { color: "rgba(255,255,255,0.15)", width: 0.5 },
      };
    });

    const predTotals = predTop.map(p => {
      return gwNames.reduce((s, gw) => {
        const e = predData.find(d => d.name === p.name && d.gw === gw);
        return s + (e ? e.pts : 0);
      }, 0);
    });
    predTraces.push({
      y: predTop.map(p => p.name), x: predTotals,
      type: "scatter", mode: "markers", name: "Total",
      marker: { color: "white", size: 10, symbol: "diamond" },
    });

    Plotly.newPlot("chartFplPredicted", predTraces, {
      ...PLOTLY_LAYOUT, height: 400, barmode: "stack",
      xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Predicted Points" },
      hovermode: "y unified",
    }, PLOTLY_CONFIG);

    // Captaincy analysis
    const capCandidates = [...players].sort((a, b) => (b.form || 0) - (a.form || 0)).slice(0, 8);
    capCandidates.forEach(p => {
      p.captaincy = +((p.form || 0) * 0.4 + (p.ppg || 0) * 0.3 +
        (p.bonus || 0) * 0.15 + (p.total_pts || 0) / 100 * 0.15).toFixed(1);
    });
    const capSorted = [...capCandidates].sort((a, b) => a.captaincy - b.captaincy);

    const capColors = capSorted.map((_, i) =>
      i >= capSorted.length - 3 ? RED : CYAN
    );

    Plotly.newPlot("chartFplCaptain", [{
      y: capSorted.map(p => p.name), x: capSorted.map(p => p.captaincy),
      type: "bar", orientation: "h",
      marker: { color: capColors, line: { color: "white", width: 1 } },
      text: capSorted.map(p => p.captaincy.toFixed(1)),
      textposition: "outside", textfont: { color: "white", size: 12, family: "IBM Plex Mono" },
      hovertemplate: "<b>%{y}</b><br>Score: %{x}<br>Form: %{customdata[0]}<br>PPG: %{customdata[1]}<extra></extra>",
      customdata: capSorted.map(p => [(p.form || 0).toFixed(1), (p.ppg || 0).toFixed(1)]),
    }], { ...PLOTLY_LAYOUT, height: 380, showlegend: false,
       xaxis: { ...PLOTLY_LAYOUT.xaxis, title: "Captaincy Score" } }, PLOTLY_CONFIG);

    // Data table
    const tableHtml = `<table class="data-table">
      <thead><tr>
        <th>Player</th><th>Pos</th><th>Price</th><th>Owned</th><th>Form</th><th>PPG</th><th>Total</th><th>ICT</th>
      </tr></thead><tbody>
      ${players.sort((a, b) => (b.total_pts || 0) - (a.total_pts || 0)).map(p => `
        <tr>
          <td><strong>${p.name}</strong></td>
          <td>${p.pos}</td>
          <td>£${p.price.toFixed(1)}m</td>
          <td>${p.owned.toFixed(1)}%</td>
          <td>${(p.form || 0).toFixed(1)}</td>
          <td>${(p.ppg || 0).toFixed(1)}</td>
          <td>${p.total_pts || 0}</td>
          <td>${p.ict || 0}</td>
        </tr>
      `).join("")}
      </tbody></table>`;
    el("fplTable").innerHTML = tableHtml;

    // Populate position filter
    const posSel = el("fplPosition");
    if (posSel && posSel.options.length <= 1) {
      const positions = [...new Set(players.map(p => p.pos))];
      positions.forEach(pos => {
        const opt = document.createElement("option");
        opt.value = pos; opt.textContent = pos;
        posSel.appendChild(opt);
      });
    }
  }

  // ─── Initialize Everything ──────────────────────────────────
  function init() {
    renderOverview();
    renderTactical();

    // Match selector listener
    el("matchSelector")?.addEventListener("change", e => renderMatch(e.target.value));

    // Player selector
    const pSel = el("playerSelector");
    if (pSel) {
      DATA.players.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.name;
        opt.textContent = `${p.name} (${p.pos})`;
        pSel.appendChild(opt);
      });
      pSel.value = "Saka";
      pSel.addEventListener("change", e => renderPlayer(e.target.value));
    }

    // Player comparison
    el("playerCompare")?.addEventListener("change", () => {
      const player = el("playerSelector")?.value || "Saka";
      renderPlayer(player);
    });

    renderPlayer("Saka");
    renderMatch(DATA.matches.length - 1);
    renderFPL();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
