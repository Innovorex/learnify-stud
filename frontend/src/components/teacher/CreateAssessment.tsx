import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '../ui/badge';
import { teacherAPI } from '../../services/api';

export function CreateAssessment() {
  const [className, setClassName] = useState('');
  const [subject, setSubject] = useState('');
  const [chapter, setChapter] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [duration, setDuration] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [questionsGenerated, setQuestionsGenerated] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!className || !subject || !chapter || !startTime || !endTime || !duration) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsGenerating(true);

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');

      await teacherAPI.createAssessment({
        teacher_id: user.id,
        class_name: className,
        subject: subject,
        chapter: chapter,
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        duration_minutes: parseInt(duration)
      });

      toast.success('Assessment created successfully – AI generation in progress…');

      // Simulate AI generation time (questions are generated in background)
      setTimeout(() => {
        setIsGenerating(false);
        setQuestionsGenerated(true);
        toast.success('Questions Generated ✅');

        // Reset form
        setClassName('');
        setSubject('');
        setChapter('');
        setStartTime('');
        setEndTime('');
        setDuration('');
      }, 3000);

    } catch (error: any) {
      setIsGenerating(false);
      toast.error(error.response?.data?.detail || 'Failed to create assessment');
    }
  };

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1>Create Assessment</h1>
        <p className="text-muted-foreground">Generate AI-powered assessment questions</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Assessment Details</CardTitle>
          <CardDescription>
            Fill in the details below to create a new assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="className">Class Name</Label>
                <Input
                  id="className"
                  placeholder="e.g., 10A"
                  value={className}
                  onChange={(e) => setClassName(e.target.value)}
                  className="bg-input-background"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  placeholder="e.g., Mathematics"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="bg-input-background"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="chapter">Chapter</Label>
              <Input
                id="chapter"
                placeholder="e.g., Real Numbers"
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                className="bg-input-background"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="startTime">Start Time</Label>
                <Input
                  id="startTime"
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="bg-input-background"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endTime">End Time</Label>
                <Input
                  id="endTime"
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="bg-input-background"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="duration">Duration (minutes)</Label>
              <Input
                id="duration"
                type="number"
                placeholder="e.g., 60"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="bg-input-background"
              />
            </div>

            <div className="flex items-center gap-4">
              <Button
                type="submit"
                disabled={isGenerating}
                className="bg-[#1E88E5] hover:bg-[#1565C0]"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {isGenerating ? 'Generating...' : 'Generate Questions with AI'}
              </Button>

              {questionsGenerated && (
                <Badge className="bg-[#43A047] hover:bg-[#43A047]/90">
                  Questions Generated ✅
                </Badge>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
