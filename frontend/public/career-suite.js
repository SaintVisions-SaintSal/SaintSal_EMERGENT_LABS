/* ═══════════════════════════════════════════════════════════════════════════════
   SaintSal™ Labs — Career Suite v1.0
   Full-spectrum career platform: Job Search, Resume, Digital Cards,
   AI Coach, Job Tracker, Backgrounds, Interview Prep, Email Signatures
   Replaces WarRoom — v7.30.0
   ═══════════════════════════════════════════════════════════════════════════════ */

var csState = {
  activeTab: 'overview',
  // Job Search
  jobQuery: '',
  jobLocation: '',
  jobRemote: false,
  jobResults: [],
  jobLoading: false,
  // Resume
  resumeData: { full_name: '', email: '', phone: '', location: '', title: '', summary: '', experience: '', education: '', skills: '', linkedin: '', website: '' },
  resumeEnhanced: null,
  resumeLoading: false,
  resumeId: null,
  resumeSaving: false,
  dnaLoaded: false,
  headshotUrl: '',
  backgroundUrl: '',
  // Digital Cards
  cardData: { name: '', title: '', company: '', email: '', phone: '', website: '', linkedin: '', tagline: '', accent_color: '#D4A843', avatar_b64: '', banner_b64: '', instagram: '', twitter: '', facebook: '', tiktok: '', github: '', address: '' },
  cardPreview: null,
  cardLoading: false,
  // Email Signatures
  sigData: { name: '', title: '', company: '', email: '', phone: '', website: '', linkedin: '', accent_color: '#D4A843', banner_color: '#0D0F14', avatar_b64: '', template: 'executive', show_photo: true, headline: '', instagram: '', twitter: '' },
  sigPreview: null,
  sigLoading: false,
  // AI Coach
  coachMessages: [],
  coachLoading: false,
  // Interview Prep
  prepCompany: '',
  prepRole: '',
  prepType: 'behavioral',
  prepResult: null,
  prepLoading: false,
  // Company Intel
  intelCompany: '',
  intelResult: null,
  intelLoading: false,
  // Job Tracker
  trackerJobs: { saved: [], applied: [], phone_screen: [], interview_scheduled: [], interview_completed: [], offer_received: [], job_won: [], rejected: [] },
  trackerLoading: false,
  // Backgrounds
  bgTemplates: [],
  bgLoading: false,
  // Cover Letter
  clSavedId: null
};

var CS_API = window.API_BASE || '';

/* ── Init ── */
function initCareerSuite() {
  renderCareerSuite();
}

/* ── Main Render ── */
function renderCareerSuite() {
  var el = document.getElementById('careerSuiteRoot');
  if (!el) return;
  var html = '';
  html += '<div style="padding:20px 16px 100px;max-width:900px;margin:0 auto;">';
  html += '<h1 style="font-size:24px;font-weight:700;color:var(--text-primary);margin-bottom:4px;">Career Suite</h1>';
  html += '<p style="color:var(--text-muted);font-size:13px;margin-bottom:20px;">Your full-spectrum career command center — search, apply, prepare, and dominate.</p>';

  /* ── Tab Navigation ── */
  html += '<div style="display:flex;gap:4px;margin-bottom:24px;overflow-x:auto;padding-bottom:4px;-webkit-overflow-scrolling:touch;">';
  var tabs = [
    { id: 'overview', label: 'Overview', icon: '🎯' },
    { id: 'jobs', label: 'Job Search', icon: '🔍' },
    { id: 'tracker', label: 'Tracker', icon: '📋' },
    { id: 'resume', label: 'Resume', icon: '📄' },
    { id: 'coverletter', label: 'Cover Letter', icon: '📝' },
    { id: 'linkedin', label: 'LinkedIn', icon: '💼' },
    { id: 'salary', label: 'Salary', icon: '💰' },
    { id: 'network', label: 'Network', icon: '🌐' },
    { id: 'cards', label: 'Cards', icon: '💳' },
    { id: 'signature', label: 'Signatures', icon: '✉️' },
    { id: 'coach', label: 'AI Coach', icon: '🧠' },
    { id: 'interview', label: 'Interview', icon: '🎤' },
    { id: 'backgrounds', label: 'Backgrounds', icon: '🖼️' }
  ];
  tabs.forEach(function(t) {
    var active = csState.activeTab === t.id;
    html += '<button onclick="csSwitchTab(\'' + t.id + '\')" '
         + 'style="flex-shrink:0;padding:8px 14px;border-radius:8px;border:none;cursor:pointer;font-size:12px;font-weight:' + (active ? '600' : '500') + ';'
         + 'background:' + (active ? 'var(--accent-gold,#D4A843)' : 'var(--surface-raised,#1a1a1a)') + ';'
         + 'color:' + (active ? '#000' : 'var(--text-secondary,#aaa)') + ';transition:all 0.2s;">'
         + t.icon + ' ' + t.label + '</button>';
  });
  html += '</div>';

  /* ── Tab Content ── */
  html += '<div id="csTabContent">';
  html += csRenderTab(csState.activeTab);
  html += '</div>';
  html += '</div>';
  el.innerHTML = html;
}

function csSwitchTab(tab) {
  csState.activeTab = tab;
  renderCareerSuite();
  // Auto-load data for certain tabs
  if (tab === 'tracker') csLoadTracker();
  if (tab === 'backgrounds') csLoadBackgrounds();
  if (tab === 'resume' && !csState.dnaLoaded) csAutofillFromDNA();
}

function csRenderTab(tab) {
  switch(tab) {
    case 'overview': return csOverview();
    case 'jobs': return csJobSearch();
    case 'tracker': return csTracker();
    case 'resume': return csResume();
    case 'coverletter': return csCoverLetter();
    case 'linkedin': return csLinkedInOptimizer();
    case 'salary': return csSalaryNegotiator();
    case 'network': return csNetworkMapper();
    case 'cards': return csCards();
    case 'signature': return csSignature();
    case 'coach': return csCoach();
    case 'interview': return csInterview();
    case 'backgrounds': return csBackgrounds();
    default: return csOverview();
  }
}


/* ══════════════════════════════════════════════════════════════════════════════
   OVERVIEW TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csOverview() {
  var cards = [
    { id: 'jobs', icon: '🔍', title: 'Job Search', desc: 'AI-powered job search across LinkedIn, Indeed, Glassdoor & more. Semantic matching finds roles you never knew existed.', action: 'Search Jobs' },
    { id: 'tracker', icon: '📋', title: 'Job Tracker', desc: 'Kanban board to track every application — from wishlist to offer. Never lose track of an opportunity.', action: 'Open Tracker' },
    { id: 'resume', icon: '📄', title: 'Resume Builder', desc: 'AI-enhanced resumes written at Goldman Sachs / McKinsey caliber. ATS-optimized with killer bullet points.', action: 'Build Resume' },
    { id: 'cards', icon: '💳', title: 'Digital Cards', desc: 'Executive digital business cards with QR codes and vCard download. Network like a pro.', action: 'Create Card' },
    { id: 'signature', icon: '✉️', title: 'Email Signatures', desc: 'Professional HTML email signatures that make every email a brand impression.', action: 'Design Signature' },
    { id: 'coach', icon: '🧠', title: 'AI Career Coach', desc: 'Your personal career strategist — salary negotiation, career path, offer evaluation, and more.', action: 'Chat with Coach' },
    { id: 'interview', icon: '🎤', title: 'Interview Prep', desc: 'Company intel, STAR examples, likely questions, salary ranges, and negotiation scripts. Walk in prepared.', action: 'Prepare Now' },
    { id: 'backgrounds', icon: '🖼️', title: 'Video Backgrounds', desc: 'Professional video call backgrounds — executive office to tech startup. Look the part on every call.', action: 'Browse' }
  ];

  var html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;">';
  cards.forEach(function(c) {
    html += '<div style="background:var(--surface-raised,#141414);border-radius:12px;padding:20px;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;" '
         + 'onmouseenter="this.style.transform=\'translateY(-2px)\';this.style.boxShadow=\'0 8px 24px rgba(0,0,0,0.3)\'" '
         + 'onmouseleave="this.style.transform=\'none\';this.style.boxShadow=\'none\'" '
         + 'onclick="csSwitchTab(\'' + c.id + '\')">'
         + '<div style="font-size:28px;margin-bottom:10px;">' + c.icon + '</div>'
         + '<div style="font-size:15px;font-weight:600;color:var(--text-primary);margin-bottom:6px;">' + c.title + '</div>'
         + '<div style="font-size:12px;color:var(--text-muted);line-height:1.5;margin-bottom:14px;">' + c.desc + '</div>'
         + '<div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);">' + c.action + ' →</div>'
         + '</div>';
  });
  html += '</div>';
  return html;
}


/* ══════════════════════════════════════════════════════════════════════════════
   JOB SEARCH TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csJobSearch() {
  var html = '';
  html += '<div style="margin-bottom:20px;">';
  html += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">';
  html += '<input id="csJobQuery" placeholder="Job title, skill, or keyword..." value="' + _esc(csState.jobQuery) + '" '
       + 'style="flex:1;min-width:200px;padding:10px 14px;border-radius:8px;border:1px solid var(--border-subtle,#333);background:var(--surface-raised,#1a1a1a);color:var(--text-primary);font-size:13px;" '
       + 'onkeydown="if(event.key===\'Enter\')csSearchJobs()">';
  html += '<input id="csJobLocation" placeholder="Location (optional)" value="' + _esc(csState.jobLocation) + '" '
       + 'style="width:160px;padding:10px 14px;border-radius:8px;border:1px solid var(--border-subtle,#333);background:var(--surface-raised,#1a1a1a);color:var(--text-primary);font-size:13px;">';
  html += '<label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer;padding:0 8px;">'
       + '<input type="checkbox" id="csJobRemote" ' + (csState.jobRemote ? 'checked' : '') + ' onchange="csState.jobRemote=this.checked" style="accent-color:var(--accent-gold,#D4A843);"> Remote</label>';
  html += '<button onclick="csSearchJobs()" style="padding:10px 20px;border-radius:8px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:13px;cursor:pointer;">Search</button>';
  html += '</div></div>';

  if (csState.jobLoading) {
    html += csLoadingSpinner('Searching jobs...');
  } else if (csState.jobResults.length > 0) {
    html += '<div style="font-size:12px;color:var(--text-muted);margin-bottom:12px;">' + csState.jobResults.length + ' results found</div>';
    csState.jobResults.forEach(function(job, idx) {
      html += '<div style="background:var(--surface-raised,#141414);border-radius:10px;padding:16px;margin-bottom:8px;">';
      html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">';
      html += '<div style="flex:1;">';
      html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:3px;">' + _esc(job.title) + '</div>';
      html += '<div style="font-size:12px;color:var(--accent-gold,#D4A843);margin-bottom:3px;">' + _esc(job.company) + '</div>';
      html += '<div style="font-size:11px;color:var(--text-muted);">' + _esc(job.location) + (job.remote ? ' · Remote' : '') + (job.source ? ' · ' + _esc(job.source) : '') + '</div>';
      if (job.snippet) {
        html += '<div style="font-size:11px;color:var(--text-secondary);margin-top:8px;line-height:1.5;">' + _esc(job.snippet) + '</div>';
      }
      html += '</div>';
      html += '<div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0;">';
      if (job.url) {
        html += '<a href="' + _esc(job.url) + '" target="_blank" rel="noopener" style="padding:6px 12px;border-radius:6px;background:var(--accent-gold,#D4A843);color:#000;font-size:11px;font-weight:600;text-decoration:none;text-align:center;">Apply</a>';
      }
      html += '<button onclick="csTrackJob(' + idx + ')" style="padding:6px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:none;color:var(--text-secondary);font-size:11px;cursor:pointer;">Track</button>';
      html += '</div></div></div>';
    });
  } else {
    html += '<div style="text-align:center;padding:40px 20px;color:var(--text-muted);">';
    html += '<div style="font-size:36px;margin-bottom:12px;">🔍</div>';
    html += '<div style="font-size:14px;margin-bottom:4px;">Search for your next opportunity</div>';
    html += '<div style="font-size:12px;">AI-powered search across LinkedIn, Indeed, Glassdoor, and more</div>';
    html += '</div>';
  }
  return html;
}

async function csSearchJobs() {
  var q = document.getElementById('csJobQuery');
  var loc = document.getElementById('csJobLocation');
  if (!q || !q.value.trim()) return;
  csState.jobQuery = q.value.trim();
  csState.jobLocation = loc ? loc.value.trim() : '';
  csState.jobLoading = true;
  csState.jobResults = [];
  renderCareerSuite();
  try {
    var params = 'query=' + encodeURIComponent(csState.jobQuery);
    if (csState.jobLocation) params += '&location=' + encodeURIComponent(csState.jobLocation);
    if (csState.jobRemote) params += '&remote=true';
    var r = await fetch(CS_API + '/api/career/jobs/search?' + params);
    var data = await r.json();
    csState.jobResults = data.jobs || [];
  } catch (e) {
    console.error('[Career] Job search error:', e);
    csState.jobResults = [];
  }
  csState.jobLoading = false;
  renderCareerSuite();
}

function csTrackJob(idx) {
  var job = csState.jobResults[idx];
  if (!job) return;
  fetch(CS_API + '/api/career/v2/tracker', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_title: job.title, company_name: job.company, job_url: job.url || '', status: 'saved', notes: job.snippet || '', job_source: job.source || 'search', job_description: job.snippet || '' })
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (d.success) {
      csShowToast('Added to tracker — check the Tracker tab');
    }
  }).catch(function(e) { console.error(e); });
}


/* ══════════════════════════════════════════════════════════════════════════════
   JOB TRACKER TAB (Kanban)
   ══════════════════════════════════════════════════════════════════════════════ */
function csTracker() {
  var html = '';
  if (csState.trackerLoading) return csLoadingSpinner('Loading tracker...');

  var columns = [
    { id: 'saved', label: 'Saved', color: '#888', icon: 'fa-bookmark' },
    { id: 'applied', label: 'Applied', color: '#4F8EF7', icon: 'fa-paper-plane' },
    { id: 'phone_screen', label: 'Phone Screen', color: '#D4A843', icon: 'fa-phone' },
    { id: 'interview_scheduled', label: 'Interview', color: '#9b59b6', icon: 'fa-calendar-check' },
    { id: 'interview_completed', label: 'Completed', color: '#1abc9c', icon: 'fa-check-circle' },
    { id: 'offer_received', label: 'Offer', color: '#2ecc71', icon: 'fa-handshake' },
    { id: 'job_won', label: 'Won!', color: '#00FF88', icon: 'fa-trophy' },
    { id: 'rejected', label: 'Rejected', color: '#e74c3c', icon: 'fa-times-circle' }
  ];

  html += '<div data-testid="career-tracker-kanban" style="display:flex;gap:6px;overflow-x:auto;padding-bottom:8px;-webkit-overflow-scrolling:touch;">';
  columns.forEach(function(col) {
    var jobs = csState.trackerJobs[col.id] || [];
    html += '<div style="min-width:150px;flex:1;background:var(--surface-raised,#111);border-radius:10px;padding:10px;">';
    html += '<div style="font-size:11px;font-weight:600;color:' + col.color + ';margin-bottom:8px;display:flex;align-items:center;gap:5px;">'
         + '<i class="fas ' + col.icon + '" style="font-size:10px;"></i> '
         + col.label + ' <span style="color:var(--text-muted);font-weight:400;">(' + jobs.length + ')</span></div>';
    if (jobs.length === 0) {
      html += '<div style="font-size:10px;color:var(--text-muted);padding:12px 0;text-align:center;">—</div>';
    }
    jobs.forEach(function(job) {
      html += '<div data-testid="tracker-job-card" style="background:var(--surface-base,#0a0a0a);border-radius:8px;padding:8px;margin-bottom:5px;border-left:3px solid ' + col.color + ';">';
      html += '<div style="font-size:11px;font-weight:600;color:var(--text-primary);margin-bottom:2px;">' + _esc(job.job_title || '') + '</div>';
      html += '<div style="font-size:10px;color:var(--accent-gold,#D4A843);margin-bottom:4px;">' + _esc(job.company_name || job.company || '') + '</div>';
      html += '<div style="display:flex;gap:3px;flex-wrap:wrap;">';
      // Show move buttons for adjacent stages only
      var ci = columns.findIndex(function(c) { return c.id === col.id; });
      if (ci > 0) {
        var prev = columns[ci - 1];
        html += '<button data-testid="move-job-' + prev.id + '" onclick="csUpdateJobStatus(\'' + (job.job_id || job.id) + '\',\'' + prev.id + '\',\'' + _esc(job.company_name || job.company || '') + '\',\'' + _esc(job.job_title || '') + '\')" '
             + 'style="padding:2px 6px;border-radius:3px;border:1px solid ' + prev.color + '44;background:none;color:' + prev.color + ';font-size:8px;cursor:pointer;">'
             + '<i class="fas fa-arrow-left"></i></button>';
      }
      if (ci < columns.length - 1) {
        var next = columns[ci + 1];
        html += '<button data-testid="move-job-' + next.id + '" onclick="csUpdateJobStatus(\'' + (job.job_id || job.id) + '\',\'' + next.id + '\',\'' + _esc(job.company_name || job.company || '') + '\',\'' + _esc(job.job_title || '') + '\')" '
             + 'style="padding:2px 6px;border-radius:3px;border:1px solid ' + next.color + '44;background:none;color:' + next.color + ';font-size:8px;cursor:pointer;">'
             + next.label + ' <i class="fas fa-arrow-right"></i></button>';
      }
      html += '<button onclick="csDeleteJob(\'' + (job.job_id || job.id) + '\')" '
           + 'style="padding:2px 6px;border-radius:3px;border:1px solid #e74c3c44;background:none;color:#e74c3c;font-size:8px;cursor:pointer;margin-left:auto;">'
           + '<i class="fas fa-trash"></i></button>';
      html += '</div></div>';
    });
    html += '</div>';
  });
  html += '</div>';

  // Stage coaching display area
  html += '<div id="csStageCoachingArea"></div>';

  // Quick add form
  html += '<div style="margin-top:12px;background:var(--surface-raised,#141414);border-radius:10px;padding:14px;">';
  html += '<div style="font-size:12px;font-weight:600;color:var(--text-primary);margin-bottom:8px;"><i class="fas fa-plus-circle" style="color:var(--accent-gold);"></i> Quick Add</div>';
  html += '<div style="display:flex;gap:6px;flex-wrap:wrap;">';
  html += '<input data-testid="tracker-add-title" id="csTrackTitle" placeholder="Job title" style="flex:1;min-width:130px;padding:8px 10px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;">';
  html += '<input data-testid="tracker-add-company" id="csTrackCompany" placeholder="Company" style="flex:1;min-width:110px;padding:8px 10px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;">';
  html += '<input id="csTrackUrl" placeholder="URL (optional)" style="flex:1;min-width:110px;padding:8px 10px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;">';
  html += '<button data-testid="tracker-add-btn" onclick="csQuickAdd()" style="padding:8px 16px;border-radius:6px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:12px;cursor:pointer;">Add</button>';
  html += '</div></div>';

  return html;
}

function csLoadTracker() {
  csState.trackerLoading = true;
  renderCareerSuite();
  fetch(CS_API + '/api/career/v2/tracker').then(function(r) { return r.json(); }).then(function(data) {
    csState.trackerJobs = data.kanban || { saved: [], applied: [], phone_screen: [], interview_scheduled: [], interview_completed: [], offer_received: [], job_won: [], rejected: [] };
    csState.trackerLoading = false;
    renderCareerSuite();
  }).catch(function() { csState.trackerLoading = false; renderCareerSuite(); });
}

function csUpdateJobStatus(jobId, status, company, title) {
  fetch(CS_API + '/api/career/v2/tracker/' + jobId, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: status, company_name: company || '', job_title: title || '' })
  }).then(function(r) { return r.json(); }).then(function(data) {
    csLoadTracker();
    // Show stage coaching popup
    if (data.coaching) {
      csShowStageCoaching(data.coaching, data.interview_prep);
    }
  }).catch(function() { csLoadTracker(); });
}

function csShowStageCoaching(coaching, interviewPrep) {
  var area = document.getElementById('csStageCoachingArea');
  if (!area) return;
  var h = '<div data-testid="stage-coaching-popup" style="background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.25);border-radius:12px;padding:16px;margin-top:12px;animation:fadeIn 0.3s ease;">';
  h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">';
  h += '<div style="font-size:12px;font-weight:700;color:var(--accent-gold,#D4A843);"><i class="fas fa-lightbulb"></i> SAL Coaching — ' + _esc(coaching.title || coaching.stage) + '</div>';
  h += '<button onclick="document.getElementById(\'csStageCoachingArea\').innerHTML=\'\'" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:14px;"><i class="fas fa-times"></i></button>';
  h += '</div>';
  if (coaching.tips && coaching.tips.length) {
    coaching.tips.forEach(function(tip) {
      h += '<div style="font-size:11px;color:var(--text-secondary);padding:4px 0;padding-left:16px;position:relative;line-height:1.5;">';
      h += '<i class="fas fa-check" style="color:#2ecc71;position:absolute;left:0;top:6px;font-size:9px;"></i> ' + _esc(tip);
      h += '</div>';
    });
  }
  // Interview prep pack
  if (interviewPrep) {
    h += '<div style="margin-top:14px;padding-top:12px;border-top:1px solid rgba(212,175,55,0.15);">';
    h += '<div style="font-size:12px;font-weight:700;color:#9b59b6;margin-bottom:8px;"><i class="fas fa-graduation-cap"></i> Auto-Generated Interview Prep</div>';
    if (interviewPrep.prep_checklist) {
      h += '<div style="font-size:10px;font-weight:600;color:var(--text-muted);margin-bottom:4px;">PREP CHECKLIST</div>';
      interviewPrep.prep_checklist.forEach(function(item) {
        h += '<div style="font-size:11px;color:var(--text-secondary);padding:2px 0;padding-left:16px;position:relative;">';
        h += '<input type="checkbox" style="position:absolute;left:0;top:3px;accent-color:#D4A843;"> ' + _esc(item) + '</div>';
      });
    }
    if (interviewPrep.common_questions) {
      h += '<div style="font-size:10px;font-weight:600;color:var(--text-muted);margin-top:10px;margin-bottom:4px;">COMMON QUESTIONS</div>';
      interviewPrep.common_questions.forEach(function(q, i) {
        h += '<div style="font-size:11px;color:var(--text-secondary);padding:3px 0;">' + (i+1) + '. ' + _esc(q) + '</div>';
      });
    }
    if (interviewPrep.company_specific_questions) {
      h += '<div style="font-size:10px;font-weight:600;color:#9b59b6;margin-top:10px;margin-bottom:4px;">COMPANY-SPECIFIC (AI-GENERATED)</div>';
      interviewPrep.company_specific_questions.forEach(function(q, i) {
        h += '<div style="font-size:11px;color:var(--text-secondary);padding:3px 0;"><i class="fas fa-brain" style="color:#9b59b6;font-size:9px;"></i> ' + _esc(q) + '</div>';
      });
    }
    if (interviewPrep.power_tips) {
      h += '<div style="font-size:10px;font-weight:600;color:#D4A843;margin-top:10px;margin-bottom:4px;">POWER TIPS</div>';
      interviewPrep.power_tips.forEach(function(tip) {
        h += '<div style="font-size:11px;color:var(--accent-gold);padding:2px 0;"><i class="fas fa-bolt" style="font-size:9px;"></i> ' + _esc(tip) + '</div>';
      });
    }
    h += '</div>';
  }
  h += '</div>';
  area.innerHTML = h;
}

function csQuickAdd() {
  var t = document.getElementById('csTrackTitle');
  var c = document.getElementById('csTrackCompany');
  var u = document.getElementById('csTrackUrl');
  if (!t || !t.value.trim()) return;
  fetch(CS_API + '/api/career/v2/tracker', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_title: t.value.trim(), company_name: c ? c.value.trim() : '', job_url: u ? u.value.trim() : '', status: 'saved' })
  }).then(function() { if(t) t.value=''; if(c) c.value=''; if(u) u.value=''; csLoadTracker(); });
}

function csDeleteJob(jobId) {
  fetch(CS_API + '/api/career/v2/tracker/' + jobId, { method: 'DELETE' }).then(function() { csLoadTracker(); });
}

function csGetStageGuidance(status, company, role) {
  var el = document.getElementById('csCoachGuidance');
  if (el) el.innerHTML = '<div style="text-align:center;padding:20px;"><i class="fas fa-spinner fa-spin" style="color:#D4AF37;"></i> SAL is preparing your guidance...</div>';
  fetch(CS_API + '/api/career/v2/coach/stage-guidance', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: status, company: company, role: role })
  }).then(function(r) { return r.json(); }).then(function(data) {
    if (data.coaching && el) {
      var c = data.coaching;
      var html = '<div style="background:rgba(212,175,55,0.05);border:1px solid rgba(212,175,55,0.2);border-radius:10px;padding:16px;margin-top:12px;">';
      html += '<div style="font-size:11px;color:#D4AF37;font-weight:700;letter-spacing:1px;margin-bottom:8px;">SAL GUIDANCE — ' + status.toUpperCase() + '</div>';
      if (c.guidance) html += '<div style="font-size:12px;color:#ccc;line-height:1.6;margin-bottom:12px;">' + _esc(c.guidance).replace(/\n/g,'<br>') + '</div>';
      if (c.action_items && c.action_items.length) {
        html += '<div style="font-size:10px;color:#D4AF37;font-weight:600;margin-bottom:4px;">ACTION ITEMS</div>';
        c.action_items.forEach(function(a) { html += '<div style="font-size:11px;color:#aaa;padding:3px 0;">• ' + _esc(typeof a === 'string' ? a : a.action || JSON.stringify(a)) + '</div>'; });
      }
      if (c.motivation) html += '<div style="font-size:12px;color:#D4AF37;font-style:italic;margin-top:10px;">"' + _esc(c.motivation) + '"</div>';
      html += '</div>';
      el.innerHTML = html;
    }
  }).catch(function(e) { if(el) el.innerHTML = '<div style="color:#ef4444;font-size:12px;">Error: ' + e.message + '</div>'; });
}


/* ══════════════════════════════════════════════════════════════════════════════
   RESUME BUILDER TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csResume() {
  var d = csState.resumeData;
  var html = '';
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">';

  // Left: Form
  html += '<div style="background:var(--surface-raised,#141414);border-radius:10px;padding:16px;">';
  html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">';
  html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);">Your Information</div>';
  if (!csState.dnaLoaded) {
    html += '<button data-testid="resume-dna-autofill-btn" onclick="csAutofillFromDNA()" style="padding:5px 12px;border-radius:6px;border:1px solid var(--accent-gold,#D4A843);background:none;color:var(--accent-gold,#D4A843);font-size:11px;cursor:pointer;font-weight:600;">Autofill from DNA</button>';
  } else {
    html += '<span style="font-size:10px;color:var(--accent-gold,#D4A843);font-weight:600;">DNA loaded</span>';
  }
  html += '</div>';

  var fields = [
    { key: 'full_name', label: 'Full Name', ph: 'John Doe' },
    { key: 'title', label: 'Job Title', ph: 'Senior Software Engineer' },
    { key: 'email', label: 'Email', ph: 'john@example.com' },
    { key: 'phone', label: 'Phone', ph: '+1 (555) 123-4567' },
    { key: 'location', label: 'Location', ph: 'San Francisco, CA' },
    { key: 'linkedin', label: 'LinkedIn URL', ph: 'linkedin.com/in/johndoe' },
    { key: 'website', label: 'Website', ph: 'johndoe.dev' }
  ];
  fields.forEach(function(f) {
    html += '<div style="margin-bottom:10px;">';
    html += '<label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">' + f.label + '</label>';
    html += '<input data-testid="resume-' + f.key + '" id="csRes_' + f.key + '" value="' + _esc(d[f.key] || '') + '" placeholder="' + f.ph + '" '
         + 'oninput="csState.resumeData[\'' + f.key + '\']=this.value" '
         + 'style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;box-sizing:border-box;">';
    html += '</div>';
  });

  // Headshot & Background upload
  html += '<div style="display:flex;gap:10px;margin-bottom:10px;">';
  html += '<div style="flex:1;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Headshot Photo</label>';
  html += '<label data-testid="resume-headshot-upload" style="display:block;padding:8px;border-radius:6px;border:1px dashed rgba(255,255,255,.15);text-align:center;cursor:pointer;font-size:11px;color:var(--text-muted);">' + (csState.headshotUrl ? '<i class="fas fa-check" style="color:#2ecc71;"></i> Uploaded' : '<i class="fas fa-camera"></i> Upload') + '<input type="file" accept="image/*" onchange="csUploadCareerFile(this,\'headshot\')" style="display:none;"></label></div>';
  html += '<div style="flex:1;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Background Image</label>';
  html += '<label data-testid="resume-background-upload" style="display:block;padding:8px;border-radius:6px;border:1px dashed rgba(255,255,255,.15);text-align:center;cursor:pointer;font-size:11px;color:var(--text-muted);">' + (csState.backgroundUrl ? '<i class="fas fa-check" style="color:#2ecc71;"></i> Uploaded' : '<i class="fas fa-image"></i> Upload') + '<input type="file" accept="image/*" onchange="csUploadCareerFile(this,\'background\')" style="display:none;"></label></div>';
  html += '</div>';

  // Textarea fields
  html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Professional Summary</label>';
  html += '<textarea id="csRes_summary" placeholder="Brief summary of your experience..." oninput="csState.resumeData.summary=this.value" '
       + 'style="width:100%;height:60px;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;resize:vertical;box-sizing:border-box;">' + _esc(d.summary || '') + '</textarea></div>';

  html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Experience (one role per line: Company | Title | Dates | Bullets)</label>';
  html += '<textarea id="csRes_experience" placeholder="Acme Corp | Senior Dev | 2020-Present | Led team of 8..." oninput="csState.resumeData.experience=this.value" '
       + 'style="width:100%;height:80px;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;resize:vertical;box-sizing:border-box;">' + _esc(d.experience || '') + '</textarea></div>';

  html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Education</label>';
  html += '<textarea id="csRes_education" placeholder="Stanford University | B.S. Computer Science | 2016" oninput="csState.resumeData.education=this.value" '
       + 'style="width:100%;height:50px;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;resize:vertical;box-sizing:border-box;">' + _esc(d.education || '') + '</textarea></div>';

  html += '<div style="margin-bottom:14px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Skills (comma-separated)</label>';
  html += '<input id="csRes_skills" value="' + _esc(d.skills || '') + '" placeholder="Python, React, Leadership, AWS..." oninput="csState.resumeData.skills=this.value" '
       + 'style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;box-sizing:border-box;"></div>';

  // Action buttons row
  html += '<div style="display:flex;gap:8px;flex-wrap:wrap;">';
  html += '<button data-testid="resume-save-enhance-btn" onclick="csSaveAndEnhanceResume()" ' + (csState.resumeLoading || csState.resumeSaving ? 'disabled' : '') + ' '
       + 'style="flex:1;min-width:140px;padding:10px;border-radius:8px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:13px;cursor:pointer;">'
       + (csState.resumeSaving ? 'Saving...' : csState.resumeLoading ? 'Enhancing...' : 'Save & AI Enhance') + '</button>';
  if (csState.resumeId) {
    html += '<button data-testid="resume-download-pdf-btn" onclick="csExportResume(\'pdf\')" '
         + 'style="padding:10px 14px;border-radius:8px;border:1px solid var(--accent-gold,#D4A843);background:none;color:var(--accent-gold,#D4A843);font-weight:600;font-size:12px;cursor:pointer;"><i class="fas fa-file-pdf"></i> PDF</button>';
    html += '<button data-testid="resume-download-docx-btn" onclick="csExportResume(\'docx\')" '
         + 'style="padding:10px 14px;border-radius:8px;border:1px solid var(--accent-gold,#D4A843);background:none;color:var(--accent-gold,#D4A843);font-weight:600;font-size:12px;cursor:pointer;"><i class="fas fa-file-word"></i> DOCX</button>';
  }
  html += '</div>';
  html += '</div>';

  // Right: AI Enhanced Preview
  html += '<div style="background:var(--surface-raised,#141414);border-radius:10px;padding:16px;">';
  html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:14px;">AI Enhanced Preview</div>';
  if (csState.resumeEnhanced) {
    var e = csState.resumeEnhanced;
    if (e.enhanced_summary) {
      html += '<div style="margin-bottom:14px;"><div style="font-size:11px;color:var(--accent-gold,#D4A843);font-weight:600;margin-bottom:4px;">ENHANCED SUMMARY</div>';
      html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.6;">' + _esc(e.enhanced_summary) + '</div></div>';
    }
    if (e.ats_score) {
      html += '<div style="margin-bottom:14px;display:flex;align-items:center;gap:10px;">';
      html += '<div style="font-size:11px;color:var(--accent-gold,#D4A843);font-weight:600;">ATS SCORE</div>';
      html += '<div style="background:rgba(212,168,67,0.15);border-radius:20px;padding:4px 14px;font-size:16px;font-weight:700;color:var(--accent-gold,#D4A843);">' + e.ats_score + '/100</div></div>';
    }
    if (e.ats_keywords && e.ats_keywords.length) {
      html += '<div style="margin-bottom:14px;"><div style="font-size:11px;color:var(--accent-gold,#D4A843);font-weight:600;margin-bottom:6px;">ATS KEYWORDS</div>';
      html += '<div style="display:flex;flex-wrap:wrap;gap:4px;">';
      (e.ats_keywords || e.keywords_added || []).forEach(function(kw) {
        html += '<span style="padding:3px 8px;border-radius:4px;background:var(--accent-gold,#D4A843)22;color:var(--accent-gold,#D4A843);font-size:10px;">' + _esc(kw) + '</span>';
      });
      html += '</div></div>';
    }
    if (e.skills_categorized) {
      html += '<div style="margin-bottom:14px;"><div style="font-size:11px;color:var(--accent-gold,#D4A843);font-weight:600;margin-bottom:6px;">CATEGORIZED SKILLS</div>';
      Object.keys(e.skills_categorized).forEach(function(cat) {
        var skills = e.skills_categorized[cat];
        if (skills && skills.length) {
          html += '<div style="margin-bottom:6px;"><span style="font-size:10px;font-weight:600;color:var(--text-secondary);">' + _esc(cat) + ':</span> ';
          html += '<span style="font-size:11px;color:var(--text-muted);">' + skills.map(_esc).join(', ') + '</span></div>';
        }
      });
      html += '</div>';
    }
    if (e.cover_letter_opener) {
      html += '<div style="margin-bottom:14px;"><div style="font-size:11px;color:var(--accent-gold,#D4A843);font-weight:600;margin-bottom:4px;">COVER LETTER OPENER</div>';
      html += '<div style="font-size:12px;color:var(--text-secondary);line-height:1.6;font-style:italic;">"' + _esc(e.cover_letter_opener) + '"</div></div>';
    }
    // Export buttons in preview panel too
    if (csState.resumeId) {
      html += '<div style="display:flex;gap:8px;margin-top:16px;padding-top:14px;border-top:1px solid var(--border-subtle,#222);">';
      html += '<button data-testid="resume-preview-pdf-btn" onclick="csExportResume(\'pdf\')" style="flex:1;padding:10px;border-radius:8px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:12px;cursor:pointer;"><i class="fas fa-file-pdf"></i> Download PDF</button>';
      html += '<button data-testid="resume-preview-docx-btn" onclick="csExportResume(\'docx\')" style="flex:1;padding:10px;border-radius:8px;border:1px solid var(--accent-gold,#D4A843);background:none;color:var(--accent-gold,#D4A843);font-weight:600;font-size:12px;cursor:pointer;"><i class="fas fa-file-word"></i> Download DOCX</button>';
      html += '</div>';
    }
  } else {
    html += '<div style="text-align:center;padding:40px 20px;color:var(--text-muted);">';
    html += '<div style="font-size:28px;margin-bottom:10px;"><i class="fas fa-magic" style="color:var(--accent-gold,#D4A843);"></i></div>';
    html += '<div style="font-size:13px;">Fill out your info and click "Save & AI Enhance" to get Goldman Sachs-level resume content</div>';
    html += '</div>';
  }
  html += '</div>';
  html += '</div>';
  return html;
}

async function csSaveAndEnhanceResume() {
  var d = csState.resumeData;
  if (!d.full_name || !d.title) { csShowToast('Enter at least name and title'); return; }

  // Step 1: Save to Supabase
  csState.resumeSaving = true;
  renderCareerSuite();

  var expArr = (d.experience || '').split('\n').filter(Boolean).map(function(line) {
    var parts = line.split('|').map(function(s) { return s.trim(); });
    return { company: parts[0] || '', title: parts[1] || '', dates: parts[2] || '', description: parts[3] || '', achievements: (parts[3] || '').split(';').map(function(s){return s.trim();}).filter(Boolean) };
  });
  var eduArr = (d.education || '').split('\n').filter(Boolean).map(function(line) {
    var parts = line.split('|').map(function(s) { return s.trim(); });
    return { school: parts[0] || '', degree: parts[1] || '', year: parts[2] || '' };
  });

  var savePayload = {
    full_name: d.full_name, email: d.email, phone: d.phone, location: d.location,
    linkedin_url: d.linkedin, website: d.website, name: d.full_name + ' Resume',
    summary: d.summary, skills: (d.skills || '').split(',').map(function(s){return s.trim();}).filter(Boolean),
    work_experience: expArr, education: eduArr,
    headshot_url: csState.headshotUrl || '', background_image_url: csState.backgroundUrl || ''
  };

  try {
    if (csState.resumeId) {
      // Update existing
      await fetch(CS_API + '/api/career/v2/resumes/' + csState.resumeId, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: savePayload.name, summary_text: savePayload.summary,
          contact_info: JSON.stringify({ full_name: d.full_name, email: d.email, phone: d.phone, location: d.location, linkedin: d.linkedin, website: d.website }),
          skills_section: JSON.stringify(savePayload.skills), education_section: JSON.stringify(eduArr),
          raw_content: JSON.stringify(expArr), background_image_url: csState.backgroundUrl || '' })
      });
    } else {
      // Create new
      var r = await fetch(CS_API + '/api/career/v2/resumes', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(savePayload)
      });
      var data = await r.json();
      if (data.resume_id) csState.resumeId = data.resume_id;
    }
    csShowToast('Resume saved');
  } catch(e) { console.error('[Career] Save error:', e); csShowToast('Save failed'); }

  csState.resumeSaving = false;

  // Step 2: Enhance via AI
  if (!csState.resumeId) { renderCareerSuite(); return; }
  csState.resumeLoading = true;
  csState.resumeEnhanced = null;
  renderCareerSuite();

  try {
    var r2 = await fetch(CS_API + '/api/career/v2/resumes/' + csState.resumeId + '/enhance', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_role: d.title })
    });
    var data2 = await r2.json();
    if (data2.enhanced) csState.resumeEnhanced = data2.enhanced;
    csShowToast('Resume enhanced by SAL');
  } catch(e) { console.error('[Career] Enhance error:', e); csShowToast('Enhancement failed — resume still saved'); }

  csState.resumeLoading = false;
  renderCareerSuite();
}

function csExportResume(fmt) {
  if (!csState.resumeId) { csShowToast('Save resume first'); return; }
  var url = CS_API + '/api/career/v2/resumes/' + csState.resumeId + '/export/' + fmt;
  window.open(url, '_blank');
  csShowToast('Downloading ' + fmt.toUpperCase() + '...');
}

async function csAutofillFromDNA() {
  try {
    // Try to get DNA from localStorage first
    var dna = null;
    try { dna = JSON.parse(localStorage.getItem('businessDNA') || 'null'); } catch(e) {}
    if (!dna) {
      // Fetch from backend
      var r = await fetch(CS_API + '/api/user/dna');
      if (r.ok) dna = await r.json();
    }
    if (dna && (dna.first_name || dna.email || dna.business_name)) {
      // Autofill resume fields
      if (!csState.resumeData.full_name && (dna.first_name || dna.last_name)) {
        csState.resumeData.full_name = ((dna.first_name || '') + ' ' + (dna.last_name || '')).trim();
      }
      if (!csState.resumeData.email && dna.email) csState.resumeData.email = dna.email;
      if (!csState.resumeData.phone && dna.phone) csState.resumeData.phone = dna.phone;
      if (!csState.resumeData.title && dna.tagline) csState.resumeData.title = dna.tagline;
      if (!csState.resumeData.summary && dna.bio) csState.resumeData.summary = dna.bio;
      if (!csState.resumeData.location && (dna.business_city || dna.business_state)) {
        csState.resumeData.location = ((dna.business_city || '') + ', ' + (dna.business_state || '')).replace(/^, |, $/g, '');
      }
      if (!csState.resumeData.website && dna.website) csState.resumeData.website = dna.website;
      csState.dnaLoaded = true;
      csShowToast('Autofilled from Business DNA');

      // Also push to Supabase career profile
      fetch(CS_API + '/api/career/v2/profile/autofill-dna', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dna: dna })
      }).catch(function() {});

      renderCareerSuite();
    }
  } catch(e) { console.error('[Career] DNA autofill error:', e); }
}

async function csUploadCareerFile(input, type) {
  var file = input.files[0];
  if (!file) return;
  var formData = new FormData();
  formData.append('file', file);
  try {
    var r = await fetch(CS_API + '/api/career/v2/upload/' + type, { method: 'POST', body: formData });
    var data = await r.json();
    if (data.url) {
      // URL is now a full Supabase Storage public URL
      if (type === 'headshot') csState.headshotUrl = data.url;
      else csState.backgroundUrl = data.url;
      csShowToast(type.charAt(0).toUpperCase() + type.slice(1) + ' uploaded');
      renderCareerSuite();
    } else {
      csShowToast('Upload failed: ' + (data.error || 'Unknown error'));
    }
  } catch(e) { console.error('[Career] Upload error:', e); csShowToast('Upload failed'); }
}


/* ══════════════════════════════════════════════════════════════════════════════
   DIGITAL CARDS TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csCards() {
  var d = csState.cardData;
  var html = '';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">';

  // ── LEFT: Form ──
  html += '<div style="background:var(--surface-raised,#141414);border-radius:12px;padding:20px;overflow-y:auto;max-height:calc(100vh - 220px);">';
  html += '<div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:16px;">Business Card Details</div>';

  // Core fields
  var fields = [
    { key: 'name', label: 'Full Name', ph: 'Ryan Capatosto' },
    { key: 'title', label: 'Title', ph: 'CEO' },
    { key: 'company', label: 'Company', ph: 'Saint Vision Technologies' },
    { key: 'email', label: 'Email', ph: 'ryan@cookin.io' },
    { key: 'phone', label: 'Phone', ph: '19494169971' },
    { key: 'website', label: 'Website', ph: 'https://saintsallabs.com' },
    { key: 'address', label: 'Address', ph: '221 Main Street Suite J, Huntington Beach, CA' },
    { key: 'tagline', label: 'Tagline', ph: 'Gotta Guy!!' }
  ];
  fields.forEach(function(f) {
    html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">' + f.label + '</label>';
    html += '<input value="' + _esc(d[f.key] || '') + '" placeholder="' + f.ph + '" oninput="csState.cardData[\'' + f.key + '\']=this.value;csUpdateCardPreview()" style="width:100%;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.3);color:var(--text-primary);font-size:13px;box-sizing:border-box;"></div>';
  });

  // Social links in 2-col grid
  html += '<div style="font-size:12px;font-weight:600;color:var(--text-secondary);margin:14px 0 8px;">Social Links</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">';
  var socials = [
    { key: 'linkedin', label: 'LinkedIn', ph: 'linkedin.com/in/...' },
    { key: 'instagram', label: 'Instagram', ph: '@saintvisions' },
    { key: 'twitter', label: 'Twitter/X', ph: '@SaintVisions' },
    { key: 'facebook', label: 'Facebook', ph: 'facebook.com/...' },
    { key: 'tiktok', label: 'TikTok', ph: '@saintvisions' },
    { key: 'github', label: 'GitHub', ph: 'github.com/...' }
  ];
  socials.forEach(function(s) {
    html += '<input value="' + _esc(d[s.key] || '') + '" placeholder="' + s.ph + '" oninput="csState.cardData[\'' + s.key + '\']=this.value;csUpdateCardPreview()" style="padding:7px 10px;border-radius:6px;border:1px solid rgba(255,255,255,.08);background:rgba(0,0,0,.3);color:var(--text-primary);font-size:11px;box-sizing:border-box;" title="' + s.label + '">';
  });
  html += '</div>';

  // Avatar + Banner uploads
  html += '<div style="display:flex;gap:12px;margin-top:14px;">';
  html += '<div style="flex:1;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Profile Photo</label>';
  html += '<label style="display:block;padding:10px;border-radius:8px;border:1px dashed rgba(255,255,255,.15);text-align:center;cursor:pointer;font-size:11px;color:var(--text-muted);">' + (d.avatar_b64 ? '✅ Photo loaded' : '📷 Upload') + '<input type="file" accept="image/*" onchange="csHandleUpload(this,\'cardData\',\'avatar_b64\')" style="display:none;"></label></div>';
  html += '<div style="flex:1;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Banner Image</label>';
  html += '<label style="display:block;padding:10px;border-radius:8px;border:1px dashed rgba(255,255,255,.15);text-align:center;cursor:pointer;font-size:11px;color:var(--text-muted);">' + (d.banner_b64 ? '✅ Banner loaded' : '🖼 Upload') + '<input type="file" accept="image/*" onchange="csHandleUpload(this,\'cardData\',\'banner_b64\')" style="display:none;"></label></div>';
  html += '</div>';

  // Accent color
  html += '<div style="margin-top:14px;display:flex;align-items:center;gap:10px;">';
  html += '<label style="font-size:11px;color:var(--text-muted);">Accent</label>';
  html += '<input type="color" value="' + d.accent_color + '" oninput="csState.cardData.accent_color=this.value;csUpdateCardPreview()" style="width:40px;height:28px;border:none;border-radius:6px;cursor:pointer;background:none;">';
  html += '</div>';

  html += '<button onclick="csGenerateCard()" ' + (csState.cardLoading ? 'disabled' : '') + ' style="width:100%;padding:12px;border-radius:10px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:700;font-size:14px;cursor:pointer;margin-top:16px;">' + (csState.cardLoading ? 'Generating...' : '💳 Generate Card + QR Code') + '</button>';
  html += '</div>';

  // ── RIGHT: Live Preview ──
  html += '<div style="background:var(--surface-raised,#141414);border-radius:12px;padding:20px;">';
  html += '<div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:16px;">Card Preview</div>';
  html += '<div id="csCardPreview">' + csRenderCardPreview() + '</div>';

  // QR Code section
  if (csState.cardPreview && csState.cardPreview.qr_png) {
    html += '<div style="margin-top:20px;text-align:center;">';
    html += '<div style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">Scan to save contact</div>';
    html += '<img src="data:image/png;base64,' + csState.cardPreview.qr_png + '" style="width:160px;height:160px;border-radius:12px;background:#fff;padding:8px;" alt="QR Code">';
    html += '</div>';
  }

  // Download buttons
  if (d.name && d.email) {
    html += '<div style="display:flex;gap:8px;margin-top:16px;">';
    html += '<button onclick="csDownloadVCard()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:none;color:var(--text-secondary);font-size:12px;font-weight:600;cursor:pointer;">📥 Download vCard</button>';
    html += '<button onclick="csShareCard()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:none;color:var(--text-secondary);font-size:12px;font-weight:600;cursor:pointer;">🔗 Share Link</button>';
    html += '</div>';
  }
  html += '</div>';
  html += '</div>';
  return html;
}

function csRenderCardPreview() {
  var d = csState.cardData;
  if (!d.name && !d.company) {
    return '<div style="text-align:center;padding:60px 20px;color:var(--text-muted);"><div style="font-size:36px;margin-bottom:12px;">💳</div><div style="font-size:14px;">Fill in your details to see a live preview</div></div>';
  }
  var accent = d.accent_color || '#D4A843';
  var bannerBg = d.banner_b64 ? 'url(' + d.banner_b64 + ') center/cover' : 'linear-gradient(135deg, #1a1a2e 0%, ' + accent + '33 100%)';
  var html = '';
  html += '<div style="border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);background:#111;max-width:420px;margin:0 auto;">';

  // Banner
  html += '<div style="height:120px;background:' + bannerBg + ';position:relative;">';
  if (d.company) {
    html += '<div style="position:absolute;top:12px;right:14px;font-size:10px;letter-spacing:2px;color:rgba(255,255,255,.7);text-transform:uppercase;font-weight:600;">' + _esc(d.company) + '</div>';
  }
  html += '</div>';

  // Avatar overlapping
  html += '<div style="padding:0 24px;margin-top:-40px;position:relative;">';
  if (d.avatar_b64) {
    html += '<div style="width:80px;height:80px;border-radius:50%;border:3px solid #111;overflow:hidden;background:#222;"><img src="' + d.avatar_b64 + '" style="width:100%;height:100%;object-fit:cover;"></div>';
  } else {
    html += '<div style="width:80px;height:80px;border-radius:50%;border:3px solid #111;background:linear-gradient(135deg,' + accent + ',' + accent + '88);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;color:#000;">' + _esc((d.name || 'S')[0]) + '</div>';
  }
  html += '</div>';

  // Info
  html += '<div style="padding:12px 24px 20px;">';
  html += '<div style="font-size:22px;font-weight:700;color:#fff;">' + _esc(d.name || 'Your Name') + '</div>';
  html += '<div style="font-size:13px;color:' + accent + ';font-weight:600;margin-top:2px;">' + _esc(d.title || 'Title') + '</div>';
  if (d.company) html += '<div style="font-size:13px;color:#999;margin-top:1px;">' + _esc(d.company) + '</div>';
  if (d.tagline) html += '<div style="font-size:12px;color:#777;font-style:italic;margin-top:8px;">' + _esc(d.tagline) + '</div>';

  // Contact details
  html += '<div style="margin-top:16px;display:flex;flex-direction:column;gap:8px;">';
  if (d.email) html += '<div style="display:flex;align-items:center;gap:8px;font-size:12px;"><span style="width:28px;height:28px;border-radius:50%;background:' + accent + '22;display:flex;align-items:center;justify-content:center;color:' + accent + ';font-size:14px;">✉</span><span style="color:#ccc;">' + _esc(d.email) + '</span></div>';
  if (d.phone) html += '<div style="display:flex;align-items:center;gap:8px;font-size:12px;"><span style="width:28px;height:28px;border-radius:50%;background:' + accent + '22;display:flex;align-items:center;justify-content:center;color:' + accent + ';font-size:14px;">📞</span><span style="color:#ccc;">' + _esc(d.phone) + '</span></div>';
  if (d.website) html += '<div style="display:flex;align-items:center;gap:8px;font-size:12px;"><span style="width:28px;height:28px;border-radius:50%;background:' + accent + '22;display:flex;align-items:center;justify-content:center;color:' + accent + ';font-size:14px;">🌐</span><span style="color:#ccc;">' + _esc(d.website) + '</span></div>';
  if (d.address) html += '<div style="display:flex;align-items:center;gap:8px;font-size:12px;"><span style="width:28px;height:28px;border-radius:50%;background:' + accent + '22;display:flex;align-items:center;justify-content:center;color:' + accent + ';font-size:14px;">📍</span><span style="color:#ccc;">' + _esc(d.address) + '</span></div>';
  html += '</div>';

  // Social icons
  var socialIcons = [];
  if (d.linkedin) socialIcons.push({icon:'in', color:'#0A66C2', url:d.linkedin});
  if (d.instagram) socialIcons.push({icon:'📷', color:'#E4405F', url:d.instagram});
  if (d.twitter) socialIcons.push({icon:'𝕏', color:'#fff', url:d.twitter});
  if (d.facebook) socialIcons.push({icon:'f', color:'#1877F2', url:d.facebook});
  if (d.tiktok) socialIcons.push({icon:'♪', color:'#ff0050', url:d.tiktok});
  if (d.github) socialIcons.push({icon:'⌘', color:'#fff', url:d.github});
  if (socialIcons.length > 0) {
    html += '<div style="display:flex;gap:8px;margin-top:16px;">';
    socialIcons.forEach(function(s) {
      html += '<div style="width:32px;height:32px;border-radius:50%;background:' + s.color + ';display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#fff;cursor:pointer;">' + s.icon + '</div>';
    });
    html += '</div>';
  }

  // Save contact button
  html += '<button onclick="csDownloadVCard()" style="width:100%;margin-top:16px;padding:10px;border-radius:8px;border:none;background:' + accent + ';color:#000;font-weight:700;font-size:13px;cursor:pointer;">Save contact</button>';

  html += '</div></div>';
  return html;
}

function csUpdateCardPreview() {
  var el = document.getElementById('csCardPreview');
  if (el) el.innerHTML = csRenderCardPreview();
}

function csHandleUpload(input, stateKey, field) {
  var file = input.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(e) {
    csState[stateKey][field] = e.target.result;
    csUpdateCardPreview();
    csUpdateSigPreview();
    renderCareerSuite();
  };
  reader.readAsDataURL(file);
}

function csDownloadVCard() {
  var d = csState.cardData;
  if (!d.name) return;
  var vcard = 'BEGIN:VCARD\nVERSION:3.0\n';
  vcard += 'FN:' + d.name + '\n';
  if (d.title) vcard += 'TITLE:' + d.title + '\n';
  if (d.company) vcard += 'ORG:' + d.company + '\n';
  if (d.email) vcard += 'EMAIL:' + d.email + '\n';
  if (d.phone) vcard += 'TEL;TYPE=CELL:' + d.phone + '\n';
  if (d.website) vcard += 'URL:' + d.website + '\n';
  if (d.address) vcard += 'ADR;TYPE=WORK:;;' + d.address + '\n';
  if (d.linkedin) vcard += 'X-SOCIALPROFILE;TYPE=linkedin:' + d.linkedin + '\n';
  if (d.instagram) vcard += 'X-SOCIALPROFILE;TYPE=instagram:' + d.instagram + '\n';
  if (d.twitter) vcard += 'X-SOCIALPROFILE;TYPE=twitter:' + d.twitter + '\n';
  if (d.tagline) vcard += 'NOTE:' + d.tagline + '\n';
  vcard += 'END:VCARD';
  var blob = new Blob([vcard], { type: 'text/vcard' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = (d.name.replace(/\s+/g, '_') || 'contact') + '.vcf';
  a.click();
  csShowToast('vCard downloaded — open to save to contacts');
}

function csShareCard() {
  if (navigator.share) {
    var d = csState.cardData;
    navigator.share({ title: d.name + ' - Digital Business Card', text: d.name + ' | ' + d.title + ' | ' + d.company + '\n' + d.email + ' | ' + d.phone, url: d.website || 'https://saintsallabs.com' });
  } else {
    csShowToast('Sharing not supported — try on mobile');
  }
}

async function csGenerateCard() {
  var d = csState.cardData;
  if (!d.name || !d.email) { csShowToast('Enter at least name and email'); return; }
  csState.cardLoading = true;
  renderCareerSuite();
  try {
    var r = await fetch(CS_API + '/api/career/cards/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(d)
    });
    csState.cardPreview = await r.json();
  } catch(e) { console.error(e); }
  csState.cardLoading = false;
  renderCareerSuite();
}




/* ══════════════════════════════════════════════════════════════════════════════
   EMAIL SIGNATURES TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csSignature() {
  var d = csState.sigData;
  var html = '';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">';

  // ── LEFT: Form ──
  html += '<div style="background:var(--surface-raised,#141414);border-radius:12px;padding:20px;overflow-y:auto;max-height:calc(100vh - 220px);">';
  html += '<div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:16px;">Email Signature</div>';

  var fields = [
    { key: 'name', label: 'Full Name', ph: 'Ryan Capatosto' },
    { key: 'title', label: 'Job Title', ph: 'Chief Executive Officer' },
    { key: 'company', label: 'Company', ph: 'Saint Vision, Inc.' },
    { key: 'headline', label: 'Headline', ph: 'Visit Cookin.io' },
    { key: 'email', label: 'Email', ph: 'ryan@cookin.io' },
    { key: 'phone', label: 'Phone', ph: '+1(949) 416-9971' },
    { key: 'website', label: 'Website', ph: 'https://saintsallabs.com' },
    { key: 'linkedin', label: 'LinkedIn', ph: 'linkedin.com/in/...' },
    { key: 'instagram', label: 'Instagram', ph: '@saintvisions' },
    { key: 'twitter', label: 'Twitter/X', ph: '@SaintVisions' }
  ];
  fields.forEach(function(f) {
    html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">' + f.label + '</label>';
    html += '<input value="' + _esc(d[f.key] || '') + '" placeholder="' + f.ph + '" oninput="csState.sigData[\'' + f.key + '\']=this.value;csUpdateSigPreview()" style="width:100%;padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.3);color:var(--text-primary);font-size:13px;box-sizing:border-box;"></div>';
  });

  // Photo upload
  html += '<div style="margin-top:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Headshot Photo</label>';
  html += '<label style="display:block;padding:10px;border-radius:8px;border:1px dashed rgba(255,255,255,.15);text-align:center;cursor:pointer;font-size:11px;color:var(--text-muted);">' + (d.avatar_b64 ? '✅ Photo loaded' : '📷 Upload Photo') + '<input type="file" accept="image/*" onchange="csHandleUpload(this,\'sigData\',\'avatar_b64\')" style="display:none;"></label></div>';

  // Template selector
  html += '<div style="margin-top:14px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:6px;">Template</label>';
  html += '<div style="display:flex;gap:8px;">';
  ['executive','classic','modern'].forEach(function(t) {
    var active = d.template === t;
    html += '<button onclick="csState.sigData.template=\'' + t + '\';csUpdateSigPreview();renderCareerSuite()" style="flex:1;padding:8px;border-radius:8px;border:1px solid ' + (active ? 'var(--accent-gold)' : 'rgba(255,255,255,.1)') + ';background:' + (active ? 'var(--accent-gold-dim,rgba(212,168,67,.15))' : 'none') + ';color:' + (active ? 'var(--accent-gold)' : 'var(--text-muted)') + ';font-size:11px;font-weight:600;cursor:pointer;text-transform:capitalize;">' + t + '</button>';
  });
  html += '</div></div>';

  // Accent
  html += '<div style="margin-top:14px;display:flex;align-items:center;gap:10px;">';
  html += '<label style="font-size:11px;color:var(--text-muted);">Accent</label>';
  html += '<input type="color" value="' + d.accent_color + '" oninput="csState.sigData.accent_color=this.value;csUpdateSigPreview()" style="width:40px;height:28px;border:none;border-radius:6px;cursor:pointer;background:none;">';
  html += '</div>';

  html += '<button onclick="csGenerateSignature()" ' + (csState.sigLoading ? 'disabled' : '') + ' style="width:100%;padding:12px;border-radius:10px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:700;font-size:14px;cursor:pointer;margin-top:16px;">' + (csState.sigLoading ? 'Generating...' : '✉️ Generate Signature') + '</button>';
  html += '</div>';

  // ── RIGHT: Preview ──
  html += '<div style="background:var(--surface-raised,#141414);border-radius:12px;padding:20px;">';
  html += '<div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:16px;">Signature Preview</div>';
  html += '<div id="csSigPreview" style="background:#fff;border-radius:12px;padding:20px;">' + csRenderSigPreview() + '</div>';

  // Actions
  html += '<div style="display:flex;gap:8px;margin-top:16px;">';
  html += '<button data-testid="sig-copy-html-btn" onclick="csCopySignature()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:none;color:var(--text-secondary);font-size:12px;font-weight:600;cursor:pointer;"><i class="fas fa-copy"></i> Copy HTML</button>';
  html += '<button data-testid="sig-add-to-email-btn" onclick="csCopySignaturePlain()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:none;color:var(--text-secondary);font-size:12px;font-weight:600;cursor:pointer;"><i class="fas fa-envelope"></i> Add to Email</button>';
  html += '</div>';
  html += '</div>';

  html += '</div>';
  return html;
}

function csRenderSigPreview() {
  var d = csState.sigData;
  if (!d.name && !d.company) return '<div style="text-align:center;padding:40px;color:#999;">Fill in details for live preview</div>';
  var accent = d.accent_color || '#D4A843';
  var name = _esc(d.name || 'Your Name');
  var title = _esc(d.title || '');
  var company = _esc(d.company || '');
  var headline = _esc(d.headline || '');

  // Build based on template
  var h = '';
  if (d.template === 'modern') {
    h += '<table cellpadding="0" cellspacing="0" style="font-family:Arial,sans-serif;font-size:13px;color:#333;">';
    h += '<tr><td style="border-left:4px solid ' + accent + ';padding-left:14px;">';
    h += '<table cellpadding="0" cellspacing="0"><tr>';
    if (d.avatar_b64 && d.show_photo !== false) {
      h += '<td style="padding-right:14px;vertical-align:top;"><img src="' + d.avatar_b64 + '" width="80" height="80" style="border-radius:50%;object-fit:cover;border:2px solid ' + accent + ';" alt=""></td>';
    }
    h += '<td style="vertical-align:top;">';
    h += '<div style="font-size:18px;font-weight:700;color:#111;">' + name + '</div>';
    h += '<div style="font-size:13px;color:' + accent + ';font-weight:600;">' + title + '</div>';
    h += '<div style="font-size:12px;color:#666;">' + company + '</div>';
    if (headline) h += '<div style="font-size:11px;color:#999;margin-top:4px;">' + headline + '</div>';
    h += '<div style="margin-top:10px;font-size:12px;color:#555;">';
    if (d.email) h += '<div>✉ <a href="mailto:' + _esc(d.email) + '" style="color:' + accent + ';text-decoration:none;">' + _esc(d.email) + '</a></div>';
    if (d.phone) h += '<div>📞 ' + _esc(d.phone) + '</div>';
    if (d.website) h += '<div>🌐 <a href="' + _esc(d.website) + '" style="color:' + accent + ';text-decoration:none;">' + _esc(d.website) + '</a></div>';
    h += '</div>';
    h += '</td></tr></table></td></tr></table>';
  } else if (d.template === 'classic') {
    h += '<table cellpadding="0" cellspacing="0" style="font-family:Georgia,serif;font-size:13px;color:#333;"><tr>';
    if (d.avatar_b64 && d.show_photo !== false) {
      h += '<td style="padding-right:16px;vertical-align:top;"><img src="' + d.avatar_b64 + '" width="90" height="90" style="border-radius:8px;object-fit:cover;" alt=""></td>';
    }
    h += '<td style="vertical-align:top;">';
    h += '<div style="font-size:18px;font-weight:700;color:#111;">' + name + '</div>';
    h += '<div style="font-size:13px;color:#555;">' + title + (company ? ' · ' + company : '') + '</div>';
    if (headline) h += '<div style="font-size:11px;color:#888;">' + headline + '</div>';
    h += '<div style="width:60px;height:2px;background:' + accent + ';margin:10px 0;"></div>';
    h += '<div style="font-size:11px;line-height:1.8;color:#555;">';
    if (d.email) h += '✉ <a href="mailto:' + _esc(d.email) + '" style="color:#333;text-decoration:none;">' + _esc(d.email) + '</a><br>';
    if (d.phone) h += '📞 ' + _esc(d.phone) + '<br>';
    if (d.website) h += '🌐 <a href="' + _esc(d.website) + '" style="color:#333;text-decoration:none;">' + _esc(d.website) + '</a>';
    h += '</div></td></tr></table>';
  } else {
    // Executive (default)
    h += '<table cellpadding="0" cellspacing="0" style="font-family:Arial,sans-serif;font-size:13px;color:#333;">';
    h += '<tr><td style="padding-bottom:12px;">';
    h += '<table cellpadding="0" cellspacing="0"><tr>';
    if (d.avatar_b64 && d.show_photo !== false) {
      h += '<td style="padding-right:14px;vertical-align:top;"><img src="' + d.avatar_b64 + '" width="80" height="80" style="border-radius:50%;object-fit:cover;" alt=""></td>';
    }
    h += '<td style="vertical-align:top;">';
    h += '<div style="font-size:18px;font-weight:700;color:#111;">' + name + '</div>';
    h += '<div style="font-size:13px;color:' + accent + ';font-weight:600;">' + title + '</div>';
    h += '<div style="font-size:12px;color:#666;">' + company + '</div>';
    if (headline) h += '<div style="font-size:11px;color:#888;margin-top:2px;">' + headline + '</div>';
    h += '</td></tr></table></td></tr>';
    h += '<tr><td style="border-top:2px solid ' + accent + ';padding-top:10px;">';
    h += '<table cellpadding="0" cellspacing="0" style="font-size:11px;color:#555;"><tr>';
    if (d.email) h += '<td style="padding-right:20px;">✉ <a href="mailto:' + _esc(d.email) + '" style="color:#333;text-decoration:none;">' + _esc(d.email) + '</a></td>';
    if (d.phone) h += '<td style="padding-right:20px;">📞 ' + _esc(d.phone) + '</td>';
    h += '</tr></table>';
    if (d.website) h += '<div style="margin-top:4px;font-size:11px;">🌐 <a href="' + _esc(d.website) + '" style="color:' + accent + ';text-decoration:none;">' + _esc(d.website) + '</a></div>';
    h += '</td></tr></table>';
  }

  // Social icons
  var icons = [];
  if (d.linkedin) icons.push('<a href="' + _esc(d.linkedin) + '" style="display:inline-block;width:24px;height:24px;border-radius:50%;background:#0A66C2;text-align:center;line-height:24px;color:#fff;font-size:11px;font-weight:700;text-decoration:none;">in</a>');
  if (d.instagram) icons.push('<a href="' + _esc(d.instagram) + '" style="display:inline-block;width:24px;height:24px;border-radius:50%;background:#E4405F;text-align:center;line-height:24px;color:#fff;font-size:11px;text-decoration:none;">📷</a>');
  if (d.twitter) icons.push('<a href="' + _esc(d.twitter) + '" style="display:inline-block;width:24px;height:24px;border-radius:50%;background:#333;text-align:center;line-height:24px;color:#fff;font-size:11px;text-decoration:none;">𝕏</a>');
  if (icons.length > 0) {
    h += '<div style="margin-top:10px;display:flex;gap:6px;">' + icons.join('') + '</div>';
  }

  // Powered by badge
  h += '<div style="margin-top:12px;font-size:9px;color:#bbb;letter-spacing:1px;">POWERED BY SAINTSAL™ AI</div>';

  return h;
}

function csUpdateSigPreview() {
  var el = document.getElementById('csSigPreview');
  if (el) el.innerHTML = csRenderSigPreview();
}

async function csGenerateSignature() {
  var d = csState.sigData;
  if (!d.name || !d.email) { csShowToast('Enter at least name and email'); return; }
  csState.sigLoading = true;
  renderCareerSuite();
  try {
    var r = await fetch(CS_API + '/api/career/signature/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(d)
    });
    var data = await r.json();
    csState.sigPreview = data.signature_html || csRenderSigPreview();
  } catch(e) { csState.sigPreview = csRenderSigPreview(); }
  csState.sigLoading = false;
  renderCareerSuite();
}

function csCopySignature() {
  var html = csState.sigPreview || csRenderSigPreview();
  if (!html) return;
  var blob = new Blob([html], { type: 'text/html' });
  var item = new ClipboardItem({ 'text/html': blob, 'text/plain': new Blob([html], { type: 'text/plain' }) });
  navigator.clipboard.write([item]).then(function() {
    csShowToast('Signature copied — paste into your email settings');
  }).catch(function() {
    navigator.clipboard.writeText(html).then(function() { csShowToast('HTML copied to clipboard'); });
  });
}

function csCopySignaturePlain() {
  csShowToast('To add: Go to Gmail Settings → Signature → Paste the copied HTML. Or Outlook → File → Options → Mail → Signatures.');
  csCopySignature();
}




/* ══════════════════════════════════════════════════════════════════════════════
   AI CAREER COACH TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csCoach() {
  var html = '';
  html += '<div style="background:var(--surface-raised,#141414);border-radius:10px;padding:16px;min-height:400px;display:flex;flex-direction:column;">';
  html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:12px;">SAL Career Coach</div>';

  // Messages
  html += '<div id="csCoachMessages" style="flex:1;overflow-y:auto;margin-bottom:12px;max-height:350px;">';
  if (csState.coachMessages.length === 0) {
    html += '<div style="text-align:center;padding:40px 20px;color:var(--text-muted);">';
    html += '<div style="font-size:28px;margin-bottom:10px;">🧠</div>';
    html += '<div style="font-size:13px;margin-bottom:12px;">Your AI career strategist</div>';
    html += '<div style="font-size:11px;color:var(--text-muted);line-height:1.6;">Ask about salary negotiation, career transitions, offer evaluation, interview strategy, resume tips, or anything career-related.</div>';
    html += '</div>';
  } else {
    csState.coachMessages.forEach(function(msg) {
      var isUser = msg.role === 'user';
      html += '<div style="margin-bottom:10px;display:flex;justify-content:' + (isUser ? 'flex-end' : 'flex-start') + ';">';
      html += '<div style="max-width:85%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.6;'
           + (isUser ? 'background:var(--accent-gold,#D4A843);color:#000;border-bottom-right-radius:4px;' : 'background:var(--surface-base,#0a0a0a);color:var(--text-secondary);border-bottom-left-radius:4px;')
           + '">' + _esc(msg.text).replace(/\n/g, '<br>') + '</div></div>';
    });
  }
  if (csState.coachLoading) {
    html += '<div style="display:flex;justify-content:flex-start;margin-bottom:10px;">';
    html += '<div style="padding:10px 14px;border-radius:12px;background:var(--surface-base,#0a0a0a);color:var(--text-muted);font-size:12px;">Thinking...</div></div>';
  }
  html += '</div>';

  // Input
  html += '<div style="display:flex;gap:8px;">';
  html += '<input id="csCoachInput" placeholder="Ask SAL anything about your career..." '
       + 'onkeydown="if(event.key===\'Enter\')csCoachSend()" '
       + 'style="flex:1;padding:10px 14px;border-radius:8px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:13px;">';
  html += '<button onclick="csCoachSend()" style="padding:10px 20px;border-radius:8px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:13px;cursor:pointer;">Send</button>';
  html += '</div>';

  // Quick prompts
  html += '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;">';
  var prompts = ['How do I negotiate a higher salary?', 'Should I take this offer?', 'Career transition advice', 'How to prepare for a VP interview'];
  prompts.forEach(function(p) {
    html += '<button onclick="csCoachQuickPrompt(\'' + p.replace(/'/g, "\\'") + '\')" '
         + 'style="padding:5px 10px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:none;color:var(--text-muted);font-size:10px;cursor:pointer;">' + p + '</button>';
  });
  html += '</div>';
  html += '</div>';
  return html;
}

async function csCoachSend() {
  var inp = document.getElementById('csCoachInput');
  if (!inp || !inp.value.trim()) return;
  var msg = inp.value.trim();
  csState.coachMessages.push({ role: 'user', text: msg });
  csState.coachLoading = true;
  renderCareerSuite();
  // Scroll to bottom
  setTimeout(function() { var el = document.getElementById('csCoachMessages'); if (el) el.scrollTop = el.scrollHeight; }, 50);

  try {
    var r = await fetch(CS_API + '/api/career/coach/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    var data = await r.json();
    csState.coachMessages.push({ role: 'assistant', text: data.response || 'No response.' });
  } catch(e) {
    csState.coachMessages.push({ role: 'assistant', text: 'Coach temporarily unavailable. Please try again.' });
  }
  csState.coachLoading = false;
  renderCareerSuite();
  setTimeout(function() { var el = document.getElementById('csCoachMessages'); if (el) el.scrollTop = el.scrollHeight; }, 50);
}

function csCoachQuickPrompt(text) {
  var inp = document.getElementById('csCoachInput');
  if (inp) inp.value = text;
  csCoachSend();
}


/* ══════════════════════════════════════════════════════════════════════════════
   INTERVIEW PREP TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csInterview() {
  var html = '';
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">';

  // Form
  html += '<div style="background:var(--surface-raised,#141414);border-radius:10px;padding:16px;">';
  html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:14px;">Interview Prep Generator</div>';

  html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Company</label>';
  html += '<input id="csPrepCompany" value="' + _esc(csState.prepCompany) + '" placeholder="Google, Apple, Stripe..." '
       + 'oninput="csState.prepCompany=this.value" '
       + 'style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;box-sizing:border-box;"></div>';

  html += '<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Role</label>';
  html += '<input id="csPrepRole" value="' + _esc(csState.prepRole) + '" placeholder="Senior Software Engineer" '
       + 'oninput="csState.prepRole=this.value" '
       + 'style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;box-sizing:border-box;"></div>';

  html += '<div style="margin-bottom:14px;"><label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:3px;">Interview Type</label>';
  html += '<select id="csPrepType" onchange="csState.prepType=this.value" '
       + 'style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;">';
  ['behavioral', 'technical', 'system_design', 'case_study', 'executive'].forEach(function(t) {
    html += '<option value="' + t + '"' + (csState.prepType === t ? ' selected' : '') + '>' + t.charAt(0).toUpperCase() + t.slice(1).replace('_', ' ') + '</option>';
  });
  html += '</select></div>';

  html += '<button onclick="csGeneratePrep()" ' + (csState.prepLoading ? 'disabled' : '') + ' '
       + 'style="width:100%;padding:10px;border-radius:8px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:13px;cursor:pointer;margin-bottom:16px;">'
       + (csState.prepLoading ? 'Generating...' : '🎤 Generate Prep Package') + '</button>';

  // Company Intel section
  html += '<div style="border-top:1px solid var(--border-subtle,#222);padding-top:14px;">';
  html += '<div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:10px;">Company Intel</div>';
  html += '<div style="display:flex;gap:8px;">';
  html += '<input id="csIntelCompany" value="' + _esc(csState.intelCompany) + '" placeholder="Company name..." '
       + 'oninput="csState.intelCompany=this.value" '
       + 'onkeydown="if(event.key===\'Enter\')csGetCompanyIntel()" '
       + 'style="flex:1;padding:8px 12px;border-radius:6px;border:1px solid var(--border-subtle,#333);background:var(--surface-base,#0a0a0a);color:var(--text-primary);font-size:12px;">';
  html += '<button onclick="csGetCompanyIntel()" style="padding:8px 14px;border-radius:6px;border:none;background:var(--accent-gold,#D4A843);color:#000;font-weight:600;font-size:12px;cursor:pointer;">Research</button>';
  html += '</div>';
  if (csState.intelLoading) html += csLoadingSpinner('Researching...');
  if (csState.intelResult) {
    var intel = csState.intelResult;
    html += '<div style="margin-top:10px;font-size:12px;color:var(--text-secondary);line-height:1.6;">';
    if (intel.overview) html += '<p style="margin-bottom:8px;">' + _esc(intel.overview) + '</p>';
    if (intel.interview_tips && intel.interview_tips.length) {
      html += '<div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-bottom:4px;">INTERVIEW TIPS</div>';
      intel.interview_tips.forEach(function(tip) { html += '<div style="padding-left:10px;margin-bottom:3px;">• ' + _esc(tip) + '</div>'; });
    }
    if (intel.questions_to_ask && intel.questions_to_ask.length) {
      html += '<div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-top:8px;margin-bottom:4px;">QUESTIONS TO ASK</div>';
      intel.questions_to_ask.forEach(function(q) { html += '<div style="padding-left:10px;margin-bottom:3px;">• ' + _esc(q) + '</div>'; });
    }
    html += '</div>';
  }
  html += '</div>';
  html += '</div>';

  // Results
  html += '<div style="background:var(--surface-raised,#141414);border-radius:10px;padding:16px;">';
  html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:14px;">Prep Package</div>';
  if (csState.prepLoading) {
    html += csLoadingSpinner('Building your prep package...');
  } else if (csState.prepResult) {
    var p = csState.prepResult;
    // Likely Questions
    if (p.likely_questions && p.likely_questions.length) {
      html += '<div style="margin-bottom:16px;"><div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-bottom:8px;">LIKELY QUESTIONS</div>';
      p.likely_questions.forEach(function(q, i) {
        html += '<div style="background:var(--surface-base,#0a0a0a);border-radius:8px;padding:10px;margin-bottom:6px;">';
        html += '<div style="font-size:12px;font-weight:600;color:var(--text-primary);margin-bottom:4px;">' + (i+1) + '. ' + _esc(q.question || '') + '</div>';
        if (q.why_they_ask) html += '<div style="font-size:10px;color:var(--text-muted);margin-bottom:4px;">Why: ' + _esc(q.why_they_ask) + '</div>';
        if (q.model_answer) html += '<div style="font-size:11px;color:var(--text-secondary);line-height:1.5;">' + _esc(q.model_answer) + '</div>';
        html += '</div>';
      });
      html += '</div>';
    }
    // Salary Range
    if (p.salary_range) {
      var sr = p.salary_range;
      html += '<div style="margin-bottom:16px;"><div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-bottom:6px;">SALARY RANGE</div>';
      html += '<div style="display:flex;gap:12px;font-size:13px;">';
      html += '<div style="text-align:center;"><div style="color:var(--text-muted);font-size:10px;">Low</div><div style="color:var(--text-primary);font-weight:600;">$' + (sr.low || '?').toLocaleString() + '</div></div>';
      html += '<div style="text-align:center;"><div style="color:var(--text-muted);font-size:10px;">Mid</div><div style="color:var(--accent-gold,#D4A843);font-weight:600;">$' + (sr.mid || '?').toLocaleString() + '</div></div>';
      html += '<div style="text-align:center;"><div style="color:var(--text-muted);font-size:10px;">High</div><div style="color:#2ecc71;font-weight:600;">$' + (sr.high || '?').toLocaleString() + '</div></div>';
      html += '</div>';
      if (sr.note) html += '<div style="font-size:10px;color:var(--text-muted);margin-top:4px;">' + _esc(sr.note) + '</div>';
      html += '</div>';
    }
    // STAR Examples
    if (p.star_examples && p.star_examples.length) {
      html += '<div style="margin-bottom:16px;"><div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-bottom:6px;">STAR STORY STARTERS</div>';
      p.star_examples.forEach(function(s) { html += '<div style="font-size:11px;color:var(--text-secondary);margin-bottom:4px;">• ' + _esc(s) + '</div>'; });
      html += '</div>';
    }
    // Negotiation Script
    if (p.negotiation_script) {
      html += '<div style="margin-bottom:16px;"><div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-bottom:6px;">NEGOTIATION SCRIPT</div>';
      html += '<div style="font-size:11px;color:var(--text-secondary);line-height:1.6;background:var(--surface-base,#0a0a0a);padding:10px;border-radius:6px;">' + _esc(p.negotiation_script) + '</div></div>';
    }
    // Day-of Checklist
    if (p.day_of_checklist && p.day_of_checklist.length) {
      html += '<div><div style="font-size:11px;font-weight:600;color:var(--accent-gold,#D4A843);margin-bottom:6px;">DAY-OF CHECKLIST</div>';
      p.day_of_checklist.forEach(function(item) { html += '<div style="font-size:11px;color:var(--text-secondary);margin-bottom:3px;">☐ ' + _esc(item) + '</div>'; });
      html += '</div>';
    }
  } else {
    html += '<div style="text-align:center;padding:40px 20px;color:var(--text-muted);">';
    html += '<div style="font-size:28px;margin-bottom:10px;">🎤</div>';
    html += '<div style="font-size:13px;">Enter company and role to generate a full interview prep package</div>';
    html += '</div>';
  }
  html += '</div>';
  html += '</div>';
  return html;
}

async function csGeneratePrep() {
  if (!csState.prepCompany || !csState.prepRole) { csShowToast('Enter company and role'); return; }
  csState.prepLoading = true;
  csState.prepResult = null;
  renderCareerSuite();
  try {
    var r = await fetch(CS_API + '/api/career/coach/interview-prep', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company: csState.prepCompany, role: csState.prepRole, interview_type: csState.prepType })
    });
    var data = await r.json();
    if (data.prep) csState.prepResult = data.prep;
  } catch(e) { console.error(e); }
  csState.prepLoading = false;
  renderCareerSuite();
}

async function csGetCompanyIntel() {
  if (!csState.intelCompany) return;
  csState.intelLoading = true;
  csState.intelResult = null;
  renderCareerSuite();
  try {
    var r = await fetch(CS_API + '/api/career/company-intel?company=' + encodeURIComponent(csState.intelCompany));
    var data = await r.json();
    csState.intelResult = data.intel || null;
  } catch(e) { console.error(e); }
  csState.intelLoading = false;
  renderCareerSuite();
}


/* ══════════════════════════════════════════════════════════════════════════════
   VIDEO BACKGROUNDS TAB
   ══════════════════════════════════════════════════════════════════════════════ */
function csBackgrounds() {
  var html = '';
  html += '<div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:14px;">Professional Video Backgrounds</div>';
  html += '<p style="font-size:12px;color:var(--text-muted);margin-bottom:16px;">Look the part on every video call. Click to preview.</p>';

  if (csState.bgLoading) return csLoadingSpinner('Loading backgrounds...');

  if (csState.bgTemplates.length > 0) {
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;">';
    csState.bgTemplates.forEach(function(bg) {
      var tierBadge = bg.tier === 'free' ? '' : '<span style="position:absolute;top:8px;right:8px;padding:2px 8px;border-radius:4px;background:var(--accent-gold,#D4A843);color:#000;font-size:9px;font-weight:600;text-transform:uppercase;">' + bg.tier + '</span>';
      html += '<div style="position:relative;border-radius:10px;overflow:hidden;cursor:pointer;transition:transform 0.15s;" '
           + 'onmouseenter="this.style.transform=\'scale(1.02)\'" onmouseleave="this.style.transform=\'none\'">';
      html += '<div style="height:140px;background:' + bg.gradient + ';display:flex;align-items:center;justify-content:center;">';
      html += '<div style="width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,0.1);border:2px solid rgba(255,255,255,0.2);"></div>';
      html += '</div>';
      html += tierBadge;
      html += '<div style="padding:10px 12px;background:var(--surface-raised,#141414);">';
      html += '<div style="font-size:12px;font-weight:600;color:var(--text-primary);">' + _esc(bg.name) + '</div>';
      html += '<div style="font-size:10px;color:var(--text-muted);">' + _esc(bg.desc) + '</div>';
      html += '</div></div>';
    });
    html += '</div>';
  } else {
    html += '<div style="text-align:center;padding:40px;color:var(--text-muted);">';
    html += '<div style="font-size:28px;margin-bottom:10px;">🖼️</div>';
    html += '<div style="font-size:13px;">No backgrounds loaded. Check back soon.</div>';
    html += '</div>';
  }
  return html;
}

function csLoadBackgrounds() {
  if (csState.bgTemplates.length > 0) return; // already loaded
  csState.bgLoading = true;
  renderCareerSuite();
  fetch(CS_API + '/api/career/backgrounds/templates').then(function(r) { return r.json(); }).then(function(data) {
    csState.bgTemplates = data.templates || [];
    csState.bgLoading = false;
    renderCareerSuite();
  }).catch(function() { csState.bgLoading = false; renderCareerSuite(); });
}


/* ══════════════════════════════════════════════════════════════════════════════
   COVER LETTER AI
   ══════════════════════════════════════════════════════════════════════════════ */
var clState = { resumeText: '', jobDesc: '', style: 'direct', result: null, loading: false };
function csCoverLetter() {
  var h = '<div data-testid="career-cover-letter">';
  h += '<h2 style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">Cover Letter AI</h2>';
  h += '<p style="color:var(--text-muted);font-size:13px;margin-bottom:16px;">Generate a tailored cover letter from your resume + job description.</p>';
  if (clState.result && !clState.loading) {
    h += '<div style="background:var(--surface-raised,#1a1a1a);border:1px solid var(--border-color,#2a2a2a);border-radius:12px;padding:16px;margin-bottom:12px;">';
    h += '<div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--accent-gold);font-weight:600;">Generated Cover Letter</span>';
    h += '<span style="color:var(--text-muted);font-size:12px;">' + (clState.result.word_count||0) + ' words | ' + (clState.result.keywords_matched?.length||0) + ' keywords matched</span></div>';
    h += '<div style="color:var(--text-primary);font-size:14px;line-height:1.7;white-space:pre-wrap;">' + _esc(clState.result.cover_letter) + '</div>';
    h += '<div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap;">';
    h += '<button data-testid="cl-copy-btn" onclick="navigator.clipboard.writeText(clState.result.cover_letter);csShowToast(\'Copied!\')" style="padding:8px 16px;border-radius:8px;border:none;background:var(--accent-gold);color:#000;font-weight:600;font-size:12px;cursor:pointer;">Copy</button>';
    if (csState.clSavedId) {
      h += '<button data-testid="cl-download-pdf-btn" onclick="csExportCoverLetter(\'pdf\')" style="padding:8px 16px;border-radius:8px;border:1px solid var(--accent-gold);background:none;color:var(--accent-gold);font-weight:600;font-size:12px;cursor:pointer;"><i class="fas fa-file-pdf"></i> PDF</button>';
      h += '<button data-testid="cl-download-docx-btn" onclick="csExportCoverLetter(\'docx\')" style="padding:8px 16px;border-radius:8px;border:1px solid var(--accent-gold);background:none;color:var(--accent-gold);font-weight:600;font-size:12px;cursor:pointer;"><i class="fas fa-file-word"></i> DOCX</button>';
    } else {
      h += '<button data-testid="cl-save-export-btn" onclick="csSaveCoverLetterAndExport()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--accent-gold);background:none;color:var(--accent-gold);font-weight:600;font-size:12px;cursor:pointer;">Save & Export</button>';
    }
    h += '<button onclick="clState.result=null;csState.clSavedId=null;renderCareerSuite()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--border-color);background:transparent;color:var(--text-secondary);font-size:12px;cursor:pointer;">New Letter</button></div></div></div>';
    return h;
  }
  h += '<div style="display:flex;flex-direction:column;gap:12px;">';
  h += '<textarea id="clResume" data-testid="cl-resume-input" rows="5" style="width:100%;padding:12px;border-radius:8px;border:1px solid var(--border-color,#2a2a2a);background:var(--surface-raised,#1a1a1a);color:var(--text-primary);font-size:13px;resize:vertical;" placeholder="Paste your resume or key experience...">' + _esc(clState.resumeText) + '</textarea>';
  h += '<textarea id="clJobDesc" data-testid="cl-job-input" rows="5" style="width:100%;padding:12px;border-radius:8px;border:1px solid var(--border-color,#2a2a2a);background:var(--surface-raised,#1a1a1a);color:var(--text-primary);font-size:13px;resize:vertical;" placeholder="Paste the job description...">' + _esc(clState.jobDesc) + '</textarea>';
  h += '<div style="display:flex;gap:8px;">';
  ['direct','storytelling','technical'].forEach(function(s){
    var a = clState.style===s;
    h += '<button onclick="clState.style=\'' + s + '\';renderCareerSuite()" style="padding:7px 14px;border-radius:8px;border:1px solid '+(a?'var(--accent-gold)':'var(--border-color)')+';background:'+(a?'rgba(212,160,67,0.15)':'transparent')+';color:'+(a?'var(--accent-gold)':'var(--text-secondary)')+';font-size:12px;cursor:pointer;text-transform:capitalize;">'+s+'</button>';
  });
  h += '</div>';
  h += clState.loading ? csLoadingSpinner('Crafting your cover letter...') : '<button data-testid="cl-generate-btn" onclick="csGenerateCoverLetter()" style="padding:12px 24px;border-radius:10px;border:none;background:var(--accent-gold);color:#000;font-weight:700;font-size:14px;cursor:pointer;width:100%;">Generate Cover Letter</button>';
  h += '</div></div>'; return h;
}
function csGenerateCoverLetter() {
  var r = document.getElementById('clResume'), j = document.getElementById('clJobDesc');
  if (!r||!j||!r.value.trim()||!j.value.trim()) { csShowToast('Fill in both fields'); return; }
  if (typeof salCheckAccess === 'function') { salCheckAccess('career_coverletter').then(function(ok){ if(!ok)return; _doGenerateCoverLetter(r,j); }); } else { _doGenerateCoverLetter(r,j); }
}
function _doGenerateCoverLetter(r,j) {
  clState.resumeText=r.value; clState.jobDesc=j.value; clState.loading=true; csState.clSavedId=null; renderCareerSuite();
  fetch((window.API||'')+'/api/career/cover-letter',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({resume_text:clState.resumeText,job_description:clState.jobDesc,style:clState.style})}).then(function(r){return r.json()}).then(function(d){clState.result=d;clState.loading=false;if(typeof salLogUsage==='function')salLogUsage('cover_letter',3);renderCareerSuite()}).catch(function(e){clState.loading=false;csShowToast('Error: '+e.message);renderCareerSuite()});
}

async function csSaveCoverLetterAndExport() {
  if (!clState.result || !clState.result.cover_letter) { csShowToast('Generate a cover letter first'); return; }
  try {
    var r = await fetch(CS_API + '/api/career/v2/cover-letters', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: clState.result.cover_letter, style: clState.style,
        target_company: clState.result.company || '', target_role: clState.result.role || '',
        name: 'Cover Letter', saintssal_enhanced: true })
    });
    var data = await r.json();
    if (data.cover_letter_id) {
      csState.clSavedId = data.cover_letter_id;
      csShowToast('Saved — now choose PDF or DOCX');
      renderCareerSuite();
    }
  } catch(e) { console.error('[Career] Save CL error:', e); csShowToast('Save failed'); }
}

function csExportCoverLetter(fmt) {
  if (!csState.clSavedId) { csShowToast('Save cover letter first'); return; }
  var url = CS_API + '/api/career/v2/cover-letters/' + csState.clSavedId + '/export/' + fmt;
  window.open(url, '_blank');
  csShowToast('Downloading ' + fmt.toUpperCase() + '...');
}

/* ══════════════════════════════════════════════════════════════════════════════
   LINKEDIN OPTIMIZER
   ══════════════════════════════════════════════════════════════════════════════ */
var liState = { profileText: '', result: null, loading: false };
function csLinkedInOptimizer() {
  var h = '<div data-testid="career-linkedin-optimizer">';
  h += '<h2 style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">LinkedIn Optimizer</h2>';
  if (liState.result && !liState.loading) {
    var r = liState.result;
    h += '<div style="display:flex;gap:12px;margin-bottom:14px;">';
    h += '<div style="flex:1;background:rgba(239,68,68,0.08);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:26px;font-weight:800;color:#ef4444;">'+(r.score_before||45)+'</div><div style="font-size:11px;color:var(--text-muted);">Before</div></div>';
    h += '<div style="flex:1;background:rgba(34,197,94,0.08);border-radius:10px;padding:14px;text-align:center;"><div style="font-size:26px;font-weight:800;color:#22c55e;">'+(r.score_after||85)+'</div><div style="font-size:11px;color:var(--text-muted);">After</div></div></div>';
    h += '<div style="background:var(--surface-raised);border:1px solid var(--border-color);border-radius:12px;padding:14px;margin-bottom:12px;"><div style="color:var(--accent-gold);font-weight:600;font-size:13px;margin-bottom:6px;">Optimized Headline</div><div style="color:var(--text-primary);font-size:14px;">'+_esc(r.headline||'')+'</div></div>';
    h += '<div style="background:var(--surface-raised);border:1px solid var(--border-color);border-radius:12px;padding:14px;margin-bottom:12px;"><div style="color:var(--accent-gold);font-weight:600;font-size:13px;margin-bottom:6px;">Optimized Summary</div><div style="color:var(--text-primary);font-size:13px;line-height:1.7;white-space:pre-wrap;">'+_esc(r.summary||'')+'</div></div>';
    if (r.skills_to_add&&r.skills_to_add.length){h+='<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">';r.skills_to_add.forEach(function(s){h+='<span style="padding:4px 10px;border-radius:6px;background:rgba(96,165,250,0.1);color:#60a5fa;font-size:12px;">'+_esc(s)+'</span>'});h+='</div>';}
    h += '<button onclick="liState.result=null;renderCareerSuite()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--border-color);background:transparent;color:var(--text-secondary);font-size:12px;cursor:pointer;">Optimize Another</button></div>';
    return h;
  }
  h += '<textarea id="liProfile" data-testid="li-profile-input" rows="8" style="width:100%;padding:12px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;resize:vertical;margin-bottom:12px;" placeholder="Paste your current LinkedIn profile text here...">'+_esc(liState.profileText)+'</textarea>';
  h += liState.loading ? csLoadingSpinner('Analyzing your profile...') : '<button data-testid="li-optimize-btn" onclick="csOptimizeLinkedIn()" style="padding:12px 24px;border-radius:10px;border:none;background:var(--accent-gold);color:#000;font-weight:700;font-size:14px;cursor:pointer;width:100%;">Optimize My Profile</button>';
  h += '</div>'; return h;
}
function csOptimizeLinkedIn() {
  var el = document.getElementById('liProfile');
  if (!el||!el.value.trim()){csShowToast('Paste your LinkedIn profile');return;}
  liState.profileText=el.value;liState.loading=true;renderCareerSuite();
  fetch((window.API||'')+'/api/career/linkedin-optimize',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({current_profile_text:liState.profileText})}).then(function(r){return r.json()}).then(function(d){liState.result=d;liState.loading=false;renderCareerSuite()}).catch(function(e){liState.loading=false;csShowToast('Error: '+e.message);renderCareerSuite()});
}

/* ══════════════════════════════════════════════════════════════════════════════
   SALARY NEGOTIATOR
   ══════════════════════════════════════════════════════════════════════════════ */
var snState = { role: '', location: '', years: 5, offer: '', result: null, loading: false };
function csSalaryNegotiator() {
  var h = '<div data-testid="career-salary-negotiator">';
  h += '<h2 style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">Salary Negotiator</h2>';
  h += '<p style="color:var(--text-muted);font-size:13px;margin-bottom:14px;">Get market data + word-for-word negotiation scripts.</p>';
  if (snState.result && !snState.loading) {
    var r = snState.result, range = r.market_range||{};
    h += '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px;">';
    [['low','Low'],['median','Median'],['high','High'],['top_10_pct','Top 10%']].forEach(function(k){var v=range[k[0]]||'N/A';if(typeof v==='number')v='$'+v.toLocaleString();h+='<div style="background:var(--surface-raised);border-radius:10px;padding:12px;text-align:center;border:1px solid var(--border-color);"><div style="font-size:15px;font-weight:700;color:var(--accent-gold);">'+v+'</div><div style="font-size:11px;color:var(--text-muted);">'+k[1]+'</div></div>'});
    h += '</div>';
    h += '<div style="background:var(--surface-raised);border:1px solid var(--border-color);border-radius:12px;padding:14px;margin-bottom:12px;"><div style="color:var(--accent-gold);font-weight:600;font-size:13px;margin-bottom:6px;">Counter-Offer Script</div><div style="color:var(--text-primary);font-size:13px;line-height:1.7;white-space:pre-wrap;">'+_esc(r.counter_offer_script||'')+'</div></div>';
    h += '<button onclick="snState.result=null;renderCareerSuite()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--border-color);background:transparent;color:var(--text-secondary);font-size:12px;cursor:pointer;">New Analysis</button></div>';
    return h;
  }
  h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">';
  h += '<input id="snRole" data-testid="sn-role-input" type="text" value="'+_esc(snState.role)+'" style="padding:10px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;" placeholder="Role (e.g. Senior Engineer)">';
  h += '<input id="snLocation" type="text" value="'+_esc(snState.location)+'" style="padding:10px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;" placeholder="Location (e.g. SF, CA)"></div>';
  h += '<div style="display:grid;grid-template-columns:80px 1fr;gap:10px;margin-bottom:12px;">';
  h += '<input id="snYears" type="number" value="'+snState.years+'" style="padding:10px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;" placeholder="Yrs">';
  h += '<input id="snOffer" type="text" value="'+_esc(snState.offer)+'" style="padding:10px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;" placeholder="Current offer (optional)"></div>';
  h += snState.loading ? csLoadingSpinner('Researching market data...') : '<button data-testid="sn-negotiate-btn" onclick="csNegotiateSalary()" style="padding:12px 24px;border-radius:10px;border:none;background:var(--accent-gold);color:#000;font-weight:700;font-size:14px;cursor:pointer;width:100%;">Get Negotiation Strategy</button>';
  h += '</div>'; return h;
}
function csNegotiateSalary() {
  var r=document.getElementById('snRole');if(!r||!r.value.trim()){csShowToast('Enter a role');return;}
  snState.role=r.value;snState.location=(document.getElementById('snLocation')||{}).value||'';snState.years=parseInt((document.getElementById('snYears')||{}).value)||5;snState.offer=(document.getElementById('snOffer')||{}).value||'';snState.loading=true;renderCareerSuite();
  fetch((window.API||'')+'/api/career/salary-negotiate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:snState.role,location:snState.location,experience_years:snState.years,offer_details:snState.offer})}).then(function(r){return r.json()}).then(function(d){snState.result=d;snState.loading=false;renderCareerSuite()}).catch(function(e){snState.loading=false;csShowToast('Error: '+e.message);renderCareerSuite()});
}

/* ══════════════════════════════════════════════════════════════════════════════
   NETWORK MAPPER
   ══════════════════════════════════════════════════════════════════════════════ */
var nmState = { company: '', linkedin: '', result: null, loading: false };
function csNetworkMapper() {
  var h = '<div data-testid="career-network-mapper">';
  h += '<h2 style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">Network Mapper</h2>';
  h += '<p style="color:var(--text-muted);font-size:13px;margin-bottom:14px;">Find key connections at your target company + get intro templates.</p>';
  if (nmState.result && !nmState.loading) {
    var r = nmState.result;
    if (r.connections&&r.connections.length){h+='<div style="margin-bottom:14px;"><div style="color:var(--accent-gold);font-weight:600;font-size:13px;margin-bottom:8px;">Key Connections</div>';r.connections.forEach(function(c){h+='<div style="background:var(--surface-raised);border:1px solid var(--border-color);border-radius:10px;padding:10px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;"><div><div style="color:var(--text-primary);font-weight:600;font-size:13px;">'+_esc(c.name||'')+'</div><div style="color:var(--text-muted);font-size:12px;">'+_esc(c.title||'')+'</div></div>'+(c.linkedin_url?'<a href="'+c.linkedin_url+'" target="_blank" style="color:#60a5fa;font-size:12px;">LinkedIn</a>':'')+'</div>'});h+='</div>';}
    if (r.approach_strategy){h+='<div style="background:var(--surface-raised);border:1px solid rgba(212,160,67,0.2);border-radius:10px;padding:14px;margin-bottom:12px;"><div style="color:var(--accent-gold);font-weight:600;font-size:13px;margin-bottom:6px;">Strategy</div><div style="color:var(--text-primary);font-size:13px;line-height:1.6;">'+_esc(r.approach_strategy)+'</div></div>';}
    h += '<button onclick="nmState.result=null;renderCareerSuite()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--border-color);background:transparent;color:var(--text-secondary);font-size:12px;cursor:pointer;">New Search</button></div>';
    return h;
  }
  h += '<input id="nmCompany" data-testid="nm-company-input" type="text" value="'+_esc(nmState.company)+'" style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;margin-bottom:10px;" placeholder="Target Company (Google, Apple, Meta...)">';
  h += '<input id="nmLinkedIn" type="text" value="'+_esc(nmState.linkedin)+'" style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border-color);background:var(--surface-raised);color:var(--text-primary);font-size:13px;margin-bottom:12px;" placeholder="Your LinkedIn URL (optional)">';
  h += nmState.loading ? csLoadingSpinner('Mapping network...') : '<button data-testid="nm-map-btn" onclick="csMapNetwork()" style="padding:12px 24px;border-radius:10px;border:none;background:var(--accent-gold);color:#000;font-weight:700;font-size:14px;cursor:pointer;width:100%;">Map Network</button>';
  h += '</div>'; return h;
}
function csMapNetwork() {
  var c=document.getElementById('nmCompany');if(!c||!c.value.trim()){csShowToast('Enter a company');return;}
  nmState.company=c.value;nmState.linkedin=(document.getElementById('nmLinkedIn')||{}).value||'';nmState.loading=true;renderCareerSuite();
  fetch((window.API||'')+'/api/career/network-map',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target_company:nmState.company,user_linkedin_url:nmState.linkedin})}).then(function(r){return r.json()}).then(function(d){nmState.result=d;nmState.loading=false;renderCareerSuite()}).catch(function(e){nmState.loading=false;csShowToast('Error: '+e.message);renderCareerSuite()});
}

/* ── Tab setter for Cmd+K palette ── */
window.csSetTab = function(tab) { csState.activeTab = tab; renderCareerSuite(); };


/* ══════════════════════════════════════════════════════════════════════════════
   UTILITIES
   ══════════════════════════════════════════════════════════════════════════════ */
function _esc(str) {
  if (!str) return '';
  var d = document.createElement('div');
  d.textContent = String(str);
  return d.innerHTML;
}

function csLoadingSpinner(text) {
  return '<div style="text-align:center;padding:30px;"><div style="display:inline-block;width:28px;height:28px;border:3px solid var(--border-subtle,#333);border-top-color:var(--accent-gold,#D4A843);border-radius:50%;animation:csSpin 0.8s linear infinite;"></div>'
       + '<div style="font-size:12px;color:var(--text-muted);margin-top:8px;">' + (text || 'Loading...') + '</div></div>';
}

function csShowToast(msg) {
  var toast = document.createElement('div');
  toast.textContent = msg;
  toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);padding:10px 20px;border-radius:8px;background:var(--accent-gold,#D4A843);color:#000;font-size:13px;font-weight:600;z-index:9999;opacity:0;transition:opacity 0.3s;';
  document.body.appendChild(toast);
  setTimeout(function() { toast.style.opacity = '1'; }, 10);
  setTimeout(function() { toast.style.opacity = '0'; setTimeout(function() { toast.remove(); }, 300); }, 2500);
}
