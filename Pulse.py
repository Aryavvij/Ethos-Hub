import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration (Authority Hub)
st.set_page_config(
    page_title="The Pulse",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. The Full Pulse Source Code
# Features: Onboarding, Ticker, Categorized Feed, and Verified Roles
pulse_html_source = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Pulse — ETHOS HUB</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f5f0e8;
    --surface: #ffffff;
    --surface2: #ede8df;
    --border: #d9d2c5;
    --text: #1a1510;
    --muted: #8a7f70;
    --faint: #ede8df;
    --cultural: #e8420a;
    --sports: #0066ff;
    --academic: #00913f;
    --campus: #8800cc;
    --general: #cc7700;
    --pin: #e8420a;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Grain texture */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
  }

  .layout {
    position: relative;
    z-index: 1;
    max-width: 820px;
    margin: 0 auto;
    padding: 0 20px 100px;
  }

  header { padding: 48px 0 0; }
  .header-inner {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    padding-bottom: 20px;
    border-bottom: 3px solid var(--text);
  }

  .brand-eyebrow { font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--muted); }
  .brand-title { font-family: 'Bebas Neue', sans-serif; font-size: 72px; line-height: 0.9; color: var(--text); }
  .brand-title span { color: var(--cultural); }

  .post-btn {
    background: var(--text); color: var(--bg); border: none; padding: 14px 24px;
    font-family: 'Bebas Neue', sans-serif; font-size: 18px; letter-spacing: 2px;
    cursor: pointer; transition: all 0.2s;
  }
  .post-btn:hover { background: var(--cultural); transform: translateY(-2px); }

  .user-chip { display: flex; align-items: center; gap: 8px; font-size: 11px; color: var(--muted); justify-content: flex-end; margin-top: 10px; }
  .chip-name { font-weight: 700; color: var(--text); }
  .chip-batch { background: var(--text); color: var(--bg); font-size: 9px; padding: 3px 8px; }
  .chip-role { background: var(--cultural); color: #fff; font-size: 9px; padding: 3px 8px; }

  /* TICKER */
  .ticker-bar { background: var(--text); color: var(--bg); overflow: hidden; padding: 8px 0; font-family: 'Bebas Neue', sans-serif; font-size: 14px; margin-bottom: 28px; }
  .ticker-inner { display: flex; gap: 60px; animation: ticker 28s linear infinite; white-space: nowrap; }
  @keyframes ticker { from { transform: translateX(0); } to { transform: translateX(-50%); } }
  .ticker-dot { color: var(--cultural); margin-right: 12px; }

  /* FILTERS */
  .controls { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
  .filter-row { display: flex; border: 2px solid var(--text); overflow: hidden; }
  .filter-btn { background: transparent; border: none; border-right: 1px solid var(--border); padding: 8px 14px; font-size: 11px; cursor: pointer; }
  .filter-btn.active { background: var(--text); color: var(--bg); }

  /* POSTS */
  .posts-grid { display: flex; flex-direction: column; gap: 2px; }
  .post-card { background: var(--surface); border-left: 4px solid var(--border); padding: 20px; position: relative; transition: all 0.15s; }
  .post-card:hover { transform: translateX(4px); }
  .post-card.type-cultural { border-left-color: var(--cultural); }
  .post-card.type-sports { border-left-color: var(--sports); }
  .post-card.type-academic { border-left-color: var(--academic); }

  .post-title { font-family: 'Bebas Neue', sans-serif; font-size: 22px; margin-bottom: 6px; }
  .post-body { font-size: 13px; line-height: 1.7; color: #4a4035; margin-bottom: 14px; }
  .event-date { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; background: var(--faint); padding: 4px 10px; }

  /* ONBOARDING & OVERLAYS */
  .onboarding-overlay, .overlay { display: none; position: fixed; inset: 0; background: var(--bg); z-index: 300; align-items: center; justify-content: center; padding: 24px; }
  .onboarding-overlay.open, .overlay.open { display: flex; }
  .onboarding-box, .compose-box { width: 100%; max-width: 480px; background: var(--surface); border: 2px solid var(--text); padding: 32px; }
  .ob-title, .compose-title { font-family: 'Bebas Neue', sans-serif; font-size: 52px; line-height: 0.95; margin-bottom: 10px; }
  
  .ob-input, .compose-input, .ob-select { width: 100%; border: 2px solid var(--text); padding: 12px; font-family: 'DM Sans', sans-serif; margin-bottom: 18px; }
  .ob-btn, .submit-btn { width: 100%; background: var(--text); color: var(--bg); border: none; padding: 16px; font-family: 'Bebas Neue', sans-serif; font-size: 22px; cursor: pointer; }

  .notif { position: fixed; bottom: 24px; right: 24px; background: var(--text); color: var(--bg); padding: 12px 20px; font-size: 13px; z-index: 400; display: none; }
  .notif.show { display: block; }
</style>
</head>
<body>

<div class="onboarding-overlay" id="onboardingOverlay">
  <div class="onboarding-box">
    <div class="ob-title">WHO ARE <span>YOU?</span></div>
    <input class="ob-input" type="text" id="setupUsername" placeholder="USERNAME" maxlength="24">
    <select class="ob-select" id="setupBatch"><option value="" disabled selected>PASSOUT YEAR</option></select>
    <select class="ob-select" id="setupRole">
        <option value="">REGULAR STUDENT</option>
        <option value="Class Representative">Class Representative</option>
        <option value="Cultural Secretary">Cultural Secretary</option>
        <option value="Student Council President">President</option>
    </select>
    <button class="ob-btn" onclick="completeOnboarding()">JOIN THE PULSE</button>
  </div>
</div>

<div class="layout">
  <header>
    <div class="header-inner">
      <div class="brand">
        <div class="brand-eyebrow">ETHOS HUB / CAMPUS FEED</div>
        <div class="brand-title">THE <span>PULSE</span></div>
      </div>
      <div class="header-right">
        <button class="post-btn" onclick="openCompose()">+ POST</button>
      </div>
    </div>
    <div class="user-chip" id="userChip" style="display:none">
        <span class="chip-name" id="chipName"></span>
        <span class="chip-batch" id="chipBatch"></span>
        <span class="chip-role" id="chipRole" style="display:none"></span>
    </div>
  </header>

  <div class="ticker-bar"><div class="ticker-inner" id="tickerInner"></div></div>

  <div class="controls">
    <div class="filter-row">
      <button class="filter-btn active" onclick="setFilter('all', this)">ALL</button>
      <button class="filter-btn" onclick="setFilter('cultural', this)">CULTURAL</button>
      <button class="filter-btn" onclick="setFilter('sports', this)">SPORTS</button>
      <button class="filter-btn" onclick="setFilter('academic', this)">ACADEMIC</button>
    </div>
  </div>

  <div class="posts-grid" id="postsGrid"></div>
</div>

<div class="overlay" id="overlay">
  <div class="compose-box">
    <div class="compose-title">NEW <span>POST</span></div>
    <input class="compose-input" type="text" id="postTitle" placeholder="TITLE">
    <textarea class="ob-input" id="postBody" placeholder="DETAILS" style="height:100px"></textarea>
    <select class="ob-select" id="postType">
        <option value="cultural">CULTURAL</option>
        <option value="sports">SPORTS</option>
        <option value="academic">ACADEMIC</option>
    </select>
    <button class="submit-btn" onclick="submitPost()">PUBLISH</button>
    <button class="ob-btn" onclick="closeCompose()" style="background:none; color:var(--text); font-size:14px;">CANCEL</button>
  </div>
</div>

<div class="notif" id="notif"></div>

<script>
  let CURRENT_USER = '';
  let CURRENT_BATCH = '';
  let CURRENT_ROLE = '';
  let posts = [
    { id: 1, type: 'cultural', author: 'Admin', batch: 2026, role: 'Secretary', title: 'FEST 2025 REGISTRATIONS', body: 'Live now on portal.', postedAt: new Date(), ups: 10, downs: 0 }
  ];

  function initApp() {
    const sel = document.getElementById('setupBatch');
    [2025, 2026, 2027, 2028].forEach(yr => {
      const opt = document.createElement('option'); opt.value = yr; opt.textContent = 'Class of ' + yr; sel.appendChild(opt);
    });

    const u = localStorage.getItem('pulse_user');
    if (u) { 
      CURRENT_USER = u; 
      CURRENT_BATCH = localStorage.getItem('pulse_batch');
      CURRENT_ROLE = localStorage.getItem('pulse_role');
      showChip(); render(); 
    } else { document.getElementById('onboardingOverlay').classList.add('open'); }
  }

  function completeOnboarding() {
    CURRENT_USER = document.getElementById('setupUsername').value;
    CURRENT_BATCH = document.getElementById('setupBatch').value;
    CURRENT_ROLE = document.getElementById('setupRole').value;
    localStorage.setItem('pulse_user', CURRENT_USER);
    localStorage.setItem('pulse_batch', CURRENT_BATCH);
    localStorage.setItem('pulse_role', CURRENT_ROLE);
    document.getElementById('onboardingOverlay').classList.remove('open');
    showChip(); render();
  }

  function showChip() {
    document.getElementById('chipName').textContent = CURRENT_USER;
    document.getElementById('chipBatch').textContent = 'CLASS OF ' + CURRENT_BATCH;
    if(CURRENT_ROLE) { document.getElementById('chipRole').textContent = CURRENT_ROLE; document.getElementById('chipRole').style.display='block'; }
    document.getElementById('userChip').style.display = 'flex';
  }

  function render() {
    const grid = document.getElementById('postsGrid');
    grid.innerHTML = '';
    posts.forEach(p => {
      const card = document.createElement('div');
      card.className = 'post-card type-' + p.type;
      card.innerHTML = `<div class="post-title">${p.title}</div><div class="post-body">${p.body}</div><div style="font-size:10px; color:var(--muted)">BY ${p.author} | ${p.role}</div>`;
      grid.appendChild(card);
    });
    document.getElementById('tickerInner').innerHTML = posts.map(p => `<span class="ticker-dot">●</span> ${p.title}`).join(' ');
  }

  function openCompose() { document.getElementById('overlay').classList.add('open'); }
  function closeCompose() { document.getElementById('overlay').classList.remove('open'); }
  function submitPost() {
    posts.unshift({
        id: Date.now(),
        type: document.getElementById('postType').value,
        author: CURRENT_USER, batch: CURRENT_BATCH, role: CURRENT_ROLE,
        title: document.getElementById('postTitle').value,
        body: document.getElementById('postBody').value,
        postedAt: new Date(), ups: 0, downs: 0
    });
    closeCompose(); render();
  }

  initApp();
</script>
</body>
</html>
"""

# 3. Component Rendering
components.html(pulse_html_source, height=1500, scrolling=True)