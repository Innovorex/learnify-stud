import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { GraduationCap, BookOpen, Brain } from 'lucide-react';
import { User } from '../App';
import { toast } from 'sonner';
import { authAPI } from '../services/api';

interface LoginSignupProps {
  onLogin: (user: User) => void;
}

export function LoginSignup({ onLogin }: LoginSignupProps) {
  const [activeTab, setActiveTab] = useState('login');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupRole, setSignupRole] = useState<'teacher' | 'student'>('student');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginEmail || !loginPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const response = await authAPI.login({ email: loginEmail, password: loginPassword });
      const { access_token, user } = response.data;

      // Store token in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      const loggedInUser: User = {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      };

      toast.success('Login successful!');
      onLogin(loggedInUser);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signupName || !signupEmail || !signupPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      await authAPI.register({
        name: signupName,
        email: signupEmail,
        password: signupPassword,
        role: signupRole
      });

      toast.success('Account created successfully! Please login.');

      // Reset signup form
      setSignupName('');
      setSignupEmail('');
      setSignupPassword('');
      setSignupRole('student');

      // Switch to login tab
      setActiveTab('login');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Illustration/Banner */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#1E88E5] to-[#1565C0] p-12 flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-8">
            <Brain className="h-8 w-8 text-white" />
            <span className="text-white text-2xl font-semibold">AI Assessment Platform</span>
          </div>
          
          <div className="mt-16 space-y-8">
            <div className="flex items-start gap-4">
              <div className="bg-white/20 p-3 rounded-lg">
                <GraduationCap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-white text-xl mb-2">AI-Powered Questions</h3>
                <p className="text-blue-100">
                  Generate intelligent assessments automatically using advanced AI technology
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="bg-white/20 p-3 rounded-lg">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-white text-xl mb-2">Smart Analytics</h3>
                <p className="text-blue-100">
                  Track student performance with detailed insights and reports
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="text-blue-100">
          <p>Empowering education through intelligent assessment</p>
        </div>
      </div>

      {/* Right side - Login/Signup Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="text-center mb-8 lg:hidden">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Brain className="h-8 w-8 text-[#1E88E5]" />
              <span className="text-2xl font-semibold">AI Assessment</span>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <Card>
                <CardHeader>
                  <CardTitle>Welcome Back</CardTitle>
                  <CardDescription>
                    Enter your credentials to access your account
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="login-email">Email</Label>
                      <Input
                        id="login-email"
                        type="email"
                        placeholder="name@example.com"
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        className="bg-input-background"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="login-password">Password</Label>
                      <Input
                        id="login-password"
                        type="password"
                        placeholder="Enter your password"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        className="bg-input-background"
                      />
                    </div>
                    <Button type="submit" className="w-full">
                      Sign In
                    </Button>
                    <button
                      type="button"
                      className="w-full text-sm text-[#1E88E5] hover:underline"
                    >
                      Forgot Password?
                    </button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="signup">
              <Card>
                <CardHeader>
                  <CardTitle>Create Account</CardTitle>
                  <CardDescription>
                    Sign up to get started with AI Assessment
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSignup} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="signup-name">Full Name</Label>
                      <Input
                        id="signup-name"
                        type="text"
                        placeholder="Enter your name"
                        value={signupName}
                        onChange={(e) => setSignupName(e.target.value)}
                        className="bg-input-background"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signup-email">Email</Label>
                      <Input
                        id="signup-email"
                        type="email"
                        placeholder="name@example.com"
                        value={signupEmail}
                        onChange={(e) => setSignupEmail(e.target.value)}
                        className="bg-input-background"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signup-password">Password</Label>
                      <Input
                        id="signup-password"
                        type="password"
                        placeholder="Create a password"
                        value={signupPassword}
                        onChange={(e) => setSignupPassword(e.target.value)}
                        className="bg-input-background"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="role">Role</Label>
                      <Select value={signupRole} onValueChange={(value) => setSignupRole(value as 'teacher' | 'student')}>
                        <SelectTrigger id="role" className="bg-input-background">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="student">Student</SelectItem>
                          <SelectItem value="teacher">Teacher</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button type="submit" className="w-full">
                      Sign Up
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <footer className="text-center mt-8 text-sm text-muted-foreground">
            AI Assessment Platform © 2025
          </footer>
        </div>
      </div>
    </div>
  );
}