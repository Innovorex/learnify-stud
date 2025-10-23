import { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Clock, ChevronLeft, ChevronRight } from 'lucide-react';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Label } from '../ui/label';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog';
import { toast } from 'sonner';
import { studentAPI } from '../../services/api';

interface Question {
  id: number;
  question: string;
  options: Record<string, string>;
}

interface ExamPageProps {
  assessmentId: number;
  onComplete: () => void;
}

export function ExamPage({ assessmentId, onComplete }: ExamPageProps) {

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [assessment, setAssessment] = useState<any>(null);

  useEffect(() => {
    fetchQuestionsAndAssessment();
  }, [assessmentId]);

  useEffect(() => {
    if (timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  const fetchQuestionsAndAssessment = async () => {
    try {
      const response = await studentAPI.getQuestions(Number(assessmentId));
      const fetchedQuestions = response.data;

      setQuestions(fetchedQuestions);

      // Get assessment duration from localStorage or fetch it
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const className = user.class_name || '10';
      const section = user.section || 'A';
      const assessmentsRes = await studentAPI.getAssessments(className, section);
      const currentAssessment = assessmentsRes.data.find((a: any) => a.id === Number(assessmentId));

      if (currentAssessment) {
        setAssessment(currentAssessment);
        setTimeLeft(currentAssessment.duration_minutes * 60);
      }

      setLoading(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load exam questions');
      onComplete();
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerChange = (value: string) => {
    setAnswers({ ...answers, [questions[currentQuestion].id]: value });
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');

      const response = await studentAPI.submitExam({
        student_id: user.id,
        assessment_id: Number(assessmentId),
        answers: answers
      });

      toast.success(`Exam submitted! Score: ${response.data.score}/${response.data.total}`);
      onComplete();
    } catch (error: any) {
      toast.error('Failed to submit exam. Please try again.');
    }
  };

  const answeredCount = Object.keys(answers).length;
  const progressPercentage = questions.length > 0 ? (answeredCount / questions.length) * 100 : 0;

  // Calculate timer color based on time remaining
  const getTimerClass = () => {
    if (!assessment) return 'timer-safe';
    const totalTime = assessment.duration_minutes * 60;
    const percentage = (timeLeft / totalTime) * 100;

    if (percentage > 50) return 'timer-safe';
    if (percentage > 25) return 'timer-warning';
    return 'timer-urgent';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-lg">Loading exam...</p>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">No questions available for this assessment.</p>
            <Button onClick={onComplete} className="mt-4">
              Back to Assessments
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const optionKeys = Object.keys(currentQ.options);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Bar */}
      <Card className="bg-card">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Progress</p>
              <p>
                {answeredCount} of {questions.length} answered
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              <div>
                <p className="text-sm text-muted-foreground">Time Remaining</p>
                <p className={`text-lg font-semibold ${getTimerClass()}`}>{formatTime(timeLeft)}</p>
              </div>
            </div>
          </div>
          <Progress value={progressPercentage} className="mt-4" />
        </CardContent>
      </Card>

      {/* Question Card */}
      <Card>
        <CardContent className="p-8">
          <div className="mb-6">
            <span className="text-sm text-muted-foreground">
              Question {currentQuestion + 1} of {questions.length}
            </span>
            <h2 className="text-xl mt-2">{currentQ.question}</h2>
          </div>

          <RadioGroup
            value={answers[currentQ.id] || ''}
            onValueChange={handleAnswerChange}
            className="space-y-4"
          >
            {optionKeys.map((key) => (
              <div
                key={key}
                className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-muted cursor-pointer"
              >
                <RadioGroupItem value={key} id={`option-${key}`} />
                <Label htmlFor={`option-${key}`} className="flex-1 cursor-pointer">
                  <span className="mr-2">{key})</span>
                  {currentQ.options[key]}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>

        <div className="flex gap-2">
          {currentQuestion === questions.length - 1 ? (
            <Button
              onClick={() => setShowSubmitDialog(true)}
              variant="secondary"
            >
              Submit Exam
            </Button>
          ) : (
            <Button onClick={handleNext} variant="gradient">
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>

      {/* Submit Confirmation Dialog */}
      <AlertDialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Submit Exam?</AlertDialogTitle>
            <AlertDialogDescription>
              You have answered {answeredCount} out of {questions.length} questions.
              Are you sure you want to submit your exam? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleSubmit}
              className="btn-gradient"
            >
              Submit
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
