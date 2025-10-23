import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { ClipboardList, Clock, TrendingUp, Users } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { teacherAPI } from '../../services/api';
import { toast } from 'sonner';

interface Assessment {
  id: number;
  class_name: string;
  section: string;
  subject: string;
  chapter: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
}

interface SummaryItem {
  assessment_id: number;
  subject: string;
  chapter: string;
  average_score: number;
  top_score: number;
}

export function TeacherDashboard() {
  const [loading, setLoading] = useState(true);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [summary, setSummary] = useState<SummaryItem[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const user = localStorage.getItem('user');
      if (!user) {
        toast.error('User not found. Please login again.');
        return;
      }
      const teacherId = JSON.parse(user).id;

      const [assessmentsRes, summaryRes] = await Promise.all([
        teacherAPI.getMyAssessments(teacherId),
        teacherAPI.getTeacherSummary(teacherId),
      ]);

      setAssessments(assessmentsRes.data);
      setSummary(summaryRes.data);
    } catch (error: any) {
      console.error('Error fetching dashboard data:', error);
      toast.error(error.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const totalAssessments = assessments.length;
    const now = new Date();
    const pendingExams = assessments.filter(a => new Date(a.start_time) > now).length;
    const averageScore = summary.length > 0
      ? Math.round(summary.reduce((acc, s) => acc + s.average_score, 0) / summary.length)
      : 0;
    const studentsParticipated = summary.reduce((acc, s) => acc + 1, 0);

    return [
      { label: 'Total Assessments', value: totalAssessments.toString(), icon: ClipboardList, color: 'text-[#1E88E5]' },
      { label: 'Pending Exams', value: pendingExams.toString(), icon: Clock, color: 'text-orange-500' },
      { label: 'Average Score', value: `${averageScore}%`, icon: TrendingUp, color: 'text-[#43A047]' },
      { label: 'Students Participated', value: studentsParticipated.toString(), icon: Users, color: 'text-purple-500' },
    ];
  };

  const getRecentActivity = () => {
    return assessments.slice(0, 4).map(assessment => {
      const now = new Date();
      const startTime = new Date(assessment.start_time);
      const endTime = new Date(assessment.end_time);

      let status: 'Scheduled' | 'Completed' | 'In Progress';
      if (now < startTime) {
        status = 'Scheduled';
      } else if (now > endTime) {
        status = 'Completed';
      } else {
        status = 'In Progress';
      }

      return {
        id: `AS${assessment.id.toString().padStart(3, '0')}`,
        className: assessment.class_name,
        section: assessment.section,
        subject: assessment.subject,
        chapter: assessment.chapter,
        startTime: new Date(assessment.start_time).toLocaleString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true,
        }),
        status,
      };
    });
  };

  const stats = calculateStats();
  const recentActivity = getRecentActivity();

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1>Dashboard</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1>Dashboard</h1>
        <p className="text-muted-foreground">Overview of your assessment activities</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                    <h3 className="text-3xl">{stat.value}</h3>
                  </div>
                  <div className={`p-3 bg-muted rounded-lg ${stat.color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {recentActivity.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No assessments found</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Class</TableHead>
                  <TableHead>Section</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Chapter</TableHead>
                  <TableHead>Start Time</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentActivity.map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell>{activity.id}</TableCell>
                    <TableCell>{activity.className}</TableCell>
                    <TableCell>{activity.section}</TableCell>
                    <TableCell>{activity.subject}</TableCell>
                    <TableCell>{activity.chapter}</TableCell>
                    <TableCell>{activity.startTime}</TableCell>
                    <TableCell>
                      <Badge
                        variant={activity.status === 'Completed' ? 'secondary' : 'default'}
                        className={
                          activity.status === 'Completed'
                            ? 'bg-[#43A047] hover:bg-[#43A047]/90'
                            : 'bg-[#1E88E5] hover:bg-[#1E88E5]/90'
                        }
                      >
                        {activity.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}