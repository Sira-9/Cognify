/**
 * Cognify - API Client Layer
 */

const API_BASE = '/api';

const Api = {
  getToken() {
    return localStorage.getItem('cognify_token') || localStorage.getItem('adaptive_learn_token') || '';
  },

  setToken(token) {
    if (token) {
      localStorage.setItem('cognify_token', token);
    } else {
      localStorage.removeItem('cognify_token');
      localStorage.removeItem('adaptive_learn_token');
    }
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const token = this.getToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    // If uploading FormData, delete Content-Type to let browser set boundary
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Clear invalid token
        this.setToken(null);
        if (!endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
          window.dispatchEvent(new CustomEvent('auth:expired'));
        }
      }

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
      }
      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async register(name, email, password) {
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
    if (res.token) this.setToken(res.token);
    return res;
  },

  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (res.token) this.setToken(res.token);
    return res;
  },

  async getMe() {
    return await this.request('/auth/me');
  },

  logout() {
    this.setToken(null);
  },

  // Dashboard & Metrics
  async getDashboard() {
    return await this.request('/dashboard');
  },

  // Topics & Curriculums
  async getCuratedTopics() {
    return await this.request('/topics/curated');
  },

  async createOrSelectTopic(subject, topicName, difficultyPreference = "Intermediate") {
    return await this.request('/topics/create-or-select', {
      method: 'POST',
      body: JSON.stringify({
        subject,
        topic_name: topicName,
        difficulty_preference: difficultyPreference
      })
    });
  },

  // File Upload
  async uploadStudyMaterial(file) {
    const formData = new FormData();
    formData.append('file', file);
    return await this.request('/materials/upload', {
      method: 'POST',
      body: formData
    });
  },

  // Learning Engine Sessions
  async startLearningSession(topicId) {
    return await this.request('/learning/start', {
      method: 'POST',
      body: JSON.stringify({ topic_id: topicId })
    });
  },

  async requestHint(sessionId, conceptId, questionId, hintTier) {
    return await this.request('/learning/hint', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        concept_id: conceptId,
        question_id: questionId,
        hint_tier: hintTier
      })
    });
  },

  async submitAnswer({
    sessionId,
    conceptId,
    questionId,
    selectedOptionIndex,
    responseTimeSeconds,
    attempts,
    hintsUsed,
    skipped = false,
    timeSinceLastAction = 0.0
  }) {
    return await this.request('/learning/answer', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        concept_id: conceptId,
        question_id: questionId,
        selected_option_index: selectedOptionIndex,
        response_time_seconds: responseTimeSeconds,
        attempts: attempts,
        hints_used: hintsUsed,
        skipped: skipped,
        time_since_last_action: timeSinceLastAction
      })
    });
  },

  async nextConcept(sessionId) {
    return await this.request('/learning/next-concept', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId })
    });
  },

  async checkMastery(sessionId) {
    return await this.request('/learning/check-mastery', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId })
    });
  }
};
