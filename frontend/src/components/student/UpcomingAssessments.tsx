import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Calendar, Clock, BookOpen } from 'lucide-react';
import { studentAPI } from '../../services/api';
import { toast } from 'sonner';

interface UpcomingAssessmentsProps {
  onStartExam?: (assessmentId: number) => void;
}

export function UpcomingAssessments({ onStartExam }: UpcomingAssessmentsProps) {
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const studentId = user.id;
      const className = user.class_name;
      const section = user.section;

      if (!className || !section) {
        toast.error('Class and section information not found. Please contact administrator.');
        setLoading(false);
        return;
      }

      if (!studentId) {
        toast.error('Student ID not found. Please login again.');
        setLoading(false);
        return;
      }

      const response = await studentAPI.getAssessmentsWithStatus(studentId, className, section);
      setAssessments(response.data);
      setLoading(false);
    } catch (error: any) {
      toast.error('Failed to load assessments');
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'available':
        return 'badge-gradient-available';
      case 'completed':
        return 'badge-gradient-completed';
      case 'scheduled':
        return 'badge-gradient-scheduled';
      case 'missed':
        return 'badge-gradient-missed';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available':
        return 'Available Now';
      case 'completed':
        return 'Completed';
      case 'scheduled':
        return 'Scheduled';
      case 'missed':
        return 'Missed';
      default:
        return status;
    }
  };

  const handleStartExam = (assessmentId: number) => {
    if (onStartExam) {
      onStartExam(assessmentId);
    }
  };

  const handleViewResult = () => {
    // Results will be shown in the My Results page
    toast.info('Navigate to My Results to see detailed results');
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
        <h1>My Assessments</h1>
        <p className="text-muted-foreground">View all your assessments - available, scheduled, completed, and missed</p>
      </div>

      {assessments.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">No assessments found for your class</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {assessments.map((assessment: any) => {
            const startDateTime = formatDateTime(assessment.start_time);
            const endDateTime = formatDateTime(assessment.end_time);
            const status = assessment.status;

            return (
              <Card key={assessment.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{assessment.subject}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">{assessment.chapter}</p>
                    </div>
                    <div className={getStatusBadgeClass(status)}>
                      {getStatusLabel(status)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>Start: {startDateTime.date} at {startDateTime.time}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>End: {endDateTime.date} at {endDateTime.time}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>Duration: {assessment.duration_minutes} minutes</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <BookOpen className="h-4 w-4 text-muted-foreground" />
                      <span>ID: AS{assessment.id.toString().padStart(3, '0')}</span>
                    </div>
                    {status === 'completed' && assessment.score !== null && (
                      <div className="flex items-center gap-2 text-sm font-semibold text-[#1E88E5]">
                        <span>Score: {assessment.score}/{assessment.total_questions}</span>
                      </div>
                    )}
                  </div>

                  {status === 'available' && (
                    <Button
                      variant="gradient"
                      className="w-full font-semibold"
                      onClick={() => handleStartExam(assessment.id)}
                    >
                      Start Now
                    </Button>
                  )}
                  {status === 'completed' && (
                    <Button
                      variant="default"
                      className="w-full"
                      onClick={handleViewResult}
                    >
                      View Result
                    </Button>
                  )}
                  {status === 'scheduled' && (
                    <Button
                      className="w-full cursor-default font-semibold"
                      style={{ backgroundColor: '#FFF3E0', color: '#F57C00' }}
                      disabled
                    >
                      Starts {startDateTime.time}
                    </Button>
                  )}
                  {status === 'missed' && (
                    <Button
                      className="w-full cursor-default font-semibold"
                      style={{ backgroundColor: '#FFEBEE', color: '#C62828' }}
                      disabled
                    >
                      Expired
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
