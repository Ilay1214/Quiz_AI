import { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuizStore } from "@/store/quizStore";
import { useToast } from "@/hooks/use-toast";
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  Flag,
  Trophy,
  Target,
  Clock,
} from "lucide-react";
import Header from "@/components/common/Header";

const Results = () => {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<'all' | 'correct' | 'incorrect' | 'flagged'>('all');
  const { session, answers, flaggedQuestions, isSubmitted, resetQuiz } = useQuizStore();

  // Removed useEffect for redirecting unauthenticated users

  const results = useMemo(() => {
    if (!session || !isSubmitted) return null;

    let correct = 0;
    const questionResults = session.questions.map((question) => {
      const userAnswer = answers.find(a => a.questionId === question.id);
      const userAnswers = userAnswer?.answers || [];
      
      let isCorrect: boolean;

      if (question.type === 'text') {
        // For text questions, perform a case-insensitive, trimmed comparison
        const userText = userAnswers[0]?.trim().toLowerCase() || '';
        const correctText = question.correctAnswers[0]?.trim().toLowerCase() || '';
        isCorrect = userText === correctText;
      } else {
        // For single or multiple choice questions
        isCorrect = question.correctAnswers.length === userAnswers.length &&
          question.correctAnswers.every(ca => userAnswers.includes(ca));
      }
      
      if (isCorrect) correct++;
      
      return {
        question,
        userAnswers,
        correctAnswers: question.correctAnswers,
        isCorrect,
        isFlagged: flaggedQuestions.has(question.id),
      };
    });

    const percentage = Math.round((correct / session.questions.length) * 100);
    
    return {
      correct,
      total: session.questions.length,
      percentage,
      questionResults,
    };
  }, [session, answers, flaggedQuestions, isSubmitted]);

  if (!session || !isSubmitted || !results) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="mb-4">No results found.</p>
            <Button onClick={() => navigate('/setup')}>
              Go to Setup
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const filteredResults = results.questionResults.filter((result) => {
    switch (filter) {
      case 'correct':
        return result.isCorrect;
      case 'incorrect':
        return !result.isCorrect;
      case 'flagged':
        return result.isFlagged;
      default:
        return true;
    }
  });

  const handleRetake = () => {
    resetQuiz();
    navigate('/setup');
  };

  const handleHome = () => {
    resetQuiz();
    navigate('/');
  };

  const getGradeColor = (percentage: number) => {
    if (percentage >= 90) return 'text-success';
    if (percentage >= 80) return 'text-primary';
    if (percentage >= 70) return 'text-warning';
    return 'text-destructive';
  };

  const getGradeBg = (percentage: number) => {
    if (percentage >= 90) return 'bg-success/10 border-success/20';
    if (percentage >= 80) return 'bg-primary/10 border-primary/20';
    if (percentage >= 70) return 'bg-warning/10 border-warning/20';
    return 'bg-destructive/10 border-destructive/20';
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <Header showBackButton={true} title="Quiz Results" />
      <div className="container mx-auto px-4 max-w-4xl relative mt-8">
        {/* Score Overview */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className={`text-center ${getGradeBg(results.percentage)}`}>
            <CardContent className="pt-6">
              <div className={`text-4xl font-bold mb-2 ${getGradeColor(results.percentage)}`}>
                {results.percentage}%
              </div>
              <p className="text-sm text-muted-foreground">Overall Score</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <CheckCircle className="w-6 h-6 text-success" />
                <span className="text-2xl font-bold">{results.correct}</span>
              </div>
              <p className="text-sm text-muted-foreground">Correct Answers</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Target className="w-6 h-6 text-primary" />
                <span className="text-2xl font-bold">{results.total}</span>
              </div>
              <p className="text-sm text-muted-foreground">Total Questions</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-xl font-semibold text-success">
                  {results.questionResults.filter(r => r.isCorrect).length}
                </div>
                <div className="text-sm text-muted-foreground">Correct</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-semibold text-destructive">
                  {results.questionResults.filter(r => !r.isCorrect).length}
                </div>
                <div className="text-sm text-muted-foreground">Incorrect</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-semibold text-warning">
                  {results.questionResults.filter(r => r.isFlagged).length}
                </div>
                <div className="text-sm text-muted-foreground">Flagged</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-semibold text-primary">
                  {session.mode}
                </div>
                <div className="text-sm text-muted-foreground">Mode</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Results */}
        <Card>
          <CardHeader>
            <CardTitle>Question Breakdown</CardTitle>
            <CardDescription>
              Review your answers for each question
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={filter} onValueChange={(value: any) => setFilter(value)}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="all">All ({results.questionResults.length})</TabsTrigger>
                <TabsTrigger value="correct">
                  Correct ({results.questionResults.filter(r => r.isCorrect).length})
                </TabsTrigger>
                <TabsTrigger value="incorrect">
                  Incorrect ({results.questionResults.filter(r => !r.isCorrect).length})
                </TabsTrigger>
                <TabsTrigger value="flagged">
                  Flagged ({results.questionResults.filter(r => r.isFlagged).length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value={filter} className="space-y-4 mt-6">
                {filteredResults.map((result, index) => (
                  <Card key={result.question.id} className="border-l-4 border-l-muted">
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-muted-foreground">
                            Q{session.questions.findIndex(q => q.id === result.question.id) + 1}
                          </span>
                          {result.isCorrect ? (
                            <CheckCircle className="w-4 h-4 text-success" />
                          ) : (
                            <XCircle className="w-4 h-4 text-destructive" />
                          )}
                          {result.isFlagged && (
                            <Flag className="w-4 h-4 text-warning" />
                          )}
                        </div>
                        <Badge variant={result.isCorrect ? "default" : "destructive"}>
                          {result.isCorrect ? "Correct" : "Incorrect"}
                        </Badge>
                      </div>

                      <h4 className="font-medium mb-3">{result.question.question}</h4>

                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium text-muted-foreground">Your answer:</span>
                          <div className="mt-1">
                            {result.userAnswers.length > 0 ? (
                              result.question.type === 'text' ? (
                                <div className="p-2 border rounded-md bg-muted/20 text-sm whitespace-pre-wrap">
                                  {result.userAnswers[0]}
                                </div>
                              ) : (
                                result.userAnswers.map((answer, i) => (
                                  <Badge key={i} variant="outline" className="mr-2">
                                    {answer}
                                  </Badge>
                                ))
                              )
                            ) : (
                              <span className="text-muted-foreground italic">No answer provided</span>
                            )}
                          </div>
                        </div>

                        {!result.isCorrect && (
                          <div>
                            <span className="text-sm font-medium text-muted-foreground">Correct answer:</span>
                            <div className="mt-1">
                              {result.question.type === 'text' ? (
                                <div className="p-2 border rounded-md bg-success/10 text-success text-sm whitespace-pre-wrap">
                                  {result.correctAnswers[0]}
                                </div>
                              ) : (
                                result.correctAnswers.map((answer, i) => (
                                  <Badge key={i} variant="default" className="mr-2">
                                    {answer}
                                  </Badge>
                                ))
                              )}
                            </div>
                          </div>
                        )}

                        {result.question.explanation && (
                          <div className="pt-2 border-t">
                            <span className="text-sm font-medium text-muted-foreground">Explanation:</span>
                            <p className="text-sm mt-1">{result.question.explanation}</p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {filteredResults.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No questions match the current filter.
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 mt-8">
          <Button onClick={handleRetake} className="flex-1" size="lg">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retake with Same File
          </Button>
          <Button variant="outline" onClick={handleHome} size="lg">
            Back to Home
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Results;