/**
 * Cognify - Main Application Controller
 */

const App = {
  quizTimerInterval: null,
  activeFilter: 'all',

  init() {
    this.setupEvents();
    this.checkInitialAuth();
  },

  setupEvents() {
    window.addEventListener('auth:expired', () => {
      this.showToast('Your session has expired. Please sign in again.', 'warning');
      this.navigateTo('auth');
    });

    // Setup Drag and Drop on Upload Zone
    const dropzone = document.getElementById('upload-dropzone');
    if (dropzone) {
      ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          dropzone.classList.add('dragover-active');
        }, false);
      });

      ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          dropzone.classList.remove('dragover-active');
        }, false);
      });

      dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
          this.processFileUpload(files[0]);
        }
      });
    }

    // Close user dropdown if clicked outside
    document.addEventListener('click', (e) => {
      const menu = document.getElementById('user-dropdown-menu');
      const profile = document.getElementById('nav-user-profile');
      if (menu && profile && !profile.contains(e.target)) {
        menu.classList.add('hidden');
      }
    });
  },

  async checkInitialAuth() {
    const token = Api.getToken();
    if (token) {
      try {
        const user = await Api.getMe();
        State.user = user;
        this.updateUserUI();
        this.navigateTo('dashboard');
      } catch (err) {
        Api.setToken(null);
        this.navigateTo('auth');
      }
    } else {
      this.navigateTo('auth');
    }
  },

  // ==============================================================
  // NAVIGATION ROUTER
  // ==============================================================
  navigateTo(viewName) {
    // If not authenticated and trying to view app, redirect to auth
    if (!State.user && viewName !== 'auth') {
      viewName = 'auth';
    }

    State.currentView = viewName;

    // Hide all views
    const views = [
      'view-auth', 'view-dashboard', 'view-learn-topic', 
      'view-upload', 'view-lesson', 'view-quiz', 
      'view-mastery-summary', 'view-progress'
    ];
    views.forEach(v => {
      const el = document.getElementById(v);
      if (el) el.classList.add('hidden');
    });

    // Show target view
    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.remove('hidden');
    }

    // Update active navbar styles
    const navItems = ['nav-dashboard', 'nav-learn', 'nav-upload', 'nav-progress'];
    navItems.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.classList.remove('text-indigo-600', 'bg-indigo-50', 'font-bold');
        el.classList.add('text-slate-700');
      }
    });

    if (viewName === 'dashboard') {
      const el = document.getElementById('nav-dashboard');
      if (el) { el.classList.add('text-indigo-600', 'bg-indigo-50', 'font-bold'); }
      this.loadDashboard();
    } else if (viewName === 'learn-topic') {
      const el = document.getElementById('nav-learn');
      if (el) { el.classList.add('text-indigo-600', 'bg-indigo-50', 'font-bold'); }
      this.loadCuratedTopics();
    } else if (viewName === 'upload') {
      const el = document.getElementById('nav-upload');
      if (el) { el.classList.add('text-indigo-600', 'bg-indigo-50', 'font-bold'); }
    } else if (viewName === 'progress') {
      const el = document.getElementById('nav-progress');
      if (el) { el.classList.add('text-indigo-600', 'bg-indigo-50', 'font-bold'); }
      this.loadProgressDashboard();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  // ==============================================================
  // AUTH CONTROLLERS
  // ==============================================================
  switchAuthTab(tab) {
    const loginTab = document.getElementById('auth-tab-login');
    const regTab = document.getElementById('auth-tab-register');
    const loginForm = document.getElementById('form-login');
    const regForm = document.getElementById('form-register');
    const alert = document.getElementById('auth-alert');
    if (alert) alert.classList.add('hidden');

    if (tab === 'login') {
      loginTab.classList.add('text-indigo-600', 'border-indigo-600');
      loginTab.classList.remove('text-slate-500', 'border-transparent');
      regTab.classList.remove('text-indigo-600', 'border-indigo-600');
      regTab.classList.add('text-slate-500', 'border-transparent');
      loginForm.classList.remove('hidden');
      regForm.classList.add('hidden');
    } else {
      regTab.classList.add('text-indigo-600', 'border-indigo-600');
      regTab.classList.remove('text-slate-500', 'border-transparent');
      loginTab.classList.remove('text-indigo-600', 'border-indigo-600');
      loginTab.classList.add('text-slate-500', 'border-transparent');
      regForm.classList.remove('hidden');
      loginForm.classList.add('hidden');
    }
  },

  async handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const btn = document.getElementById('btn-login-submit');

    try {
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Signing In...</span>`;
      const res = await Api.login(email, password);
      State.user = res.user;
      this.updateUserUI();
      this.showToast(`Welcome back, ${res.user.name}!`, 'success');
      this.navigateTo('dashboard');
    } catch (err) {
      this.showAuthAlert(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>Sign In to Learn</span><i class="fa-solid fa-arrow-right text-xs"></i>`;
    }
  },

  async handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const btn = document.getElementById('btn-register-submit');

    try {
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Creating Account...</span>`;
      const res = await Api.register(name, email, password);
      State.user = res.user;
      this.updateUserUI();
      this.showToast(`Welcome to Cognify, ${res.user.name}!`, 'success');
      this.navigateTo('dashboard');
    } catch (err) {
      this.showAuthAlert(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<span>Create Account</span><i class="fa-solid fa-check text-xs"></i>`;
    }
  },

  async loginAsDemo() {
    const demoEmail = "demo_student@cognify.ai";
    const demoPassword = "DemoPassword123!";
    try {
      try {
        const res = await Api.login(demoEmail, demoPassword);
        State.user = res.user;
      } catch (err) {
        // If demo user doesn't exist, create it
        const res = await Api.register("Alex Morgan (Demo)", demoEmail, demoPassword);
        State.user = res.user;
      }
      this.updateUserUI();
      this.showToast("Signed in as Demo Student!", "success");
      this.navigateTo('dashboard');
    } catch (err) {
      this.showToast("Demo sign in error: " + err.message, "error");
    }
  },

  showAuthAlert(message, type = 'error') {
    const alert = document.getElementById('auth-alert');
    if (!alert) return;
    alert.classList.remove('hidden', 'bg-rose-50', 'text-rose-700', 'border-rose-200', 'bg-emerald-50', 'text-emerald-700', 'border-emerald-200');
    if (type === 'error') {
      alert.classList.add('bg-rose-50', 'text-rose-700', 'border', 'border-rose-200');
      alert.innerHTML = `<i class="fa-solid fa-circle-exclamation text-rose-500"></i><span>${message}</span>`;
    } else {
      alert.classList.add('bg-emerald-50', 'text-emerald-700', 'border', 'border-emerald-200');
      alert.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-500"></i><span>${message}</span>`;
    }
  },

  updateUserUI() {
    if (!State.user) return;
    const nameEl = document.getElementById('user-display-name');
    const avatarEl = document.getElementById('user-avatar-initials');
    const dropdownName = document.getElementById('dropdown-user-name');
    const dropdownEmail = document.getElementById('dropdown-user-email');
    const dashName = document.getElementById('dash-user-name');
    const streakCount = document.getElementById('nav-streak-count');

    if (nameEl) nameEl.textContent = State.user.name;
    if (dropdownName) dropdownName.textContent = State.user.name;
    if (dropdownEmail) dropdownEmail.textContent = State.user.email;
    if (dashName) dashName.textContent = State.user.name.split(' ')[0];
    if (streakCount) streakCount.textContent = State.user.current_streak || 1;

    if (avatarEl && State.user.name) {
      const parts = State.user.name.trim().split(' ');
      const initials = parts.length > 1 ? (parts[0][0] + parts[1][0]) : parts[0].substring(0, 2);
      avatarEl.textContent = initials.toUpperCase();
    }
  },

  toggleUserDropdown() {
    const menu = document.getElementById('user-dropdown-menu');
    if (menu) menu.classList.toggle('hidden');
  },

  logout() {
    Api.logout();
    State.user = null;
    State.resetSession();
    this.showToast('You have been signed out.', 'info');
    this.navigateTo('auth');
  },

  // ==============================================================
  // DASHBOARD CONTROLLER
  // ==============================================================
  async loadDashboard() {
    try {
      const data = await Api.getDashboard();
      State.dashboardData = data;

      // Update Top Metrics
      const solvedEl = document.getElementById('dash-stat-solved');
      const accEl = document.getElementById('dash-stat-accuracy');
      const progVal = document.getElementById('dash-progress-val');
      const circleEl = document.getElementById('dash-circle-progress');
      const avgTime = document.getElementById('dash-avg-time');
      const hintsStat = document.getElementById('dash-hints-stat');

      if (solvedEl) solvedEl.textContent = data.total_questions_solved;
      if (accEl) accEl.textContent = `${data.accuracy_percent}% Accuracy`;
      if (progVal) progVal.textContent = `${Math.round(data.overall_progress_percent)}%`;
      if (avgTime) avgTime.textContent = `${data.avg_response_time_seconds}s`;
      if (hintsStat) hintsStat.textContent = `${data.total_hints_used} used`;

      // Update circle SVG stroke offset (Circumference ~ 163.36)
      if (circleEl) {
        const offset = 163.36 - (163.36 * (data.overall_progress_percent / 100));
        circleEl.style.strokeDashoffset = offset;
      }

      // Update Cognitive Load HUD in Navbar and Dashboard
      this.updateCognitiveLoadBadge(data.current_cognitive_load);

      // Render Continue Learning Section if any active sessions
      const continueContainer = document.getElementById('dash-continue-container');
      const recentList = document.getElementById('dash-recent-list');
      if (data.recent_sessions && data.recent_sessions.length > 0) {
        continueContainer.classList.remove('hidden');
        recentList.innerHTML = data.recent_sessions.map(s => `
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition card-glow-hover flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between text-[11px] mb-2">
                <span class="font-bold uppercase tracking-wider text-indigo-600">${s.subject}</span>
                <span class="px-2 py-0.5 rounded-full ${s.is_completed ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'} font-semibold">
                  ${s.is_completed ? 'Mastered ✓' : 'In Progress'}
                </span>
              </div>
              <h4 class="text-sm font-bold text-slate-900">${s.topic_name}</h4>
              <p class="text-xs text-slate-500 mt-1 line-clamp-2">${s.description || 'Comprehensive curriculum'}</p>
            </div>
            
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <span class="text-xs text-slate-500 font-medium">Concept ${s.current_concept_index + 1} of ${s.total_concepts}</span>
              <button onclick="App.startTopicSession(${s.topic_id})" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center space-x-1">
                <span>${s.is_completed ? 'Review' : 'Continue'}</span>
                <i class="fa-solid fa-play text-[10px]"></i>
              </button>
            </div>
          </div>
        `).join('');
      } else {
        continueContainer.classList.add('hidden');
      }

      // Render Topic-Wise Mastery Status
      const masteryListEl = document.getElementById('dash-mastery-list');
      if (data.topic_mastery_records && data.topic_mastery_records.length > 0) {
        masteryListEl.innerHTML = data.topic_mastery_records.map(m => {
          const score = Math.round(m.mastery_score);
          const colorClass = score >= 75 ? 'bg-emerald-500' : (score >= 50 ? 'bg-amber-500' : 'bg-rose-500');
          const badgeClass = score >= 75 ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : (score >= 50 ? 'text-amber-700 bg-amber-50 border-amber-200' : 'text-rose-700 bg-rose-50 border-rose-200');
          const statusIcon = score >= 75 ? '🟢 Mastered' : (score >= 50 ? '🟡 In Progress' : '🔴 Needs Review');

          return `
            <div class="p-3.5 rounded-xl border border-slate-100 hover:border-slate-200 bg-slate-50/50 transition">
              <div class="flex items-center justify-between mb-2">
                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">${m.subject}</span>
                  <h4 class="text-xs font-bold text-slate-800">${m.topic_name}</h4>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-xs font-black text-slate-700">${score}%</span>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${badgeClass}">${statusIcon}</span>
                </div>
              </div>
              <div class="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div class="${colorClass} h-2 rounded-full transition-all duration-700" style="width: ${score}%"></div>
              </div>
              ${m.weak_concepts && m.weak_concepts.length > 0 ? `
                <p class="text-[10px] text-slate-500 mt-2">
                  <strong class="text-rose-600">Review recommendation:</strong> Focus on <em>${m.weak_concepts.slice(0, 2).join(', ')}</em>
                </p>
              ` : ''}
            </div>
          `;
        }).join('');
      } else {
        masteryListEl.innerHTML = `
          <div class="text-center py-8 text-slate-400 text-xs">
            <i class="fa-solid fa-chart-simple text-3xl mb-2 text-slate-300"></i>
            <p>Start your first learning session to populate your mastery metrics.</p>
            <button onclick="App.navigateTo('learn-topic')" class="mt-3 px-4 py-2 bg-indigo-50 text-indigo-600 rounded-xl text-xs font-semibold hover:bg-indigo-100 transition">
              Browse Topics
            </button>
          </div>
        `;
      }

      // Strong and Weak Concepts
      const strongPills = document.getElementById('dash-strong-pills');
      const weakPills = document.getElementById('dash-weak-pills');

      if (strongPills) {
        if (data.strong_concepts && data.strong_concepts.length > 0) {
          strongPills.innerHTML = data.strong_concepts.map(c => `
            <span class="text-[11px] px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-100 font-medium">✓ ${c}</span>
          `).join('');
        } else {
          strongPills.innerHTML = `<span class="text-slate-400 text-xs">Complete quizzes to unlock strengths</span>`;
        }
      }

      if (weakPills) {
        if (data.weak_concepts && data.weak_concepts.length > 0) {
          weakPills.innerHTML = data.weak_concepts.map(c => `
            <span class="text-[11px] px-2.5 py-1 bg-rose-50 text-rose-700 rounded-lg border border-rose-100 font-medium">⚠ ${c}</span>
          `).join('');
        } else {
          weakPills.innerHTML = `<span class="text-slate-400 text-xs">No active conceptual weaknesses</span>`;
        }
      }

    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  },

  updateCognitiveLoadBadge(load) {
    const navPill = document.getElementById('nav-cognitive-pill');
    const navLabel = document.getElementById('nav-cognitive-label');
    const dashBadge = document.getElementById('dash-cog-badge');
    const dashIcon = document.getElementById('dash-cog-icon');
    const dashTitle = document.getElementById('dash-cog-title');
    const dashSub = document.getElementById('dash-cog-sub');

    const clean = (load || 'LOW').toUpperCase();

    let badgeClass = 'load-badge-low';
    let iconClass = 'bg-emerald-500';
    let label = 'Low Load · Flow State';
    let sub = 'Optimal speed · Accelerated challenges';

    if (clean === 'HIGH') {
      badgeClass = 'load-badge-high';
      iconClass = 'bg-rose-500';
      label = 'High Load · Scaffolding Active';
      sub = 'Mental friction detected · Pacing slowed, worked examples ready';
    } else if (clean === 'MEDIUM' || clean === 'BALANCED') {
      badgeClass = 'load-badge-medium';
      iconClass = 'bg-amber-500';
      label = 'Balanced Load · Optimal Challenge';
      sub = 'Desirable difficulty · Standard practice';
    }

    if (navPill) {
      navPill.className = `hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border cursor-pointer ${badgeClass} transition hover:shadow`;
    }
    if (navLabel) navLabel.textContent = label;

    if (dashBadge) {
      dashBadge.className = `p-4 rounded-xl border flex items-center space-x-4 ${badgeClass}`;
    }
    if (dashIcon) dashIcon.className = `w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow ${iconClass}`;
    if (dashTitle) dashTitle.textContent = `${clean} COGNITIVE LOAD`;
    if (dashSub) dashSub.textContent = sub;
  },

  // ==============================================================
  // LEARN A TOPIC CONTROLLER
  // ==============================================================
  async loadCuratedTopics() {
    try {
      const topics = await Api.getCuratedTopics();
      State.curatedTopics = topics;
      this.renderCuratedTopicsGrid(topics);
    } catch (err) {
      this.showToast("Could not load topics catalog: " + err.message, "error");
    }
  },

  filterCuratedTopics(subject) {
    this.activeFilter = subject;
    const buttons = document.querySelectorAll('.topic-tab-btn');
    buttons.forEach(b => {
      b.classList.remove('bg-indigo-600', 'text-white', 'font-semibold');
      b.classList.add('bg-white', 'text-slate-700');
    });

    event.target.classList.remove('bg-white', 'text-slate-700');
    event.target.classList.add('bg-indigo-600', 'text-white', 'font-semibold');

    let filtered = State.curatedTopics;
    if (subject !== 'all') {
      filtered = State.curatedTopics.filter(t => t.subject.toLowerCase() === subject.toLowerCase());
    }
    this.renderCuratedTopicsGrid(filtered);
  },

  renderCuratedTopicsGrid(topics) {
    const grid = document.getElementById('curated-topics-grid');
    if (!grid) return;

    if (!topics || topics.length === 0) {
      grid.innerHTML = `
        <div class="col-span-3 text-center py-12 text-slate-400 text-xs">
          <i class="fa-solid fa-folder-open text-4xl mb-2 text-slate-300"></i>
          <p>No topics found in this category.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = topics.map(t => `
      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all card-glow-hover flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between text-xs mb-3">
            <span class="px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-100">
              ${t.subject}
            </span>
            <span class="text-slate-400 text-[11px]">
              <i class="fa-solid fa-layer-group mr-1"></i>${t.concept_count} Concepts
            </span>
          </div>
          <h3 class="text-base font-bold text-slate-900">${t.topic_name}</h3>
          <p class="text-xs text-slate-500 mt-2 leading-relaxed line-clamp-3">${t.description}</p>

          <div class="mt-4 pt-3 border-t border-slate-100">
            <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Curriculum Sequence:</p>
            <div class="space-y-1">
              ${(t.concept_titles || []).slice(0, 3).map((title, i) => `
                <div class="flex items-center text-xs text-slate-600">
                  <span class="w-4 h-4 rounded-full bg-slate-100 text-[10px] font-bold text-slate-500 flex items-center justify-center mr-2 flex-shrink-0">${i+1}</span>
                  <span class="truncate">${title}</span>
                </div>
              `).join('')}
              ${t.concept_count > 3 ? `<p class="text-[10px] text-slate-400 pl-6">+${t.concept_count - 3} more concepts</p>` : ''}
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
          <span class="text-[11px] font-medium text-slate-400 capitalize">Difficulty: ${t.difficulty_level || 'Adaptive'}</span>
          <button onclick="App.startTopicSession(${t.id})" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-100 transition flex items-center space-x-1.5">
            <span>Start Learning</span>
            <i class="fa-solid fa-arrow-right text-[10px]"></i>
          </button>
        </div>
      </div>
    `).join('');
  },

  async startTopicSession(topicId) {
    try {
      this.showToast("Initializing AI pedagogical session...", "info");
      const sessionData = await Api.startLearningSession(topicId);

      State.activeSession.sessionId = sessionData.session_id;
      State.activeSession.topicId = sessionData.topic_id;
      State.activeSession.topicName = sessionData.topic_name;
      State.activeSession.subject = sessionData.subject;
      State.activeSession.conceptIndex = sessionData.concept_index;
      State.activeSession.totalConcepts = sessionData.total_concepts;
      State.activeSession.concept = sessionData.concept;
      State.activeSession.question = sessionData.question;
      State.activeSession.currentDifficulty = sessionData.current_difficulty;
      State.activeSession.currentTeachingStyle = sessionData.teaching_style;
      State.activeSession.cognitiveLoad = sessionData.current_cognitive_load;
      State.activeSession.consecutiveHighLoad = sessionData.consecutive_high_load_count;

      this.renderLessonView();
      this.navigateTo('lesson');
    } catch (err) {
      this.showToast("Failed to launch session: " + err.message, "error");
    }
  },

  showCustomTopicModal() {
    const modal = document.getElementById('modal-custom-topic');
    if (modal) modal.classList.remove('hidden');
  },

  hideCustomTopicModal() {
    const modal = document.getElementById('modal-custom-topic');
    if (modal) modal.classList.add('hidden');
  },

  async handleCreateCustomTopic(e) {
    e.preventDefault();
    const subject = document.getElementById('custom-subject-input').value;
    const topic = document.getElementById('custom-topic-input').value;
    const diff = document.getElementById('custom-diff-select').value;
    const btn = document.getElementById('btn-create-topic-submit');

    try {
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Analyzing & Generating...</span>`;
      
      const newTopic = await Api.createOrSelectTopic(subject, topic, diff);
      this.hideCustomTopicModal();
      this.showToast(`Curriculum generated for ${topic}!`, "success");
      await this.startTopicSession(newTopic.id);
    } catch (err) {
      this.showToast("Error creating topic: " + err.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `Generate Curriculum`;
    }
  },

  // ==============================================================
  // FILE UPLOAD CONTROLLER
  // ==============================================================
  handleFileSelected(e) {
    const file = e.target.files[0];
    if (file) {
      this.processFileUpload(file);
    }
  },

  async processFileUpload(file) {
    const statusCard = document.getElementById('upload-status-card');
    const filenameEl = document.getElementById('upload-filename');
    const filesizeEl = document.getElementById('upload-filesize');
    const badgeEl = document.getElementById('upload-badge');
    const progressBar = document.getElementById('upload-progress-bar');
    const previewBox = document.getElementById('upload-concepts-preview');

    statusCard.classList.remove('hidden');
    filenameEl.textContent = file.name;
    filesizeEl.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    badgeEl.textContent = "Validating & Extracting Content...";
    badgeEl.className = "px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200";
    progressBar.style.width = "40%";
    previewBox.classList.add('hidden');

    try {
      const res = await Api.uploadStudyMaterial(file);
      progressBar.style.width = "100%";
      badgeEl.textContent = "AI Analysis Complete ✓";
      badgeEl.className = "px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200";

      // Render concepts preview
      const listEl = document.getElementById('upload-concepts-list');
      listEl.innerHTML = res.concepts.map((c, i) => `
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
          <div class="flex items-center justify-between mb-1">
            <span class="font-bold text-slate-800">Concept ${i+1}: ${c.title}</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-indigo-50 text-indigo-700">${c.difficulty_level}</span>
          </div>
          <p class="text-[11px] text-slate-600 line-clamp-2">${c.simple_explanation}</p>
        </div>
      `).join('');

      previewBox.classList.remove('hidden');
      State.activeSession.uploadedTopicId = res.topic_id;
      this.showToast("Material processed! Ready to begin teaching.", "success");
    } catch (err) {
      badgeEl.textContent = "Validation Failed";
      badgeEl.className = "px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200";
      progressBar.style.width = "0%";
      this.showToast(err.message, "error");
    }
  },

  async uploadSampleText(sampleName) {
    let text = "";
    if (sampleName.includes("operating_systems")) {
      text = `
# Operating Systems Memory Management
## Concept 1: Virtual Memory & Address Translation
Virtual memory abstracts physical RAM away from process view. Each process operates within an isolated 32-bit or 64-bit address space.
The Memory Management Unit (MMU) performs hardware translation between Virtual Page Numbers (VPN) and Physical Frame Numbers (PFN).
Key constraint: The offset inside the page is always identical between virtual and physical addresses because page size equals frame size.

## Concept 2: The Translation Lookaside Buffer (TLB)
A hardware cache located on the CPU storing recent address translations.
When the CPU references a memory location, the MMU checks the TLB first.
TLB hit takes under 1 nanosecond; a TLB miss forces a multi-level page table walk in RAM.

## Concept 3: Page Faults & Replacement Algorithms
A page fault occurs when a requested page is not in physical RAM (Present Bit is 0).
The OS traps to the kernel handler, retrieves the missing page from disk swap, updates the frame table, and restarts the instruction.
When RAM is full, replacement algorithms such as LRU (Least Recently Used) select a victim frame.
`;
    } else {
      text = `
# Machine Learning Foundations
## Concept 1: Supervised vs Unsupervised Learning
Supervised learning trains models on labeled input-output pairs to predict continuous values (regression) or discrete classes (classification).
Unsupervised learning uncovers latent cluster distributions without ground-truth labels.

## Concept 2: Overfitting, Underfitting, and Regularization
Overfitting occurs when a model memorizes training noise rather than generalizable signals.
L1 (Lasso) and L2 (Ridge) regularization add penalty terms to the loss function to constrain model weight complexity.

## Concept 3: Gradient Descent & Loss Optimization
Gradient descent iteratively updates parameters in the direction of steepest negative gradient of the loss surface.
Learning rate controls the step magnitude: too high causes divergence, too low causes slow convergence.
`;
    }

    const blob = new Blob([text], { type: 'text/plain' });
    const file = new File([blob], sampleName, { type: 'text/plain' });
    await this.processFileUpload(file);
  },

  async startSessionFromUpload() {
    if (State.activeSession.uploadedTopicId) {
      await this.startTopicSession(State.activeSession.uploadedTopicId);
    }
  },

  // ==============================================================
  // AI TEACHING ENGINE CONTROLLER
  // ==============================================================
  renderLessonView() {
    const s = State.activeSession;
    if (!s.concept) return;

    const subjectEl = document.getElementById('lesson-subject');
    const stepEl = document.getElementById('lesson-step-indicator');
    const titleEl = document.getElementById('lesson-concept-title');
    const loadBadge = document.getElementById('lesson-load-badge');
    const loadText = document.getElementById('lesson-load-text');
    const simpleExp = document.getElementById('lesson-simple-explanation');
    const importantPts = document.getElementById('lesson-important-points');
    const diagramEl = document.getElementById('lesson-diagram');
    const analogyEl = document.getElementById('lesson-analogy');
    const exampleEl = document.getElementById('lesson-example');
    const takeawayEl = document.getElementById('lesson-takeaway');
    const miscEl = document.getElementById('lesson-misconceptions');
    const bannerMode = document.getElementById('lesson-pedagogical-mode');
    const bannerRationale = document.getElementById('lesson-adaptive-rationale');

    if (subjectEl) subjectEl.textContent = s.subject;
    if (stepEl) stepEl.textContent = `Concept ${s.conceptIndex + 1} of ${s.totalConcepts}`;
    if (titleEl) titleEl.textContent = s.concept.title;

    // Cognitive load pill in lesson
    const load = (s.cognitiveLoad || 'LOW').toUpperCase();
    if (loadBadge && loadText) {
      if (load === 'HIGH') {
        loadBadge.className = 'px-3 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-2 load-badge-high shadow-sm';
        loadText.textContent = 'High Load · Scaffolding Active';
      } else if (load === 'MEDIUM') {
        loadBadge.className = 'px-3 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-2 load-badge-medium shadow-sm';
        loadText.textContent = 'Medium Load · Desirable Difficulty';
      } else {
        loadBadge.className = 'px-3 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-2 load-badge-low shadow-sm';
        loadText.textContent = 'Low Load · Flow State';
      }
    }

    // Adaptive banner
    if (bannerMode) bannerMode.textContent = s.currentTeachingStyle.toUpperCase();
    if (bannerRationale) {
      if (load === 'HIGH') {
        bannerRationale.textContent = "High mental effort detected. Lesson pacing has been slowed down with step-by-step scaffolding and concrete analogies.";
      } else if (load === 'LOW') {
        bannerRationale.textContent = "Sharp comprehension detected. Lesson has accelerated with advanced architecture insights and harder challenges.";
      } else {
        bannerRationale.textContent = "Optimal learning zone. Standard pacing maintained with balanced practice scenarios.";
      }
    }

    if (simpleExp) simpleExp.textContent = s.concept.simple_explanation;

    if (importantPts) {
      importantPts.innerHTML = (s.concept.important_points || []).map(pt => `
        <li class="flex items-start space-x-2">
          <i class="fa-solid fa-circle-check text-indigo-500 mt-1 text-xs"></i>
          <span>${pt}</span>
        </li>
      `).join('');
    }

    if (diagramEl) {
      diagramEl.textContent = s.concept.visual_representation || `
+-------------------------------------------------------------+
|  ${s.concept.title.center(55)}  |
+-------------------------------------------------------------+
       |
       v
  [ Input ] --------> [ MMU / Processing ] --------> [ Execution ]
`;
    }

    if (analogyEl) analogyEl.textContent = `"${s.concept.real_world_analogy || 'A modular filing system with catalog cards.'}"`;
    if (exampleEl) exampleEl.textContent = s.concept.concrete_example || "// Concrete implementation walkthrough";
    if (takeawayEl) takeawayEl.textContent = s.concept.key_takeaway || "Mastering this concept ensures operational correctness.";
    if (miscEl) {
      const misc = (s.concept.misconceptions && s.concept.misconceptions.length > 0) 
        ? s.concept.misconceptions[0] 
        : `Common error: Assuming ${s.concept.title} operates without constraints.`;
      miscEl.textContent = misc;
    }
  },

  exitSessionPrompt() {
    if (confirm("Would you like to save your progress and return to Dashboard?")) {
      this.navigateTo('dashboard');
    }
  },

  // ==============================================================
  // MINI QUIZ CONTROLLER
  // ==============================================================
  startMiniQuiz() {
    const s = State.activeSession;
    if (!s.question) {
      this.showToast("No quiz questions available for this concept. Moving to next.", "warning");
      this.advanceNextStep();
      return;
    }

    State.startQuestionTimer();
    this.startQuizTimer();
    this.renderQuizQuestion();
    this.navigateTo('quiz');
  },

  startQuizTimer() {
    if (this.quizTimerInterval) clearInterval(this.quizTimerInterval);
    const timerEl = document.getElementById('quiz-timer');
    this.quizTimerInterval = setInterval(() => {
      if (timerEl && State.activeSession.questionStartTime) {
        const sec = ((Date.now() - State.activeSession.questionStartTime) / 1000).toFixed(1);
        timerEl.textContent = `${sec}s`;
      }
    }, 100);
  },

  stopQuizTimer() {
    if (this.quizTimerInterval) {
      clearInterval(this.quizTimerInterval);
      this.quizTimerInterval = null;
    }
  },

  renderQuizQuestion() {
    const s = State.activeSession;
    const q = s.question;
    if (!q) return;

    const heading = document.getElementById('quiz-concept-heading');
    const sub = document.getElementById('quiz-topic-sub');
    const diffBadge = document.getElementById('quiz-diff-badge');
    const qText = document.getElementById('quiz-question-text');
    const optionsContainer = document.getElementById('quiz-options-container');
    const submitBtn = document.getElementById('btn-submit-answer');
    const feedbackBox = document.getElementById('quiz-feedback-box');
    const hintsBox = document.getElementById('quiz-hints-box');
    const hintBtn = document.getElementById('hint-button-label');

    if (heading) heading.textContent = `Concept: ${s.concept.title}`;
    if (sub) sub.textContent = s.topicName;
    if (qText) qText.textContent = q.question;

    if (diffBadge) {
      diffBadge.textContent = `${q.difficulty || s.currentDifficulty} Difficulty`;
      if ((q.difficulty || '').toLowerCase() === 'hard') {
        diffBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200';
      } else if ((q.difficulty || '').toLowerCase() === 'easy') {
        diffBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200';
      } else {
        diffBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200';
      }
    }

    if (submitBtn) submitBtn.disabled = true;
    if (feedbackBox) feedbackBox.classList.add('hidden');
    if (hintsBox) {
      hintsBox.innerHTML = '';
      hintsBox.classList.add('hidden');
    }
    if (hintBtn) hintBtn.textContent = 'Request Hint (Tier 1)';

    // Render 4 options
    const optionLetters = ['A', 'B', 'C', 'D'];
    optionsContainer.innerHTML = (q.options || []).map((opt, idx) => `
      <div onclick="App.selectQuizOption(${idx})" id="quiz-opt-${idx}" class="quiz-option-card p-4 rounded-xl flex items-center space-x-3 bg-white">
        <span class="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center flex-shrink-0" id="quiz-opt-badge-${idx}">
          ${optionLetters[idx]}
        </span>
        <span class="text-xs sm:text-sm font-medium text-slate-800">${opt}</span>
      </div>
    `).join('');
  },

  selectQuizOption(index) {
    if (State.activeSession.answered) return;

    State.activeSession.selectedOption = index;
    State.getLatencySeconds(); // record interaction latency

    // Clear previous option styles
    const options = document.querySelectorAll('.quiz-option-card');
    options.forEach((opt, idx) => {
      opt.classList.remove('selected');
      const badge = document.getElementById(`quiz-opt-badge-${idx}`);
      if (badge) {
        badge.classList.remove('bg-indigo-600', 'text-white');
        badge.classList.add('bg-slate-100', 'text-slate-700');
      }
    });

    // Select chosen option
    const chosen = document.getElementById(`quiz-opt-${index}`);
    const badge = document.getElementById(`quiz-opt-badge-${index}`);
    if (chosen) chosen.classList.add('selected');
    if (badge) {
      badge.classList.remove('bg-slate-100', 'text-slate-700');
      badge.classList.add('bg-indigo-600', 'text-white');
    }

    // Enable submit button
    const submitBtn = document.getElementById('btn-submit-answer');
    if (submitBtn) submitBtn.disabled = false;
  },

  async triggerNextHintTier() {
    const s = State.activeSession;
    if (!s.question) return;

    const nextTier = (s.hintTiersUnlocked.length || 0) + 1;
    if (nextTier > 4) {
      this.showToast("All hint tiers and worked examples have been unlocked.", "info");
      return;
    }

    try {
      const hintRes = await Api.requestHint(s.sessionId, s.concept.id, s.question.id, nextTier);
      s.hintTiersUnlocked.push(hintRes);
      s.hintsUsed++;

      // Display in hint box
      const hintsBox = document.getElementById('quiz-hints-box');
      hintsBox.classList.remove('hidden');

      const hintEl = document.createElement('div');
      hintEl.className = 'p-3 bg-amber-50/80 border border-amber-200 rounded-xl text-xs text-amber-950 space-y-1 fade-in';
      hintEl.innerHTML = `
        <div class="flex items-center space-x-1.5 font-bold text-amber-800">
          <i class="fa-solid fa-lightbulb text-amber-500"></i>
          <span>${hintRes.tier_name}</span>
        </div>
        <p class="leading-relaxed pl-5">${hintRes.hint}</p>
      `;
      hintsBox.appendChild(hintEl);

      // Update button label for subsequent tier
      const label = document.getElementById('hint-button-label');
      if (nextTier < 4) {
        label.textContent = `Request Tier ${nextTier + 1} Hint`;
      } else {
        label.textContent = `All Hints Unlocked ✓`;
      }

      this.showToast(`Unlocked ${hintRes.tier_name}`, "info");
    } catch (err) {
      this.showToast("Failed to fetch hint: " + err.message, "error");
    }
  },

  async submitQuizAnswer() {
    const s = State.activeSession;
    if (s.selectedOption === null) return;

    this.stopQuizTimer();
    const responseTime = State.getElapsedSeconds();
    const latency = State.getLatencySeconds();

    const submitBtn = document.getElementById('btn-submit-answer');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Analyzing Response...</span>`;

    try {
      const res = await Api.submitAnswer({
        sessionId: s.sessionId,
        conceptId: s.concept.id,
        questionId: s.question.id,
        selectedOptionIndex: s.selectedOption,
        responseTimeSeconds: responseTime,
        attempts: s.attempts,
        hintsUsed: s.hintsUsed,
        skipped: false,
        timeSinceLastAction: latency
      });

      s.answered = true;
      s.feedback = res;

      // Update Active Cognitive Load and Teaching Style
      s.cognitiveLoad = res.cognitive_load.predicted_load;
      s.currentTeachingStyle = res.adaptation.teaching_style;
      s.currentDifficulty = res.adaptation.next_difficulty;
      this.updateCognitiveLoadBadge(res.cognitive_load.predicted_load);

      // Highlight options
      const chosenCard = document.getElementById(`quiz-opt-${s.selectedOption}`);
      if (res.is_correct) {
        if (chosenCard) chosenCard.classList.add('correct');
      } else {
        if (chosenCard) chosenCard.classList.add('incorrect');
        if (res.correct_index !== null && res.correct_index !== undefined) {
          const correctCard = document.getElementById(`quiz-opt-${res.correct_index}`);
          if (correctCard) correctCard.classList.add('correct');
        }
      }

      // Display Feedback Box
      this.renderFeedbackBox(res);

      // If high load persistent -> suggest break
      if (res.adaptation.break_recommended) {
        document.getElementById('modal-break').classList.remove('hidden');
      }

    } catch (err) {
      this.showToast("Error evaluating answer: " + err.message, "error");
    } finally {
      submitBtn.innerHTML = `<span>Submit Answer</span><i class="fa-solid fa-check"></i>`;
    }
  },

  async skipQuestion() {
    const s = State.activeSession;
    this.stopQuizTimer();
    const responseTime = State.getElapsedSeconds();

    try {
      const res = await Api.submitAnswer({
        sessionId: s.sessionId,
        conceptId: s.concept.id,
        questionId: s.question.id,
        selectedOptionIndex: null,
        responseTimeSeconds: responseTime,
        attempts: s.attempts,
        hintsUsed: s.hintsUsed,
        skipped: true,
        timeSinceLastAction: 1.0
      });

      s.answered = true;
      s.feedback = res;
      this.renderFeedbackBox(res);
    } catch (err) {
      this.showToast("Skip failed: " + err.message, "error");
    }
  },

  renderFeedbackBox(res) {
    const box = document.getElementById('quiz-feedback-box');
    const iconContainer = document.getElementById('feedback-icon-container');
    const title = document.getElementById('feedback-title');
    const msg = document.getElementById('feedback-message');
    const loadBadge = document.getElementById('feedback-load-badge');
    const loadFactors = document.getElementById('feedback-load-factors');
    const adaptText = document.getElementById('feedback-adaptation-text');
    const retryBtn = document.getElementById('btn-quiz-retry');
    const continueBtn = document.getElementById('btn-quiz-continue');

    box.classList.remove('hidden', 'bg-emerald-50', 'border-emerald-200', 'bg-rose-50', 'border-rose-200', 'bg-amber-50', 'border-amber-200');

    if (res.is_correct) {
      box.classList.add('bg-emerald-50', 'border-emerald-200');
      iconContainer.className = 'w-9 h-9 rounded-xl flex items-center justify-center text-white flex-shrink-0 mt-0.5 bg-emerald-500 shadow';
      iconContainer.innerHTML = `<i class="fa-solid fa-check text-sm"></i>`;
      title.className = 'text-sm font-bold text-emerald-900';
    } else {
      box.classList.add('bg-rose-50', 'border-rose-200');
      iconContainer.className = 'w-9 h-9 rounded-xl flex items-center justify-center text-white flex-shrink-0 mt-0.5 bg-rose-500 shadow';
      iconContainer.innerHTML = `<i class="fa-solid fa-xmark text-sm"></i>`;
      title.className = 'text-sm font-bold text-rose-900';
    }

    title.textContent = res.feedback_title;
    msg.textContent = res.feedback_message;

    // Load indicators
    const load = res.cognitive_load.predicted_load.toUpperCase();
    loadBadge.textContent = load;
    if (load === 'HIGH') {
      loadBadge.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-rose-200 text-rose-900';
    } else if (load === 'MEDIUM') {
      loadBadge.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-amber-200 text-amber-900';
    } else {
      loadBadge.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-200 text-emerald-900';
    }

    loadFactors.innerHTML = (res.cognitive_load.contributing_factors || []).map(f => `• ${f}`).join(' ');
    adaptText.textContent = `Adaptive Engine: ${res.adaptation.rationale}`;

    // Retry or continue buttons
    if (res.can_retry) {
      retryBtn.classList.remove('hidden');
    } else {
      retryBtn.classList.add('hidden');
    }

    continueBtn.classList.remove('hidden');
  },

  retryCurrentQuestion() {
    State.activeSession.attempts++;
    State.activeSession.selectedOption = null;
    State.activeSession.answered = false;
    State.startQuestionTimer();
    this.startQuizTimer();

    // Reset styles
    const options = document.querySelectorAll('.quiz-option-card');
    options.forEach((opt, idx) => {
      opt.classList.remove('selected', 'incorrect', 'correct');
      const badge = document.getElementById(`quiz-opt-badge-${idx}`);
      if (badge) {
        badge.classList.remove('bg-indigo-600', 'text-white');
        badge.classList.add('bg-slate-100', 'text-slate-700');
      }
    });

    document.getElementById('quiz-feedback-box').classList.add('hidden');
    document.getElementById('btn-submit-answer').disabled = true;
  },

  async advanceNextStep() {
    const s = State.activeSession;
    try {
      this.showToast("Calibrating next pedagogical step...", "info");
      const res = await Api.nextConcept(s.sessionId);

      if (res.completed) {
        // Topic mastered or finished
        this.renderMasterySummary(res.mastery_result);
        this.navigateTo('mastery-summary');
      } else {
        // Advance to next concept
        s.conceptIndex = res.concept_index;
        s.totalConcepts = res.total_concepts;
        s.concept = res.concept;
        s.question = res.question;
        s.currentDifficulty = res.difficulty;

        this.renderLessonView();
        this.navigateTo('lesson');
      }
    } catch (err) {
      this.showToast("Could not advance: " + err.message, "error");
    }
  },

  // ==============================================================
  // MASTERY SUMMARY CONTROLLER
  // ==============================================================
  renderMasterySummary(result) {
    const title = document.getElementById('mastery-topic-title');
    const sub = document.getElementById('mastery-summary-sub');
    const bigScore = document.getElementById('mastery-big-score');
    const conceptsList = document.getElementById('mastery-concepts-list');
    const reviewList = document.getElementById('mastery-review-list');
    const qCount = document.getElementById('mastery-stat-questions');
    const acc = document.getElementById('mastery-stat-accuracy');
    const timeEl = document.getElementById('mastery-stat-time');
    const hintsEl = document.getElementById('mastery-stat-hints');
    const timeline = document.getElementById('mastery-load-timeline');
    const nextTopicName = document.getElementById('mastery-next-topic-name');

    if (title) title.textContent = result.topic_name;
    if (sub) sub.textContent = result.summary_text;
    if (bigScore) bigScore.textContent = `${Math.round(result.mastery_score)}%`;

    if (conceptsList) {
      conceptsList.innerHTML = (result.concepts_mastered || []).map(c => `
        <li class="flex items-center space-x-2">
          <i class="fa-solid fa-check text-emerald-600"></i>
          <span>${c}</span>
        </li>
      `).join('') || `<li class="text-slate-400">Review weak concepts to unlock full mastery.</li>`;
    }

    if (reviewList) {
      reviewList.innerHTML = (result.concepts_needing_review || []).map(c => `
        <li class="flex items-center space-x-2">
          <i class="fa-solid fa-triangle-exclamation text-amber-500"></i>
          <span>${c}</span>
        </li>
      `).join('') || `<li class="text-emerald-600 font-semibold">Zero weak concepts detected! Flawless run!</li>`;
    }

    if (qCount) qCount.textContent = result.stats.questions_answered;
    if (acc) acc.textContent = `${result.stats.accuracy}%`;
    if (timeEl) timeEl.textContent = `${result.stats.avg_response_time}s`;
    if (hintsEl) hintsEl.textContent = result.stats.hints_used;

    if (timeline) {
      timeline.innerHTML = (result.cognitive_load_trend || []).map((t, idx) => {
        const load = (t.load || 'LOW').toUpperCase();
        const color = load === 'HIGH' ? 'bg-rose-500' : (load === 'MEDIUM' ? 'bg-amber-500' : 'bg-emerald-500');
        return `
          <div class="flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-semibold bg-slate-100 border border-slate-200 flex-shrink-0">
            <span class="w-2 h-2 rounded-full ${color}"></span>
            <span>Q${idx+1}: ${load} (${t.difficulty})</span>
          </div>
        `;
      }).join('');
    }

    if (nextTopicName && result.recommendations && result.recommendations.suggested_next_topic) {
      nextTopicName.textContent = `${result.recommendations.suggested_next_topic.topic} (${result.recommendations.suggested_next_topic.subject})`;
      State.activeSession.suggestedNext = result.recommendations.suggested_next_topic;
    }
  },

  async startRecommendedTopic() {
    const next = State.activeSession.suggestedNext;
    if (next) {
      try {
        const topic = await Api.createOrSelectTopic(next.subject, next.topic);
        await this.startTopicSession(topic.id);
      } catch (err) {
        this.navigateTo('learn-topic');
      }
    } else {
      this.navigateTo('learn-topic');
    }
  },

  // ==============================================================
  // PROGRESS DASHBOARD CONTROLLER
  // ==============================================================
  async loadProgressDashboard() {
    try {
      const data = await Api.getDashboard();
      
      const progMastery = document.getElementById('prog-mastery-rate');
      const progStreak = document.getElementById('prog-streak');
      const progAccuracy = document.getElementById('prog-accuracy');
      const progSpeed = document.getElementById('prog-speed');
      const tableBody = document.getElementById('progress-table-body');

      if (progMastery) progMastery.textContent = `${Math.round(data.overall_progress_percent)}%`;
      if (progStreak) progStreak.textContent = `${data.current_learning_streak} Days`;
      if (progAccuracy) progAccuracy.textContent = `${data.accuracy_percent}%`;
      if (progSpeed) progSpeed.textContent = `${data.avg_response_time_seconds}s`;

      if (tableBody) {
        if (data.topic_mastery_records && data.topic_mastery_records.length > 0) {
          tableBody.innerHTML = data.topic_mastery_records.map(m => `
            <tr class="hover:bg-slate-50 transition">
              <td class="py-3 px-4 font-semibold text-slate-800">
                <p>${m.topic_name}</p>
                <span class="text-[10px] text-slate-400 font-normal uppercase tracking-wider">${m.subject}</span>
              </td>
              <td class="py-3 px-4">
                <span class="font-bold ${m.mastery_score >= 75 ? 'text-emerald-600' : 'text-amber-600'}">${Math.round(m.mastery_score)}%</span>
              </td>
              <td class="py-3 px-4 text-slate-600">
                ${m.mastered_concepts.length > 0 ? m.mastered_concepts.join(', ') : 'In progress'}
              </td>
              <td class="py-3 px-4 text-rose-600 font-medium">
                ${m.weak_concepts.length > 0 ? m.weak_concepts.join(', ') : 'None ✓'}
              </td>
              <td class="py-3 px-4">
                <button onclick="App.startTopicSession(${m.topic_id})" class="px-3 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 rounded-lg text-xs font-semibold transition">
                  Review
                </button>
              </td>
            </tr>
          `).join('');
        } else {
          tableBody.innerHTML = `
            <tr>
              <td colspan="5" class="py-8 text-center text-slate-400 text-xs">
                No learning records found yet. Select a topic to start!
              </td>
            </tr>
          `;
        }
      }
    } catch (err) {
      console.error(err);
    }
  },

  // ==============================================================
  // MODALS & TOASTS
  // ==============================================================
  showCognitiveExplainerModal() {
    const modal = document.getElementById('modal-cognitive-explainer');
    if (modal) modal.classList.remove('hidden');
  },

  hideCognitiveExplainerModal() {
    const modal = document.getElementById('modal-cognitive-explainer');
    if (modal) modal.classList.add('hidden');
  },

  dismissBreakModal() {
    const modal = document.getElementById('modal-break');
    if (modal) modal.classList.add('hidden');
    this.showToast("Great! Ready to continue with fresh focus.", "success");
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const colorClasses = {
      success: 'bg-emerald-600 text-white shadow-emerald-200',
      error: 'bg-rose-600 text-white shadow-rose-200',
      warning: 'bg-amber-600 text-white shadow-amber-200',
      info: 'bg-slate-900 text-white shadow-slate-300'
    }[type] || 'bg-slate-900 text-white';

    toast.className = `p-3.5 px-4 rounded-xl shadow-lg text-xs font-medium flex items-center space-x-2 transition-all duration-300 pointer-events-auto fade-in ${colorClasses}`;
    
    const icon = {
      success: 'fa-circle-check',
      error: 'fa-circle-exclamation',
      warning: 'fa-triangle-exclamation',
      info: 'fa-circle-info'
    }[type] || 'fa-circle-info';

    toast.innerHTML = `<i class="fa-solid ${icon}"></i><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }
};

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
