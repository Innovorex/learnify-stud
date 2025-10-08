import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Button } from '../ui/button';
import { Eye, Award, TrendingUp } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Badge } from '../ui/badge';
import { teacherAPI } from '../../services/api';
import { toast } from 'sonner';

interface Assessment {
  id: number;
  subject: string;
  chapter: string;
  start_time: string;
  end_time: string;
}

interface SummaryItem {
  assessment_id: number;
  subject: string;
  chapter: string;
  average_score: number;
  top_score: number;
}

interface AssessmentDetailResult {
  assessment_id: number;
  average_score: number;
  total_students: number;
  top_scorer: string | null;
  results: {
    student_id: number;
    score: number;
    submitted_at: string;
  }[];
}

interface User {
  id: number;
  name: string;
}

export function Results() {
  const [loading, setLoading] = useState(true);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [summary, setSummary] = useState<SummaryItem[]>([]);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<number | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedChapter, setSelectedChapter] = useState<string>('');
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [detailResults, setDetailResults] = useState<AssessmentDetailResult | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

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
      console.error('Error fetching results data:', error);
      toast.error(error.response?.data?.detail || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const fetchAssessmentDetails = async (assessmentId: number) => {
    try {
      setLoadingDetails(true);
      const response = await teacherAPI.getAssessmentResults(assessmentId);
      setDetailResults(response.data);
    } catch (error: any) {
      console.error('Error fetching assessment details:', error);
      toast.error(error.response?.data?.detail || 'Failed to load assessment details');
      setDetailResults(null);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleViewDetails = (assessmentId: number) => {
    const assessment = assessments.find(a => a.id === assessmentId);
    const summaryItem = summary.find(s => s.assessment_id === assessmentId);

    if (assessment && summaryItem) {
      setSelectedAssessmentId(assessmentId);
      setSelectedSubject(summaryItem.subject);
      setSelectedChapter(summaryItem.chapter);
      setShowDetailsDialog(true);
      fetchAssessmentDetails(assessmentId);
    }
  };

  const calculateOverallStats = () => {
    if (summary.length === 0) {
      return {
        overallAverage: 0,
        topScore: 0,
        completedAssessments: 0,
      };
    }

    const overallAverage = Math.round(
      summary.reduce((acc, s) => acc + s.average_score, 0) / summary.length
    );
    const topScore = Math.max(...summary.map(s => s.top_score));
    const completedAssessments = summary.length;

    return { overallAverage, topScore, completedAssessments };
  };

  const stats = calculateOverallStats();

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-[#43A047]';
    if (score >= 70) return 'text-[#1E88E5]';
    if (score >= 50) return 'text-orange-500';
    return 'text-[#E53935]';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1>Results</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1>Results</h1>
        <p className="text-muted-foreground">View assessment results and analytics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="h-5 w-5 text-[#1E88E5]" />
              <p className="text-sm text-muted-foreground">Overall Average</p>
            </div>
            <h3 className="text-3xl">{stats.overallAverage}%</h3>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <Award className="h-5 w-5 text-[#43A047]" />
              <p className="text-sm text-muted-foreground">Top Score</p>
            </div>
            <h3 className="text-3xl">{stats.topScore}%</h3>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-2">
              <Eye className="h-5 w-5 text-purple-500" />
              <p className="text-sm text-muted-foreground">Completed</p>
            </div>
            <h3 className="text-3xl">{stats.completedAssessments}</h3>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Assessment Results</CardTitle>
        </CardHeader>
        <CardContent>
          {summary.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No results found</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Chapter</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Avg Score</TableHead>
                  <TableHead>Top Score</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {summary.map((result) => {
                  const assessment = assessments.find(a => a.id === result.assessment_id);
                  return (
                    <TableRow key={result.assessment_id}>
                      <TableCell>AS{result.assessment_id.toString().padStart(3, '0')}</TableCell>
                      <TableCell>{result.subject}</TableCell>
                      <TableCell>{result.chapter}</TableCell>
                      <TableCell>
                        {assessment
                          ? new Date(assessment.start_time).toLocaleDateString('en-US')
                          : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`border-current ${getScoreColor(result.average_score)}`}
                        >
                          {Math.round(result.average_score)}%
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`border-current ${getScoreColor(result.top_score)}`}
                        >
                          {result.top_score}%
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewDetails(result.assessment_id)}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Student-wise Results</DialogTitle>
            <DialogDescription>
              {selectedSubject} - {selectedChapter}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            {loadingDetails ? (
              <p className="text-muted-foreground text-center py-8">Loading details...</p>
            ) : !detailResults || detailResults.results.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">No student results found</p>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
                  <div>
                    <p className="text-sm text-muted-foreground">Average Score</p>
                    <p className="text-lg font-semibold">{Math.round(detailResults.average_score)}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total Students</p>
                    <p className="text-lg font-semibold">{detailResults.total_students}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Top Scorer</p>
                    <p className="text-lg font-semibold">{detailResults.top_scorer || 'N/A'}</p>
                  </div>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Student ID</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Percentage</TableHead>
                      <TableHead>Submitted At</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {detailResults.results.map((student) => {
                      const percentage = student.score;
                      return (
                        <TableRow key={student.student_id}>
                          <TableCell>ST{student.student_id.toString().padStart(3, '0')}</TableCell>
                          <TableCell>{student.score}</TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={`border-current ${getScoreColor(percentage)}`}
                            >
                              {percentage}%
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {new Date(student.submitted_at).toLocaleString('en-US', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: true,
                            })}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}