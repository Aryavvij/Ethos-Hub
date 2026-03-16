import streamlit as st
import streamlit.components.v1 as components

# Set page config for proper scaling
st.set_page_config(
    page_title="The Void",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Your exact HTML/CSS/JS code
void_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Void — ETHOS HUB</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #080a0f;
    --surface: #0d1117;
    --surface2: #13191f;
    --border: #1e2830;
    --accent: #00e5ff;
    --accent2: #7b2fff;
    --danger: #ff3b5c;
    --success: #00ff88;
    --warn: #ffb300;
    --text: #e8edf2;
    --muted: #5a6a78;
    --faint: #1a2330;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Space Mono', monospace;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Background grid */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  /* Glow blob */
  body::after {
    content: '';
    position: fixed;
    top: -200px;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 400px;
    background: radial-gradient(ellipse, rgba(123,47,255,0.12) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  .layout {
    position: relative;
    z-index: 1;
    max-width: 780px;
    margin: 0 auto;
    padding: 0 16px 80px;
  }

  /* HEADER */
  header {
    padding: 40px 0 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
  }

  .header-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
  }

  .brand {
    font-family: 'Syne', sans-serif;
  }

  .brand-sub {
    font-size: 11px;
    letter-spacing: 4px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  .brand-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
    color: var(--text);
    letter-spacing: -1px;
  }

  .brand-title span {
    color: var(--accent2);
  }

  .brand-tagline {
    margin-top: 8px;
    font-size: 11px;
    color: var(--muted);
    font-style: italic;
  }

  .post-btn {
    background: var(--accent2);
    color: #fff;
    border: none;
    padding: 12px 20px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    letter-spacing: 1px;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    transition: background 0.2s, transform 0.1s;
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 8px;
  }

  .post-btn:hover { background: #9b4fff; transform: translateY(-1px); }

  /* ONBOARDING SCREEN */
  .onboarding-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: var(--bg);
    z-index: 300;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }

  .onboarding-overlay.open { display: flex; }

  .onboarding-box {
    width: 100%;
    max-width: 460px;
    animation: slideUp 0.35s ease;
  }

  .onboarding-eyebrow {
    font-size: 10px;
    letter-spacing: 4px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .onboarding-title {
    font-family: 'Syne', sans-serif;
    font-size: 36px;
    font-weight: 800;
    color: var(--text);
    line-height: 1.1;
    margin-bottom: 8px;
  }

  .onboarding-title span { color: var(--accent2); }

  .onboarding-sub {
    font-size: 12px;
    color: var(--muted);
    font-style: italic;
    margin-bottom: 36px;
    line-height: 1.6;
  }

  .onboarding-field {
    margin-bottom: 20px;
  }

  .onboarding-input {
    width: 100%;
    background: var(--faint);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent2);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 14px;
    padding: 14px 16px;
    outline: none;
    transition: border-color 0.2s;
  }

  .onboarding-input:focus { border-color: var(--accent); border-top-color: var(--accent); }

  .onboarding-select {
    width: 100%;
    background: var(--faint);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent2);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    padding: 14px 16px;
    outline: none;
    cursor: pointer;
    appearance: none;
    transition: border-color 0.2s;
  }

  .onboarding-select:focus { border-color: var(--accent); border-top-color: var(--accent); }

  .onboarding-select option { background: var(--surface2); }

  .select-wrap { position: relative; }

  .select-wrap::after {
    content: '▾';
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--accent2);
    pointer-events: none;
    font-size: 14px;
  }

  .onboarding-btn {
    width: 100%;
    background: var(--accent2);
    color: #fff;
    border: none;
    padding: 16px;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 3px;
    cursor: pointer;
    text-transform: uppercase;
    transition: background 0.2s;
    margin-top: 8px;
  }

  .onboarding-btn:hover { background: #9b4fff; }

  .onboarding-note {
    margin-top: 14px;
    font-size: 10px;
    color: var(--muted);
    text-align: center;
    line-height: 1.6;
  }

  /* USER CHIP in header */
  .user-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--faint);
    border: 1px solid var(--border);
    padding: 6px 12px;
    font-size: 11px;
    color: var(--muted);
    margin-top: 12px;
  }

  .user-chip-name { color: var(--accent); font-weight: 700; }
  .user-chip-batch {
    background: var(--accent2);
    color: #fff;
    font-size: 9px;
    padding: 2px 7px;
    letter-spacing: 1px;
    font-weight: 700;
  }

  /* SCOPE TABS */
  .scope-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 20px;
    border: 1px solid var(--border);
    width: fit-content;
  }

  .scope-tab {
    background: transparent;
    border: none;
    border-right: 1px solid var(--border);
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    padding: 10px 20px;
    cursor: pointer;
    letter-spacing: 1px;
    transition: all 0.2s;
  }

  .scope-tab:last-child { border-right: none; }
  .scope-tab:hover { color: var(--text); background: var(--faint); }

  .scope-tab.active {
    background: var(--accent);
    color: var(--bg);
    font-weight: 700;
  }

  .scope-tab.active.college { background: var(--accent2); }

  /* batch badge on post */
  .batch-badge {
    font-size: 9px;
    padding: 3px 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
    background: rgba(123,47,255,0.15);
    color: var(--accent2);
    border: 1px solid rgba(123,47,255,0.3);
    font-weight: 700;
  }

  /* FILTERS */
  .filters {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 24px;
    align-items: center;
  }

  .filter-label {
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
    margin-right: 4px;
  }

  .filter-btn {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 6px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 1px;
  }

  .filter-btn:hover { border-color: var(--accent); color: var(--accent); }

  .filter-btn.active {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--bg);
    font-weight: 700;
  }

  /* COMPOSE MODAL */
  .overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.85);
    z-index: 100;
    backdrop-filter: blur(4px);
    align-items: center;
    justify-content: center;
    padding: 16px;
  }

  .overlay.open { display: flex; }

  .compose-box {
    background: var(--surface);
    border: 1px solid var(--border);
    width: 100%;
    max-width: 560px;
    padding: 32px;
    position: relative;
    animation: slideUp 0.25s ease;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .compose-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 24px;
    color: var(--accent);
  }

  .compose-close {
    position: absolute;
    top: 16px; right: 16px;
    background: none; border: none;
    color: var(--muted); font-size: 20px;
    cursor: pointer;
    transition: color 0.2s;
  }

  .compose-close:hover { color: var(--danger); }

  .field-label {
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
    display: block;
  }

  .compose-textarea {
    width: 100%;
    background: var(--faint);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    padding: 12px;
    resize: vertical;
    min-height: 100px;
    outline: none;
    transition: border-color 0.2s;
    margin-bottom: 20px;
  }

  .compose-textarea:focus { border-color: var(--accent2); }

  .tag-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 20px;
  }

  .tag-option {
    padding: 5px 12px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .tag-option:hover { border-color: var(--accent2); color: var(--accent2); }
  .tag-option.selected { background: var(--accent2); border-color: var(--accent2); color: #fff; }

  .cat-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }

  .cat-option {
    padding: 5px 12px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .cat-option:hover { border-color: var(--accent); color: var(--accent); }
  .cat-option.selected { background: var(--accent); border-color: var(--accent); color: var(--bg); }

  .anon-toggle {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    cursor: pointer;
    user-select: none;
  }

  .toggle-track {
    width: 40px; height: 22px;
    background: var(--faint);
    border: 1px solid var(--border);
    border-radius: 11px;
    position: relative;
    transition: background 0.2s;
    flex-shrink: 0;
  }

  .toggle-track.on { background: var(--accent2); border-color: var(--accent2); }

  .toggle-thumb {
    position: absolute;
    top: 3px; left: 3px;
    width: 14px; height: 14px;
    background: var(--muted);
    border-radius: 50%;
    transition: all 0.2s;
  }

  .toggle-track.on .toggle-thumb {
    left: 21px;
    background: #fff;
  }

  .toggle-label { font-size: 12px; color: var(--text); }
  .toggle-sub { font-size: 10px; color: var(--muted); margin-top: 2px; }

  .submit-btn {
    width: 100%;
    background: var(--accent2);
    color: #fff;
    border: none;
    padding: 14px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 2px;
    cursor: pointer;
    transition: background 0.2s;
    text-transform: uppercase;
  }

  .submit-btn:hover { background: #9b4fff; }

  /* POSTS */
  .posts-container { display: flex; flex-direction: column; gap: 16px; }

  .post-card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 20px;
    transition: border-color 0.2s;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .post-card:hover { border-color: #2a3a4a; }

  .post-card.flagged {
    opacity: 0.5;
    border-color: var(--danger);
    pointer-events: none;
  }

  .post-card.flagged::after {
    content: '⚑ REPORTED — PENDING MODERATION';
    display: block;
    margin-top: 12px;
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--danger);
  }

  .post-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }

  .post-author {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--accent);
  }

  .post-author.anon { color: var(--muted); font-style: italic; }

  .post-time {
    font-size: 10px;
    color: var(--muted);
    margin-left: auto;
  }

  .flair {
    font-size: 9px;
    padding: 3px 8px;
    letter-spacing: 2px;
    font-weight: 700;
    text-transform: uppercase;
    border: 1px solid;
  }

  .flair-rant { color: var(--danger); border-color: var(--danger); }
  .flair-tip { color: var(--success); border-color: var(--success); }
  .flair-question { color: var(--accent); border-color: var(--accent); }
  .flair-appreciation { color: var(--warn); border-color: var(--warn); }
  .flair-confession { color: var(--accent2); border-color: var(--accent2); }

  .cat-badge {
    font-size: 9px;
    padding: 3px 8px;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: var(--faint);
    color: var(--muted);
    border: 1px solid var(--border);
  }

  .post-body {
    font-size: 13px;
    line-height: 1.7;
    color: var(--text);
    margin-bottom: 16px;
  }

  .post-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .vote-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--faint);
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    padding: 5px 10px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .vote-btn:hover { border-color: var(--accent); color: var(--accent); }
  .vote-btn.voted-up { border-color: var(--success); color: var(--success); background: rgba(0,255,136,0.07); }
  .vote-btn.voted-down { border-color: var(--danger); color: var(--danger); background: rgba(255,59,92,0.07); }

  .action-btn {
    background: none;
    border: none;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    transition: color 0.15s;
    padding: 5px;
  }

  .action-btn:hover { color: var(--text); }
  .action-btn.reply-btn:hover { color: var(--accent); }
  .action-btn.report-btn:hover { color: var(--danger); }

  /* REPLIES */
  .replies-section {
    margin-top: 14px;
    border-top: 1px solid var(--border);
    padding-top: 14px;
    display: none;
  }

  .replies-section.open { display: block; }

  .reply-item {
    padding: 10px 0 10px 14px;
    border-left: 2px solid var(--border);
    margin-bottom: 10px;
    animation: fadeIn 0.2s ease;
  }

  .reply-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }

  .reply-author {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--accent2);
  }

  .reply-author.anon { color: var(--muted); font-style: italic; }

  .reply-time {
    font-size: 10px;
    color: var(--muted);
  }

  .reply-body { font-size: 12px; line-height: 1.6; color: #c5d0da; }

  .reply-compose {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    align-items: flex-start;
  }

  .reply-input {
    flex: 1;
    background: var(--faint);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    padding: 8px 10px;
    outline: none;
    transition: border-color 0.2s;
    resize: none;
    min-height: 36px;
  }

  .reply-input:focus { border-color: var(--accent2); }

  .reply-anon-check {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10px;
    color: var(--muted);
    margin-top: 6px;
    cursor: pointer;
  }

  .reply-anon-check input { accent-color: var(--accent2); }

  .send-reply-btn {
    background: var(--accent2);
    border: none;
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 11px;
    padding: 8px 14px;
    cursor: pointer;
    transition: background 0.2s;
    letter-spacing: 1px;
    white-space: nowrap;
  }

  .send-reply-btn:hover { background: #9b4fff; }

  /* EMPTY STATE */
  .empty-state {
    text-align: center;
    padding: 80px 20px;
    color: var(--muted);
    display: none;
  }

  .empty-state.show { display: block; }

  .empty-icon { font-size: 40px; margin-bottom: 16px; opacity: 0.4; }

  .empty-text {
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  /* NOTIFICATION */
  .notif {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--surface2);
    border: 1px solid var(--accent2);
    color: var(--text);
    padding: 12px 20px;
    font-size: 12px;
    z-index: 200;
    animation: slideIn 0.3s ease;
    display: none;
  }

  .notif.show { display: block; }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }

  /* SCROLLBAR */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); }

  @media (max-width: 480px) {
    .brand-title { font-size: 30px; }
    .compose-box { padding: 20px; }
    .post-card { padding: 14px; }
  }
</style>
</head>
<body>

<div class="onboarding-overlay" id="onboardingOverlay">
  <div class="onboarding-box">
    <div class="onboarding-eyebrow">ETHOS HUB / FIRST TIME SETUP</div>
    <div class="onboarding-title">ENTER THE <span>VOID</span></div>
    <div class="onboarding-sub">Set your identity once. Your batch determines what you see.<br>You can still post anonymously anytime.</div>
    <div class="onboarding-field">
      <label class="field-label">YOUR USERNAME</label>
      <input class="onboarding-input" type="text" id="setupUsername" placeholder="e.g. raj_eth" maxlength="24">
    </div>
    <div class="onboarding-field">
      <label class="field-label">PASSOUT YEAR</label>
      <div class="select-wrap">
        <select class="onboarding-select" id="setupBatch" onchange="previewYear()">
          <option value="" disabled selected>Select your passout year</option>
        </select>
      </div>
      <div id="yearPreview" style="margin-top:10px;font-size:11px;color:var(--accent2);min-height:16px;letter-spacing:1px;font-style:italic;"></div>
    </div>
    <button class="onboarding-btn" onclick="completeOnboarding()">INITIALIZE →</button>
    <div class="onboarding-note">Saved locally on your device. Not visible to others unless you post with your username.</div>
  </div>
</div>

<div class="layout">
  <header>
    <div class="header-top">
      <div class="brand">
        <div class="brand-sub">ETHOS HUB / COMMUNITY</div>
        <div class="brand-title">THE <span>VOID</span></div>
        <div class="brand-tagline">// speak freely. disappear completely.</div>
      </div>
      <button class="post-btn" onclick="openCompose()">+ TRANSMIT</button>
    </div>
    <div class="user-chip" id="userChip" style="display:none">
      <span>signed in as</span>
      <span class="user-chip-name" id="chipName"></span>
      <span class="user-chip-batch" id="chipBatch"></span>
    </div>
  </header>

  <div class="scope-tabs">
    <button class="scope-tab active" id="tabBatch" onclick="setScope('batch', this)">⬡ MY BATCH</button>
    <button class="scope-tab" id="tabCollege" onclick="setScope('college', this)">◎ ALL COLLEGE</button>
  </div>

  <div class="filters">
    <span class="filter-label">FILTER //</span>
    <button class="filter-btn active" data-cat="all" onclick="setFilter('all', this)">ALL</button>
    <button class="filter-btn" data-cat="academic" onclick="setFilter('academic', this)">ACADEMIC</button>
    <button class="filter-btn" data-cat="cultural" onclick="setFilter('cultural', this)">CULTURAL</button>
    <button class="filter-btn" data-cat="sports" onclick="setFilter('sports', this)">SPORTS</button>
  </div>

  <div class="posts-container" id="postsContainer"></div>
  <div class="empty-state" id="emptyState">
    <div class="empty-icon">◌</div>
    <div class="empty-text">The void is silent here</div>
  </div>
</div>

<div class="overlay" id="overlay" onclick="handleOverlayClick(event)">
  <div class="compose-box" id="composeBox">
    <button class="compose-close" onclick="closeCompose()">✕</button>
    <div class="compose-title">// TRANSMIT TO THE VOID</div>

    <label class="field-label">YOUR MESSAGE</label>
    <textarea class="compose-textarea" id="postText" placeholder="Type into the void..."></textarea>

    <label class="field-label">FLAIR</label>
    <div class="tag-row" id="flairRow">
      <button class="tag-option" data-flair="rant" onclick="selectFlair(this)">RANT</button>
      <button class="tag-option" data-flair="tip" onclick="selectFlair(this)">TIP</button>
      <button class="tag-option" data-flair="question" onclick="selectFlair(this)">QUESTION</button>
      <button class="tag-option" data-flair="appreciation" onclick="selectFlair(this)">APPRECIATION</button>
      <button class="tag-option" data-flair="confession" onclick="selectFlair(this)">CONFESSION</button>
    </div>

    <label class="field-label">CATEGORY</label>
    <div class="cat-row" id="catRow">
      <button class="cat-option" data-cat="academic" onclick="selectCat(this)">ACADEMIC</button>
      <button class="cat-option" data-cat="cultural" onclick="selectCat(this)">CULTURAL</button>
      <button class="cat-option" data-cat="sports" onclick="selectCat(this)">SPORTS</button>
    </div>

    <div class="anon-toggle" onclick="toggleAnon()">
      <div class="toggle-track" id="anonTrack">
        <div class="toggle-thumb"></div>
      </div>
      <div>
        <div class="toggle-label" id="anonLabel">Post Anonymously</div>
        <div class="toggle-sub" id="anonSub">Your name will be hidden</div>
      </div>
    </div>

    <button class="submit-btn" onclick="submitPost()">SEND INTO THE VOID</button>
  </div>
</div>

<div class="notif" id="notif"></div>

<script>
  // ---- State ----
  let CURRENT_USER = "";
  let CURRENT_BATCH = "";
  let activeFilter = "all";
  let activeScope = "batch"; // 'batch' or 'college'
  let isAnon = true;
  let selectedFlair = null;
  let selectedCat = null;

  // Seed posts with batch info
  let posts = [
    {
      id: 1, author: "anon", isAnon: true, batch: 2027,
      flair: "rant", cat: "academic",
      text: "Why does the DSA professor give internals that cover topics he hasn't even taught yet? Three chapters this sem weren't covered in class but appeared in the test. This is actually insane.",
      time: "2h ago", ups: 24, downs: 3, userVote: null, flagged: false,
      replies: [
        { author: "anon", isAnon: true, batch: 2027, text: "Same thing happened in our section. The syllabus and what's taught are two different universes.", time: "1h ago" },
        { author: "raj_eth", isAnon: false, batch: 2027, text: "Talk to the CR, they can escalate it to HOD.", time: "45m ago" }
      ], repliesOpen: false
    },
    {
      id: 2, author: "priya_codes", isAnon: false, batch: 2027,
      flair: "tip", cat: "academic",
      text: "For anyone preparing for semester exams — the last 3 years' question papers follow a very predictable pattern. Check The Repository, I uploaded a compiled PDF with pattern analysis.",
      time: "5h ago", ups: 41, downs: 1, userVote: null, flagged: false,
      replies: [], repliesOpen: false
    },
    {
      id: 3, author: "anon", isAnon: true, batch: 2028,
      flair: "confession", cat: "cultural",
      text: "I practiced for the cultural fest dance event for 3 weeks and then chickened out on registration day. Now I'm watching from the crowd. Never again.",
      time: "1d ago", ups: 18, downs: 0, userVote: null, flagged: false,
      replies: [
        { author: "anon", isAnon: true, batch: 2028, text: "Next time just submit before your brain catches up. You've got this.", time: "20h ago" }
      ], repliesOpen: false
    },
    {
      id: 4, author: "cricket_nerd", isAnon: false, batch: 2026,
      flair: "question", cat: "sports",
      text: "Is the inter-department cricket tournament still happening this month? I heard it got postponed but can't find any official update anywhere.",
      time: "3h ago", ups: 7, downs: 0, userVote: null, flagged: false,
      replies: [], repliesOpen: false
    },
    {
      id: 5, author: "anon", isAnon: true, batch: 2029,
      flair: "tip", cat: "cultural",
      text: "Heads up to freshers — the annual cultural fest registrations open next Monday. Last year they closed in 6 hours so set a reminder.",
      time: "4h ago", ups: 33, downs: 0, userVote: null, flagged: false,
      replies: [], repliesOpen: false
    }
  ];

  // ---- Helpers ----
  const CURRENT_YEAR = new Date().getFullYear();

  function getActiveBatches() {
    // Always the 4 current passout years: this year + next 3
    return [CURRENT_YEAR, CURRENT_YEAR+1, CURRENT_YEAR+2, CURRENT_YEAR+3];
  }

  function calcCollegeYear(passoutYear) {
    const yr = 4 - (passoutYear - CURRENT_YEAR);
    if (yr < 1 || yr > 4) return null;
    const suffix = ['st','nd','rd','th'][yr-1];
    return yr + suffix + ' Year';
  }

  function populatePassoutDropdown() {
    const sel = document.getElementById('setupBatch');
    getActiveBatches().forEach(yr => {
      const opt = document.createElement('option');
      opt.value = yr;
      opt.textContent = 'Class of ' + yr;
      sel.appendChild(opt);
    });
  }

  function previewYear() {
    const passout = parseInt(document.getElementById('setupBatch').value);
    const preview = document.getElementById('yearPreview');
    const yr = calcCollegeYear(passout);
    preview.textContent = yr ? '→ You are currently in ' + yr : '';
  }

  // ---- Onboarding ----
  function initApp() {
    populatePassoutDropdown();
    const savedUser = localStorage.getItem('void_username');
    const savedBatch = localStorage.getItem('void_batch');

    if (savedUser && savedBatch) {
      CURRENT_USER = savedUser;
      CURRENT_BATCH = parseInt(savedBatch);
      showUserChip();
      render();
    } else {
      document.getElementById('onboardingOverlay').classList.add('open');
    }
  }

  function completeOnboarding() {
    const username = document.getElementById('setupUsername').value.trim();
    const batch = document.getElementById('setupBatch').value;

    if (!username) { showNotif('Enter a username to continue.'); return; }
    if (!batch) { showNotif('Select your passout year.'); return; }

    localStorage.setItem('void_username', username);
    localStorage.setItem('void_batch', batch);
    CURRENT_USER = username;
    CURRENT_BATCH = parseInt(batch);

    document.getElementById('onboardingOverlay').classList.remove('open');
    showUserChip();
    render();
    showNotif('Welcome to The Void, ' + username);
  }

  function showUserChip() {
    const yr = calcCollegeYear(CURRENT_BATCH);
    document.getElementById('chipName').textContent = CURRENT_USER;
    document.getElementById('chipBatch').textContent = 'CLASS OF ' + CURRENT_BATCH + (yr ? ' · ' + yr : '');
    document.getElementById('userChip').style.display = 'flex';
  }

  // ---- Scope ----
  function setScope(scope, btn) {
    activeScope = scope;
    document.querySelectorAll('.scope-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    render();
  }

  // ---- Render ----
  function render() {
    const container = document.getElementById('postsContainer');
    const emptyState = document.getElementById('emptyState');

    let filtered = posts.filter(p => {
      const catMatch = activeFilter === 'all' || p.cat === activeFilter;
      const scopeMatch = activeScope === 'college' || p.batch === CURRENT_BATCH;
      return catMatch && scopeMatch;
    });

    container.innerHTML = '';

    if (filtered.length === 0) {
      emptyState.classList.add('show');
      return;
    }
    emptyState.classList.remove('show');

    filtered.forEach(post => {
      const card = document.createElement('div');
      card.className = 'post-card' + (post.flagged ? ' flagged' : '');
      card.id = 'post-' + post.id;

      const authorHtml = post.isAnon
        ? `<span class="post-author anon">// anonymous</span>`
        : `<span class="post-author">${post.author}</span>`;

      const batchBadge = activeScope === 'college'
        ? `<span class="batch-badge">CLASS OF ${post.batch}</span>`
        : '';

      const repliesHtml = post.replies.map(r => `
        <div class="reply-item">
          <div class="reply-meta">
            ${r.isAnon ? `<span class="reply-author anon">// anon</span>` : `<span class="reply-author">${r.author}</span>`}
            ${activeScope === 'college' ? `<span class="batch-badge" style="font-size:8px;padding:2px 5px">CLASS OF ${r.batch||''}</span>` : ''}
            <span class="reply-time">${r.time}</span>
          </div>
          <div class="reply-body">${r.text}</div>
        </div>
      `).join('');

      const replyCount = post.replies.length;
      const replyLabel = replyCount > 0 ? `REPLIES (${replyCount})` : 'REPLY';

      card.innerHTML = `
        <div class="post-header">
          ${authorHtml}
          ${batchBadge}
          <span class="flair flair-${post.flair}">${post.flair}</span>
          <span class="cat-badge">${post.cat}</span>
          <span class="post-time">${post.time}</span>
        </div>
        <div class="post-body">${post.text}</div>
        <div class="post-actions">
          <button class="vote-btn ${post.userVote === 'up' ? 'voted-up' : ''}" onclick="vote(${post.id}, 'up')">👍 ${post.ups}</button>
          <button class="vote-btn ${post.userVote === 'down' ? 'voted-down' : ''}" onclick="vote(${post.id}, 'down')">👎 ${post.downs}</button>
          <button class="action-btn reply-btn" onclick="toggleReplies(${post.id})">${replyLabel}</button>
          ${!post.flagged ? `<button class="action-btn report-btn" onclick="reportPost(${post.id})">⚑ REPORT</button>` : ''}
        </div>
        <div class="replies-section ${post.repliesOpen ? 'open' : ''}" id="replies-${post.id}">
          ${repliesHtml}
          <div class="reply-compose">
            <textarea class="reply-input" id="replyInput-${post.id}" placeholder="Add to the void..." rows="1" oninput="autoResize(this)"></textarea>
            <button class="send-reply-btn" onclick="sendReply(${post.id})">SEND</button>
          </div>
          <label class="reply-anon-check">
            <input type="checkbox" id="replyAnon-${post.id}" checked>
            Post as anonymous
          </label>
        </div>
      `;
      container.appendChild(card);
    });
  }

  // ---- Vote ----
  function vote(id, dir) {
    const post = posts.find(p => p.id === id);
    if (!post) return;
    if (post.userVote === dir) {
      if (dir === 'up') post.ups--; else post.downs--;
      post.userVote = null;
    } else {
      if (post.userVote === 'up') post.ups--;
      if (post.userVote === 'down') post.downs--;
      if (dir === 'up') post.ups++; else post.downs++;
      post.userVote = dir;
    }
    render();
  }

  // ---- Replies ----
  function toggleReplies(id) {
    const post = posts.find(p => p.id === id);
    post.repliesOpen = !post.repliesOpen;
    render();
  }

  function sendReply(id) {
    const input = document.getElementById('replyInput-' + id);
    const anonCheck = document.getElementById('replyAnon-' + id);
    const text = input.value.trim();
    if (!text) return;
    const post = posts.find(p => p.id === id);
    const isAnonReply = anonCheck.checked;
    post.replies.push({
      author: isAnonReply ? 'anon' : CURRENT_USER,
      isAnon: isAnonReply,
      batch: CURRENT_BATCH,
      text, time: 'just now'
    });
    post.repliesOpen = true;
    render();
    showNotif('Reply transmitted.');
  }

  function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }

  // ---- Report ----
  function reportPost(id) {
    posts.find(p => p.id === id).flagged = true;
    render();
    showNotif('Post reported. Pending moderation review.');
  }

  // ---- Filter ----
  function setFilter(cat, btn) {
    activeFilter = cat;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    render();
  }

  // ---- Compose ----
  function openCompose() {
    document.getElementById('overlay').classList.add('open');
    document.getElementById('postText').focus();
  }

  function closeCompose() {
    document.getElementById('overlay').classList.remove('open');
  }

  function handleOverlayClick(e) {
    if (e.target === document.getElementById('overlay')) closeCompose();
  }

  function selectFlair(btn) {
    document.querySelectorAll('.tag-option').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedFlair = btn.dataset.flair;
  }

  function selectCat(btn) {
    document.querySelectorAll('.cat-option').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedCat = btn.dataset.cat;
  }

  function toggleAnon() {
    isAnon = !isAnon;
    document.getElementById('anonTrack').classList.toggle('on', isAnon);
    document.getElementById('anonLabel').textContent = isAnon ? 'Post Anonymously' : 'Post as ' + CURRENT_USER;
    document.getElementById('anonSub').textContent = isAnon ? 'Your name will be hidden' : 'Your username will be visible';
  }

  function submitPost() {
    const text = document.getElementById('postText').value.trim();
    if (!text) { showNotif('Write something first.'); return; }
    if (!selectedFlair) { showNotif('Select a flair tag.'); return; }
    if (!selectedCat) { showNotif('Select a category.'); return; }

    posts.unshift({
      id: Date.now(),
      author: isAnon ? 'anon' : CURRENT_USER,
      isAnon, batch: CURRENT_BATCH,
      flair: selectedFlair, cat: selectedCat,
      text, time: 'just now',
      ups: 0, downs: 0, userVote: null, flagged: false,
      replies: [], repliesOpen: false
    });

    closeCompose();
    document.getElementById('postText').value = '';
    document.querySelectorAll('.tag-option, .cat-option').forEach(b => b.classList.remove('selected'));
    selectedFlair = null; selectedCat = null;
    render();
    showNotif('Transmitted into the void.');
  }

  function showNotif(msg) {
    const el = document.getElementById('notif');
    el.textContent = msg;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 2800);
  }

  // ---- Init ----
  document.getElementById('anonTrack').classList.add('on');
  initApp();
</script>
</body>
</html>
"""

# Render the component
components.html(void_html_content, height=1200, scrolling=True)
