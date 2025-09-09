import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, Zap, BookOpen, Target } from "lucide-react";

const Landing = () => {
  const navigate = useNavigate();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleModeSelect = (mode: 'exam' | 'practice') => {
    if (isMounted) {
      navigate('/setup', { state: { mode } });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-primary to-accent text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              StudyQuiz AI
            </h1>
            <p className="text-xl mb-8 opacity-90">
              Transform your study materials into personalized quizzes with AI. 
              Practice or take timed exams to test your knowledge.
            </p>
          </div>
        </div>
      </div>

      {/* Mode Selection */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Choose Your Study Mode</h2>
          <p className="text-muted-foreground text-center mb-12">
            Select how you want to test your knowledge
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Exam Mode */}
            <Card className="relative hover:shadow-lg transition-shadow cursor-pointer group" 
                  onClick={() => handleModeSelect('exam')}>
              <CardHeader className="text-center pb-4">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors">
                  <Clock className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-2xl">Exam Mode</CardTitle>
                <CardDescription className="text-base">
                  Timed quiz that simulates real exam conditions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-accent" />
                  <span>Timed sessions (1-180 minutes)</span>
                </div>
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-accent" />
                  <span>Auto-submit when time expires</span>
                </div>
                <div className="flex items-center gap-3">
                  <BookOpen className="w-5 h-5 text-accent" />
                  <span>Results shown after completion</span>
                </div>
              </CardContent>
              <div className="absolute bottom-4 left-4 right-4">
                <Button className="w-full" size="lg">
                  Start Exam Mode
                </Button>
              </div>
            </Card>

            {/* Practice Mode */}
            <Card className="relative hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => handleModeSelect('practice')}>
              <CardHeader className="text-center pb-4">
                <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-accent/20 transition-colors">
                  <BookOpen className="w-8 h-8 text-accent" />
                </div>
                <CardTitle className="text-2xl">Practice Mode</CardTitle>
                <CardDescription className="text-base">
                  Learn with immediate feedback on each question
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-primary" />
                  <span>Immediate answer feedback</span>
                </div>
                <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-primary" />
                  <span>No time pressure</span>
                </div>
                <div className="flex items-center gap-3">
                  <BookOpen className="w-5 h-5 text-primary" />
                  <span>Learn from explanations</span>
                </div>
              </CardContent>
              <div className="absolute bottom-4 left-4 right-4">
                <Button variant="outline" className="w-full" size="lg">
                  Start Practice Mode
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-secondary/30 py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-2xl font-bold mb-8">How It Works</h3>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold mb-2">Upload Your Materials</h4>
                <p className="text-sm text-muted-foreground">
                  Upload PDF, DOCX, or TXT files with your study content
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold mb-2">AI Generates Questions</h4>
                <p className="text-sm text-muted-foreground">
                  Our AI analyzes your content and creates relevant quiz questions
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-semibold mb-2">Test Your Knowledge</h4>
                <p className="text-sm text-muted-foreground">
                  Take your personalized quiz and track your progress
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;