import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Eye, TrendingUp, Award, Calendar } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { studentAPI } from '../../services/api';
import { toast } from 'sonner';

interface Result {
  assessment_id: number;
  subject: string;
  chapter: string;
  score: number;
  total: number;
  submitted_at: string;
}

export function MyResults() {
  const [results, setResults] = useState<Result[]>([]);
  const [selectedResult, setSelectedResult] = useState<Result | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMyResults();
  }, []);

  const fetchMyResults = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const response = await studentAPI.getMyResults(user.id);
      setResults(response.data);
      setLoading(false);
    } catch (error: any) {
      toast.error('Failed to load results');
      setLoading(false);
    }
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'text-[#43A047] border-[#43A047]';
    if (percentage >= 70) return 'text-[#1E88E5] border-[#1E88E5]';
    if (percentage >= 50) return 'text-orange-500 border-orange-500';
    return 'text-[#E53935] border-[#E53935]';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const averageScore = results.length > 0
    ? Math.round(results.reduce((acc, r) => acc + (r.score / r.total) * 100, 0) / results.length)
    : 0;

  const bestScore = results.length > 0
    ? Math.max(...results.map(r => Math.round((r.score / r.total) * 100)))
    : 0;

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading results...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1>My Results</h1>
        <p className="text-muted-foreground">View your assessment performance</p>
      </div>

      {results.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">No exam results yet. Take your first assessment!</p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="h-5 w-5 text-[#1E88E5]" />
                  <p className="text-sm text-muted-foreground">Average Score</p>
                </div>
                <h3 className="text-3xl">{averageScore}%</h3>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <Award className="h-5 w-5 text-[#43A047]" />
                  <p className="text-sm text-muted-foreground">Best Score</p>
                </div>
                <h3 className="text-3xl">{bestScore}%</h3>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-2">
                  <Calendar className="h-5 w-5 text-purple-500" />
                  <p className="text-sm text-muted-foreground">Exams Taken</p>
                </div>
                <h3 className="text-3xl">{results.length}</h3>
              </CardContent>
            </Card>
          </div>

          {/* Results Table */}
          <Card>
            <CardHeader>
              <CardTitle>Assessment History</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Chapter</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Percentage</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((result) => {
                    const percentage = Math.round((result.score / result.total) * 100);
                    return (
                      <TableRow key={result.assessment_id}>
                        <TableCell>AS{result.assessment_id.toString().padStart(3, '0')}</TableCell>
                        <TableCell>{result.subject}</TableCell>
                        <TableCell>{result.chapter}</TableCell>
                        <TableCell>
                          {result.score}/{result.total}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={`border-2 ${getScoreColor(percentage)}`}>
                            {percentage}%
                          </Badge>
                        </TableCell>
                        <TableCell>{formatDate(result.submitted_at)}</TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedResult(result);
                              setShowDetailsDialog(true);
                            }}
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
            </CardContent>
          </Card>
        </>
      )}

      {/* Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Assessment Details</DialogTitle>
            <DialogDescription>
              {selectedResult?.subject} - {selectedResult?.chapter}
            </DialogDescription>
          </DialogHeader>

          {selectedResult && (
            <div className="space-y-6 mt-4">
              {/* Score Summary */}
              <Card>
                <CardContent className="p-6">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Score</p>
                      <p className="text-2xl">
                        {selectedResult.score}/{selectedResult.total}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Percentage</p>
                      <p className="text-2xl text-[#1E88E5]">
                        {Math.round((selectedResult.score / selectedResult.total) * 100)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Date</p>
                      <p className="text-lg">
                        {formatDate(selectedResult.submitted_at)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Remarks */}
              <Card className="bg-[#F7F9FC]">
                <CardContent className="p-4">
                  <p className="text-sm">
                    <span className="text-muted-foreground">Remarks:</span>{' '}
                    {selectedResult.score / selectedResult.total >= 0.9
                      ? 'Excellent performance! Keep up the great work!'
                      : selectedResult.score / selectedResult.total >= 0.7
                      ? 'Good performance! Review the questions you missed.'
                      : 'Keep practicing. Review the chapter materials.'}
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
