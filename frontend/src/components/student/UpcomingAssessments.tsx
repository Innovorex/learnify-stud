import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Calendar, Clock, BookOpen } from 'lucide-react';
import { studentAPI } from '../../services/api';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export function UpcomingAssessments() {
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      // Assuming student has a class_name property, default to '10A' for now
      const className = user.class_name || '10A';

      const response = await studentAPI.getAssessments(className);
      setAssessments(response.data);
      setLoading(false);
    } catch (error: any) {
      toast.error('Failed to load assessments');
      setLoading(false);
    }
  };

  const getAssessmentStatus = (startTime: string, endTime: string) => {
    const now = new Date();
    const start = new Date(startTime);
    const end = new Date(endTime);

    if (now >= start && now <= end) {
      return 'Available';
    } else if (now < start) {
      return 'Scheduled';
    } else {
      return 'Expired';
    }
  };

  const handleStartExam = (assessmentId: number) => {
    navigate(`/student/exam/${assessmentId}`);
  };

  const formatDateTime = (datetime: string) => {
    const date = new Date(datetime);
    return {
      date: date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading assessments...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1>Upcoming Assessments</h1>
        <p className="text-muted-foreground">View all your scheduled assessments</p>
      </div>

      {assessments.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">No upcoming assessments at the moment</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {assessments.map((assessment: any) => {
            const status = getAssessmentStatus(assessment.start_time, assessment.end_time);
            const startDateTime = formatDateTime(assessment.start_time);

            return (
              <Card key={assessment.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{assessment.subject}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">{assessment.chapter}</p>
                    </div>
                    <Badge
                      variant={status === 'Available' ? 'default' : 'secondary'}
                      className={
                        status === 'Available'
                          ? 'bg-[#43A047] hover:bg-[#43A047]/90'
                          : ''
                      }
                    >
                      {status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>{startDateTime.date}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>
                        {startDateTime.time} • {assessment.duration_minutes} minutes
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <BookOpen className="h-4 w-4 text-muted-foreground" />
                      <span>ID: AS{assessment.id.toString().padStart(3, '0')}</span>
                    </div>
                  </div>

                  <Button
                    className="w-full bg-[#1E88E5] hover:bg-[#1565C0]"
                    disabled={status !== 'Available'}
                    onClick={() => handleStartExam(assessment.id)}
                  >
                    {status === 'Available' ? 'Start Now' : 'Not Available Yet'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
