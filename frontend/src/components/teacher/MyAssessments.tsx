import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Eye, BarChart3 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
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

interface Question {
  id: number;
  question: string;
  options: { [key: string]: string };
  correct_answer: string;
  difficulty: string;
}

export function MyAssessments() {
  const [loading, setLoading] = useState(true);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);
  const [showQuestionsDialog, setShowQuestionsDialog] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const user = localStorage.getItem('user');
      if (!user) {
        toast.error('User not found. Please login again.');
        return;
      }
      const teacherId = JSON.parse(user).id;

      const response = await teacherAPI.getMyAssessments(teacherId);
      setAssessments(response.data);
    } catch (error: any) {
      console.error('Error fetching assessments:', error);
      toast.error(error.response?.data?.detail || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestions = async (assessmentId: number) => {
    try {
      setLoadingQuestions(true);
      const response = await teacherAPI.getAssessmentQuestions(assessmentId);
      setQuestions(response.data);
    } catch (error: any) {
      console.error('Error fetching questions:', error);
      toast.error(error.response?.data?.detail || 'Failed to load questions');
      setQuestions([]);
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleViewQuestions = (assessment: Assessment) => {
    setSelectedAssessment(assessment);
    setShowQuestionsDialog(true);
    fetchQuestions(assessment.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'bg-[#43A047] hover:bg-[#43A047]/90';
      case 'Scheduled':
        return 'bg-[#1E88E5] hover:bg-[#1E88E5]/90';
      case 'In Progress':
        return 'bg-orange-500 hover:bg-orange-500/90';
      default:
        return '';
    }
  };

  const getAssessmentStatus = (assessment: Assessment): 'Scheduled' | 'Completed' | 'In Progress' => {
    const now = new Date();
    const startTime = new Date(assessment.start_time);
    const endTime = new Date(assessment.end_time);

    if (now < startTime) {
      return 'Scheduled';
    } else if (now > endTime) {
      return 'Completed';
    } else {
      return 'In Progress';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1>My Assessments</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1>My Assessments</h1>
        <p className="text-muted-foreground">View and manage all your assessments</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Assessments</CardTitle>
        </CardHeader>
        <CardContent>
          {assessments.length === 0 ? (
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
                  <TableHead>End Time</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assessments.map((assessment) => {
                  const status = getAssessmentStatus(assessment);
                  return (
                    <TableRow key={assessment.id}>
                      <TableCell>AS{assessment.id.toString().padStart(3, '0')}</TableCell>
                      <TableCell>{assessment.class_name}</TableCell>
                      <TableCell>{assessment.section}</TableCell>
                      <TableCell>{assessment.subject}</TableCell>
                      <TableCell>{assessment.chapter}</TableCell>
                      <TableCell>
                        {new Date(assessment.start_time).toLocaleString('en-US', {
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                          hour12: true,
                        })}
                      </TableCell>
                      <TableCell>
                        {new Date(assessment.end_time).toLocaleString('en-US', {
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                          hour12: true,
                        })}
                      </TableCell>
                      <TableCell>{assessment.duration_minutes} min</TableCell>
                      <TableCell>
                        <Badge variant="default" className={getStatusColor(status)}>
                          {status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewQuestions(assessment)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            Questions
                          </Button>
                          <Button variant="outline" size="sm">
                            <BarChart3 className="h-4 w-4 mr-1" />
                            Results
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={showQuestionsDialog} onOpenChange={setShowQuestionsDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Assessment Questions</DialogTitle>
            <DialogDescription>
              {selectedAssessment?.subject} - {selectedAssessment?.chapter}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 mt-4 max-h-[400px] overflow-y-auto">
            {loadingQuestions ? (
              <p className="text-muted-foreground text-center py-8">Loading questions...</p>
            ) : questions.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">No questions found</p>
            ) : (
              questions.map((q, index) => (
                <div key={q.id} className="p-4 bg-muted rounded-lg space-y-3">
                  <div className="flex items-start justify-between">
                    <p className="font-medium flex-1">
                      <span className="text-[#1E88E5] font-semibold">Q{index + 1}.</span> {q.question}
                    </p>
                    <Badge variant="outline" className="ml-2">
                      {q.difficulty}
                    </Badge>
                  </div>
                  <div className="space-y-1 ml-4">
                    {Object.entries(q.options).map(([key, value]) => (
                      <p
                        key={key}
                        className={
                          key === q.correct_answer
                            ? 'text-[#43A047] font-semibold flex items-center gap-2'
                            : ''
                        }
                      >
                        {key}) {value}
                        {key === q.correct_answer && (
                          <span className="text-xs bg-[#43A047] text-white px-2 py-0.5 rounded">
                            ✓ Correct
                          </span>
                        )}
                      </p>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}