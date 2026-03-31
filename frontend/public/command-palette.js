/* ══════════════════════════════════════════════════════════════════════════════
   COMMAND PALETTE — Quick Actions (Cmd+K / Ctrl+K)
   SaintSal Labs Platform v2
   ══════════════════════════════════════════════════════════════════════════════ */

(function() {
  'use strict';

  var CMD_ITEMS = [
    // SEARCH & AI Verticals
    { id: 'v-search',      label: 'Search',           desc: 'AI-powered research assistant',   icon: 'Q', category: 'Verticals',    action: function(){ switchVertical('search'); }},
    { id: 'v-sports',      label: 'Sports + News',    desc: 'Live scores, breaking alerts',    icon: 'S', category: 'Verticals',    action: function(){ switchVertical('sports'); }},
    { id: 'v-news',        label: 'News',             desc: 'Breaking headlines & analysis',   icon: 'N', category: 'Verticals',    action: function(){ switchVertical('news'); }},
    { id: 'v-tech',        label: 'Technology',       desc: 'Code gen, architecture, startups',icon: 'T', category: 'Verticals',    action: function(){ switchVertical('tech'); }},
    { id: 'v-finance',     label: 'Finance',          desc: 'Market data, DCF, analysis',      icon: 'F', category: 'Verticals',    action: function(){ switchVertical('finance'); }},
    { id: 'v-realestate',  label: 'Real Estate',      desc: 'Geo, comps, cap rates',           icon: 'R', category: 'Verticals',    action: function(){ switchVertical('realestate'); }},
    { id: 'v-medical',     label: 'Healthcare',       desc: 'ICD-10, drug interactions, PubMed',icon: 'H', category: 'Verticals',   action: function(){ switchVertical('medical'); }},

    // CREATE tools
    { id: 't-builder',     label: 'Builder',          desc: '5-agent app builder pipeline',    icon: '&lt;&gt;', category: 'Create', action: function(){ navigate('studio'); }},
    { id: 't-social',      label: 'Social Studio',    desc: 'Content gen, scheduling, analytics',icon: 'X', category: 'Create',     action: function(){ navigate('social'); }},
    { id: 't-domains',     label: 'Domains & SSL',    desc: 'Domain search, DNS, certificates',icon: 'D', category: 'Create',       action: function(){ navigate('domains'); }},
    { id: 't-bizcenter',   label: 'Business Center',  desc: 'Formation, compliance, signatures',icon: 'B', category: 'Create',      action: function(){ navigate('launchpad'); }},

    // INTELLIGENCE
    { id: 't-career',      label: 'Career Suite',     desc: 'Jobs, resume, cover letter, salary',icon: 'C', category: 'Intelligence', action: function(){ navigate('career'); }},
    { id: 't-voice',       label: 'Voice AI',         desc: 'ElevenLabs voice conversations',  icon: 'V', category: 'Intelligence', action: function(){ navigate('voice'); }},
    { id: 't-bizplan',     label: 'Business Plan',    desc: 'AI-generated investor-grade plan', icon: 'P', category: 'Intelligence', action: function(){ navigate('bizplan'); }},

    // CARDS
    { id: 't-cards',       label: 'CookinCards',      desc: 'Card scan, grade, price, collection',icon: 'CC', category: 'Cards',    action: function(){ navigate('cookin-cards'); }},

    // CAREER SUITE TOOLS
    { id: 'c-coverletter', label: 'Cover Letter AI',  desc: 'Generate tailored cover letters', icon: 'CL', category: 'Career Tools', action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('coverletter'); }, 200); }},
    { id: 'c-linkedin',    label: 'LinkedIn Optimizer',desc: 'Optimize your LinkedIn profile', icon: 'Li', category: 'Career Tools', action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('linkedin'); }, 200); }},
    { id: 'c-salary',      label: 'Salary Negotiator', desc: 'Market data + negotiation scripts',icon: '$', category: 'Career Tools',action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('salary'); }, 200); }},
    { id: 'c-network',     label: 'Network Mapper',   desc: 'Find connections at any company', icon: 'NM', category: 'Career Tools', action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('network'); }, 200); }},
    { id: 'c-jobs',        label: 'Job Search',       desc: 'AI-powered job discovery',        icon: 'JS', category: 'Career Tools', action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('jobs'); }, 200); }},
    { id: 'c-resume',      label: 'Resume Builder',   desc: 'AI resume creation & optimization',icon: 'RB', category: 'Career Tools', action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('resume'); }, 200); }},
    { id: 'c-interview',   label: 'Interview Prep',   desc: 'AI mock interviews & coaching',   icon: 'IP', category: 'Career Tools', action: function(){ navigate('career'); setTimeout(function(){ if(typeof csSetTab==='function') csSetTab('interview'); }, 200); }},

    // BUSINESS TOOLS
    { id: 'b-patent',      label: 'IP / Patent Search',desc: 'Prior art & patent intelligence',icon: 'PT', category: 'Business',    action: function(){ navigate('launchpad'); setTimeout(function(){ if(typeof bcSetTab==='function') bcSetTab('patent'); }, 200); }},
    { id: 'b-formation',   label: 'Entity Formation', desc: 'LLC, Corp, EIN filing',          icon: 'EF', category: 'Business',     action: function(){ navigate('launchpad'); setTimeout(function(){ if(typeof bcSetTab==='function') bcSetTab('formation'); }, 200); }},

    // SYSTEM
    { id: 's-dashboard',   label: 'Dashboard',        desc: 'Overview & analytics',            icon: 'DA', category: 'System',       action: function(){ navigate('dashboard'); }},
    { id: 's-integrations',label: 'Integrations',     desc: 'API connectors & webhooks',       icon: 'IN', category: 'System',       action: function(){ navigate('connectors'); }},
    { id: 's-pricing',     label: 'Pricing',          desc: 'Plans & billing',                 icon: 'PR', category: 'System',       action: function(){ navigate('pricing'); }},
    { id: 's-account',     label: 'Account Settings', desc: 'Profile, API keys, preferences',  icon: 'AC', category: 'System',       action: function(){ navigate('account'); }},
    { id: 's-partners',    label: 'Partners',         desc: 'Affiliates & referral program',   icon: 'PA', category: 'System',       action: function(){ navigate('partners'); }},
    { id: 's-newchat',     label: 'New Chat',         desc: 'Start a fresh conversation',      icon: '+', category: 'Quick',         action: function(){ if(typeof startNewConversation==='function') startNewConversation(); navigate('chat'); }},
  ];

  var isOpen = false;
  var selectedIdx = 0;
  var filteredItems = CMD_ITEMS.slice();
  var overlay, searchInput, resultsList;

  // ─── Build DOM ────────────────────────────────────────────────
  function buildPalette() {
    if (document.getElementById('cmdPaletteOverlay')) return;

    overlay = document.createElement('div');
    overlay.id = 'cmdPaletteOverlay';
    overlay.setAttribute('data-testid', 'cmd-palette-overlay');
    overlay.innerHTML = [
      '<div class="cmd-palette" data-testid="cmd-palette">',
        '<div class="cmd-search-row">',
          '<span style="color:var(--t3);font-size:15px;flex-shrink:0;">&#9906;</span>',
          '<input type="text" id="cmdSearchInput" data-testid="cmd-search-input" placeholder="Type a command or search..." autocomplete="off" spellcheck="false">',
          '<kbd class="cmd-kbd">ESC</kbd>',
        '</div>',
        '<div class="cmd-results" id="cmdResults" data-testid="cmd-results"></div>',
        '<div class="cmd-footer">',
          '<span><kbd>&uarr;</kbd><kbd>&darr;</kbd> navigate</span>',
          '<span><kbd>Enter</kbd> select</span>',
          '<span><kbd>Esc</kbd> close</span>',
        '</div>',
      '</div>'
    ].join('');

    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closePalette();
    });

    document.body.appendChild(overlay);
    searchInput = document.getElementById('cmdSearchInput');
    resultsList = document.getElementById('cmdResults');

    searchInput.addEventListener('input', function() {
      filterItems(this.value);
    });

    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); selectNext(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); selectPrev(); }
      else if (e.key === 'Enter') { e.preventDefault(); executeSelected(); }
      else if (e.key === 'Escape') { closePalette(); }
    });
  }

  // ─── Filter ───────────────────────────────────────────────────
  function filterItems(query) {
    var q = query.toLowerCase().trim();
    if (!q) {
      filteredItems = CMD_ITEMS.slice();
    } else {
      filteredItems = CMD_ITEMS.filter(function(item) {
        return item.label.toLowerCase().indexOf(q) !== -1 ||
               item.desc.toLowerCase().indexOf(q) !== -1 ||
               item.category.toLowerCase().indexOf(q) !== -1;
      });
    }
    selectedIdx = 0;
    renderResults();
  }

  // ─── Render ───────────────────────────────────────────────────
  function renderResults() {
    if (!resultsList) return;
    if (filteredItems.length === 0) {
      resultsList.innerHTML = '<div class="cmd-empty">No results found</div>';
      return;
    }

    var html = '';
    var lastCat = '';
    filteredItems.forEach(function(item, i) {
      if (item.category !== lastCat) {
        lastCat = item.category;
        html += '<div class="cmd-category">' + lastCat + '</div>';
      }
      html += '<div class="cmd-item' + (i === selectedIdx ? ' cmd-item-active' : '') + '" data-idx="' + i + '" data-testid="cmd-item-' + item.id + '">';
      html += '<div class="cmd-item-icon"><span class="cmd-icon-text">' + item.icon + '</span></div>';
      html += '<div class="cmd-item-text"><div class="cmd-item-label">' + item.label + '</div><div class="cmd-item-desc">' + item.desc + '</div></div>';
      html += '</div>';
    });
    resultsList.innerHTML = html;

    // Click handlers
    resultsList.querySelectorAll('.cmd-item').forEach(function(el) {
      el.addEventListener('click', function() {
        selectedIdx = parseInt(this.getAttribute('data-idx'));
        executeSelected();
      });
      el.addEventListener('mouseenter', function() {
        selectedIdx = parseInt(this.getAttribute('data-idx'));
        updateActive();
      });
    });

    scrollToActive();
  }

  function updateActive() {
    if (!resultsList) return;
    resultsList.querySelectorAll('.cmd-item').forEach(function(el, i) {
      el.classList.toggle('cmd-item-active', parseInt(el.getAttribute('data-idx')) === selectedIdx);
    });
  }

  function scrollToActive() {
    var active = resultsList ? resultsList.querySelector('.cmd-item-active') : null;
    if (active) active.scrollIntoView({ block: 'nearest' });
  }

  function selectNext() {
    if (selectedIdx < filteredItems.length - 1) { selectedIdx++; updateActive(); scrollToActive(); }
  }

  function selectPrev() {
    if (selectedIdx > 0) { selectedIdx--; updateActive(); scrollToActive(); }
  }

  function executeSelected() {
    var item = filteredItems[selectedIdx];
    if (item && item.action) {
      closePalette();
      item.action();
    }
  }

  // ─── Open / Close ─────────────────────────────────────────────
  function openPalette() {
    buildPalette();
    isOpen = true;
    filteredItems = CMD_ITEMS.slice();
    selectedIdx = 0;
    overlay.classList.add('cmd-visible');
    searchInput.value = '';
    renderResults();
    setTimeout(function() { searchInput.focus(); }, 50);
  }

  function closePalette() {
    if (!overlay) return;
    isOpen = false;
    overlay.classList.remove('cmd-visible');
  }

  function togglePalette() {
    if (isOpen) closePalette(); else openPalette();
  }

  // ─── Global keyboard shortcut ─────────────────────────────────
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      e.stopPropagation();
      togglePalette();
    }
    if (e.key === 'Escape' && isOpen) {
      closePalette();
    }
  });

  // ─── Expose globally ──────────────────────────────────────────
  window.openCommandPalette = openPalette;
  window.closeCommandPalette = closePalette;

})();
