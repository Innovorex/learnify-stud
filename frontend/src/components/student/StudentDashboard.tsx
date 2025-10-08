import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Calendar, Clock, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { studentAPI } from '../../services/api';
import { toast } from 'sonner';

export function StudentDashboard() {
  const [timeRemaining, setTimeRemaining] = useState('');
  const [nextExam, setNextExam] = useState<any>(null);
  const [upcomingCount, setUpcomingCount] = useState(0);
  const [completedCount, setCompletedCount] = useState(0);
  const [averageScore, setAverageScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (!nextExam?.start_time) return;

    const timer = setInterval(() => {
      const now = new Date();
      const startTime = new Date(nextExam.start_time);
      const endTime = new Date(nextExam.end_time);
      const diff = startTime.getTime() - now.getTime();

      if (now >= startTime && now <= endTime) {
        setTimeRemaining('Available Now!');
      } else if (diff > 0) {
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeRemaining(`${hours}h ${minutes}m ${seconds}s`);
      } else {
        setTimeRemaining('Exam Ended');
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [nextExam]);

  const fetchDashboardData = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const className = user.class_name || '10A';

      // Fetch upcoming assessments
      const assessmentsRes = await studentAPI.getAssessments(className);
      const assessments = assessmentsRes.data;
      setUpcomingCount(assessments.length);

      // Find the closest upcoming exam
      const now = new Date();
      const upcoming = assessments
        .filter((a: any) => new Date(a.end_time) > now)
        .sort((a: any, b: any) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

      if (upcoming.length > 0) {
        setNextExam(upcoming[0]);
      }

      // Fetch student results
      const resultsRes = await studentAPI.getMyResults(user.id);
      const results = resultsRes.data;
      setCompletedCount(results.length);

      if (results.length > 0) {
        const avg = Math.round(
          results.reduce((acc: number, r: any) => acc + (r.score / r.total) * 100, 0) / results.length
        );
        setAverageScore(avg);
      }

      setLoading(false);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading dashboard...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1>Dashboard</h1>
        <p className="text-muted-foreground">Your upcoming assessments and performance</p>
      </div>

      {/* Next Exam Card */}
      {nextExam ? (
        <Card className="border-[#1E88E5]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-[#1E88E5]" />
              Next Assessment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Subject</p>
                <p className="text-lg">{nextExam.subject}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Chapter</p>
                <p className="text-lg">{nextExam.chapter}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Date & Time</p>
                <p className="text-lg">
                  {formatDate(nextExam.start_time)} at {formatTime(nextExam.start_time)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Duration</p>
                <p className="text-lg">{nextExam.duration_minutes} minutes</p>
              </div>
            </div>

            {/* Countdown Timer */}
            <div className="bg-[#F7F9FC] p-6 rounded-lg text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Clock className="h-5 w-5 text-[#1E88E5]" />
                <p className="text-sm text-muted-foreground">Time Remaining</p>
              </div>
              <p className="text-3xl text-[#1E88E5] mb-4">{timeRemaining}</p>
              <Button
                onClick={() => navigate(`/student/exam/${nextExam.id}`)}
                disabled={timeRemaining !== 'Available Now!'}
                className="bg-[#1E88E5] hover:bg-[#1565C0]"
              >
                {timeRemaining === 'Available Now!' ? 'Start Exam' :
                 timeRemaining === 'Exam Ended' ? 'Exam Ended' : 'Exam Not Started'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">No upcoming exams at the moment</p>
          </CardContent>
        </Card>
      )}

      {/* Exam Guidelines */}
      <Card>
        <CardHeader>
          <CardTitle>Exam Guidelines</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Important Instructions</AlertTitle>
            <AlertDescription>
              <ul className="list-disc list-inside space-y-1 mt-2">
                <li>Ensure you have a stable internet connection</li>
                <li>You can navigate between questions using Next/Previous buttons</li>
                <li>Your answers are saved automatically</li>
                <li>Once submitted, you cannot modify your answers</li>
                <li>Do not refresh the page during the exam</li>
                <li>The exam will auto-submit when time expires</li>
              </ul>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-3xl text-[#1E88E5] mb-2">{upcomingCount}</p>
            <p className="text-sm text-muted-foreground">Upcoming Exams</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-3xl text-[#43A047] mb-2">{averageScore}%</p>
            <p className="text-sm text-muted-foreground">Average Score</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-3xl text-purple-500 mb-2">{completedCount}</p>
            <p className="text-sm text-muted-foreground">Completed</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
