import axios from 'axios';

const API_BASE_URL = 'http://localhost:3003';

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
  register: (data: { name: string; email: string; password: string; role: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
};

export const studentAPI = {
  getAssessments: (className: string) =>
    api.get(`/student/assessments/${className}`),
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
    api.get(`/student/assessment/${assessmentId}/questions`),
};

export default api;
