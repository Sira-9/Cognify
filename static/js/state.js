/**
 * Cognify - Reactive Application State
 */

const State = {
  user: null,
  currentView: 'dashboard',
  dashboardData: null,
  curatedTopics: [],
  
  // Active Learning Session State
  activeSession: {
    sessionId: null,
    topicId: null,
    topicName: '',
    subject: '',
    conceptIndex: 0,
    totalConcepts: 0,
    concept: null,
    question: null,
    currentDifficulty: 'Medium',
    currentTeachingStyle: 'Standard',
    cognitiveLoad: 'BALANCED',
    consecutiveHighLoad: 0,

    // Behavior Tracking Signals
    questionStartTime: null,
    lastInteractionTime: null,
    attempts: 1,
    hintsUsed: 0,
    hintTiersUnlocked: [],
    selectedOption: null,
    answered: false,
    feedback: null
  },

  resetSession() {
    this.activeSession = {
      sessionId: null,
      topicId: null,
      topicName: '',
      subject: '',
      conceptIndex: 0,
      totalConcepts: 0,
      concept: null,
      question: null,
      currentDifficulty: 'Medium',
      currentTeachingStyle: 'Standard',
      cognitiveLoad: 'BALANCED',
      consecutiveHighLoad: 0,
      questionStartTime: null,
      lastInteractionTime: null,
      attempts: 1,
      hintsUsed: 0,
      hintTiersUnlocked: [],
      selectedOption: null,
      answered: false,
      feedback: null
    };
  },

  startQuestionTimer() {
    this.activeSession.questionStartTime = Date.now();
    this.activeSession.lastInteractionTime = Date.now();
    this.activeSession.attempts = 1;
    this.activeSession.hintsUsed = 0;
    this.activeSession.hintTiersUnlocked = [];
    this.activeSession.selectedOption = null;
    this.activeSession.answered = false;
    this.activeSession.feedback = null;
  },

  getElapsedSeconds() {
    if (!this.activeSession.questionStartTime) return 5.0;
    const elapsed = (Date.now() - this.activeSession.questionStartTime) / 1000.0;
    return Math.max(1.0, Math.round(elapsed * 10) / 10);
  },

  getLatencySeconds() {
    if (!this.activeSession.lastInteractionTime) return 1.0;
    const latency = (Date.now() - this.activeSession.lastInteractionTime) / 1000.0;
    this.activeSession.lastInteractionTime = Date.now();
    return Math.max(0.5, Math.round(latency * 10) / 10);
  }
};
