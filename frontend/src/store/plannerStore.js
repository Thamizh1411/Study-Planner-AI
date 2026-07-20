import { create } from 'zustand';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Setup axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add request interceptor to inject auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const usePlannerStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user')) || null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,
  
  // Dashboard & Exam State
  exam: null,
  subjects_count: 0,
  completion_rate: 0,
  active_streak: 0,
  average_quiz_score: 0,
  weak_topics: [],
  today_plan: [],
  schedule: {},
  analysis: null,
  motivation: null,
  
  // Progress logs for charts
  progressLogs: [],
  
  // Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  signup: async (name, email, password) => {
    set({ loading: true, error: null });
    try {
      await api.post('/auth/signup', { name, email, password });
      set({ loading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Signup failed', loading: false });
      return false;
    }
  },
  
  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      set({ 
        token: access_token, 
        user, 
        isAuthenticated: true, 
        loading: false 
      });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Login failed', loading: false });
      return false;
    }
  },

  loginGoogleMock: async (name, email) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/auth/google', { name, email, password: 'google-oauth-dummy-pass' });
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      set({ 
        token: access_token, 
        user, 
        isAuthenticated: true, 
        loading: false 
      });
      return true;
    } catch {
      set({ error: 'Google Login failed', loading: false });
      return false;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ 
      token: null, 
      user: null, 
      isAuthenticated: false,
      exam: null,
      schedule: {},
      today_plan: [],
      analysis: null,
      motivation: null
    });
  },
  
  fetchDashboard: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/progress/dashboard');
      const { exam, completion_rate, active_streak, average_quiz_score, weak_topics, today_plan, schedule, analysis, motivation } = response.data;
      
      set({
        exam,
        completion_rate,
        active_streak,
        average_quiz_score,
        weak_topics,
        today_plan,
        schedule,
        analysis,
        motivation,
        loading: false
      });
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to fetch dashboard data', loading: false });
    }
  },
  
  createExam: async (examData) => {
    set({ loading: true, error: null });
    try {
      await api.post('/exams', examData);
      await get().fetchDashboard();
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to create exam details', loading: false });
      return false;
    }
  },

  deleteExam: async (examId) => {
    set({ loading: true, error: null });
    try {
      await api.delete(`/exams/${examId}`);
      set({ exam: null, schedule: {}, today_plan: [], analysis: null, motivation: null, loading: false });
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to delete exam', loading: false });
      return false;
    }
  },
  
  generateAIPlan: async (examId) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post(`/ai/generate-plan/${examId}`);
      const { schedule, analysis, motivation } = response.data;
      set({
        schedule,
        analysis,
        motivation,
        loading: false
      });
      await get().fetchDashboard();
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'AI Plan generation failed', loading: false });
      return false;
    }
  },
  
  submitQuizScore: async (topicId, score) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/progress/quiz/submit', { topic_id: topicId, score });
      const { rebalanced_schedule, analysis } = response.data;
      if (rebalanced_schedule) {
        set({ schedule: rebalanced_schedule });
      }
      if (analysis) {
        set({ analysis });
      }
      set({ loading: false });
      await get().fetchDashboard();
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to submit quiz score', loading: false });
      return false;
    }
  },
  
  logStudyHours: async (hours) => {
    set({ loading: true, error: null });
    try {
      await api.post('/progress/progress/log-study', { hours });
      set({ loading: false });
      await get().fetchDashboard();
      return true;
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to log study hours', loading: false });
      return false;
    }
  },
  
  fetchProgressLogs: async () => {
    try {
      const response = await api.get('/progress/progress');
      set({ progressLogs: response.data });
    } catch (err) {
      console.error('Failed to fetch progress logs', err);
    }
  }
}));

export { api };
