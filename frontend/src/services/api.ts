import axios from 'axios';

// Use the configured API URL or fallback to localhost
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;

    // If accessing via the production domain, use the HTTPS backend
    if (hostname === 'learnifystudent.innovorex.co.in') {
      return 'https://lsbackend.innovorex.co.in';
    }

    // For localhost or other development environments
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:3003';
    }

    // For IP-based access, use HTTP with port 3003
    return `http://${hostname}:3003`;
  }
  return 'http://localhost:3003';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data: { name: string; email: string; password: string; role: string; class_name?: string; section?: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
};

export const studentAPI = {
  getAssessments: (className: string, section: string) =>
    api.get(`/student/assessments/${className}/${section}`),
  getAssessmentsWithStatus: (studentId: number, className: string, section: string) =>
    api.get(`/student/assessments-with-status/${studentId}/${className}/${section}`),
  getQuestions: (assessmentId: number) =>
    api.get(`/student/assessment/${assessmentId}/questions`),
  submitExam: (data: { student_id: number; assessment_id: number; answers: Record<number, string> }) =>
    api.post('/student/submit-exam', data),
  getMyResults: (studentId: number) =>
    api.get(`/student/my-results/${studentId}`),
};

export const teacherAPI = {
  createAssessment: (data: any) =>
    api.post('/teacher/create-assessment', data),
  getMyAssessments: (teacherId: number) =>
    api.get(`/teacher/my-assessments/${teacherId}`),
  getAssessmentResults: (assessmentId: number) =>
    api.get(`/teacher/results/${assessmentId}`),
  getTeacherSummary: (teacherId: number) =>
    api.get(`/teacher/summary/${teacherId}`),
  getAssessmentQuestions: (assessmentId: number) =>
    api.get(`/teacher/assessment/${assessmentId}/questions`),
};

export default api;
