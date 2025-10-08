import { useState } from 'react';
import { Bell, LayoutDashboard, Calendar, Trophy, LogOut } from 'lucide-react';
import { User } from '../App';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { StudentDashboard } from './student/StudentDashboard';
import { UpcomingAssessments } from './student/UpcomingAssessments';
import { MyResults } from './student/MyResults';

interface StudentLayoutProps {
  user: User;
  onLogout: () => void;
}

type StudentPage = 'dashboard' | 'upcoming' | 'results';

export function StudentLayout({ user, onLogout }: StudentLayoutProps) {
  const [currentPage, setCurrentPage] = useState<StudentPage>('dashboard');

  const navigation = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upcoming', label: 'Upcoming Assessments', icon: Calendar },
    { id: 'results', label: 'My Results', icon: Trophy },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <StudentDashboard />;
      case 'upcoming':
        return <UpcomingAssessments />;
      case 'results':
        return <MyResults />;
      default:
        return <StudentDashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-6 border-b border-border">
          <h1 className="text-xl">AI Assessment</h1>
          <p className="text-sm text-muted-foreground">Student Portal</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id as StudentPage)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${
                  currentPage === item.id
                    ? 'bg-[#1E88E5] text-white'
                    : 'text-foreground hover:bg-muted'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
          <div>
            <h2 className="text-lg">Welcome, {user.name}</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-[#E53935] rounded-full" />
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2">
                  <Avatar>
                    <AvatarFallback className="bg-[#1E88E5] text-white">
                      {user.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={onLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}