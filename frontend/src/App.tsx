import { useState, useEffect } from 'react';
import { LoginSignup } from './components/LoginSignup';
import { TeacherLayout } from './components/TeacherLayout';
import { StudentLayout } from './components/StudentLayout';
import { Toaster } from './components/ui/sonner';

export type UserRole = 'teacher' | 'student' | null;

export interface User {
  id: number;
  name: string;
  email: string;
  role: 'teacher' | 'student';
  class_name?: string;
  section?: string;
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);

  // Check for existing session
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        // Check if user has id field (to handle old localStorage data)
        if (parsedUser.id) {
          setUser(parsedUser);
        } else {
          // Clear old invalid user data
          localStorage.removeItem('user');
          localStorage.removeItem('token');
        }
      } catch (error) {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
  }, []);

  const handleLogin = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (!user) {
    return (
      <>
        <LoginSignup onLogin={handleLogin} />
        <Toaster />
      </>
    );
  }

  return (
    <>
      {user.role === 'teacher' ? (
        <TeacherLayout user={user} onLogout={handleLogout} />
      ) : (
        <StudentLayout user={user} onLogout={handleLogout} />
      )}
      <Toaster />
    </>
  );
}