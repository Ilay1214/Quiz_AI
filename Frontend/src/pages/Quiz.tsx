import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useQuizStore } from "@/store/quizStore";
import { useToast } from "@/hooks/use-toast";
import { 
  ArrowLeft, 
  ArrowRight, 
  Flag, 
  Clock, 
  CheckCircle, 
  Circle, 
  AlertCircle,
  Home,
  Send
} from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const Quiz = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const {
    session,
    currentQuestionIndex,
    timeRemaining,
    isTimerRunning,
    isSubmitted,
    setCurrentQuestion,
    setAnswer,
    toggleFlag,
    startTimer,
    stopTimer,
    updateTimer,
    submitQuiz,
    getCurrentQuestion,
    getAnswer,
    isQuestionAnswered,
    isQuestionFlagged,
    getProgress,
    resetQuiz,
  } = useQuizStore();

  const [selectedAnswers, setSelectedAnswers] = useState<string[]>([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [currentFeedback, setCurrentFeedback] = useState<{
    correct: boolean; 
    explanation?: string;
    correctAnswers?: string[] | null; 
  } | null>(null);

  const currentQuestion = getCurrentQuestion();
  const progress = getProgress();

  // Timer effect
  useEffect(() => {
    if (!session || session.mode !== 'exam' || !isTimerRunning || timeRemaining <= 0) return;

    const interval = setInterval(() => {
      updateTimer(timeRemaining - 1);
      
      if (timeRemaining <= 1) {
        stopTimer();
        handleSubmit();
        toast({
          title: "Time's Up!",
          description: "Your exam has been automatically submitted.",
          variant: "destructive",
        });
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [timeRemaining, isTimerRunning, session, updateTimer, stopTimer]);

  // Start timer on mount for exam mode
  useEffect(() => {
    if (session?.mode === 'exam' && timeRemaining > 0 && !isSubmitted) {
      startTimer();
    }
  }, [session, startTimer, timeRemaining, isSubmitted]);

  // Load current question answers
  useEffect(() => {
    if (currentQuestion) {
      const existingAnswers = getAnswer(currentQuestion.id) || [];
      setSelectedAnswers(existingAnswers);
      setShowFeedback(false);
      setCurrentFeedback(null);
    }
  }, [currentQuestion, getAnswer]);

  // Redirect if no session
  useEffect(() => {
    if (!session) {
      navigate('/setup');
    }
  }, [session, navigate]);

  // Redirect if already submitted
  useEffect(() => {
    if (isSubmitted) {
      navigate('/results');
    }
  }, [isSubmitted, navigate]);

  if (!session || !currentQuestion) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="mb-4">No quiz session found.</p>
            <Button onClick={() => navigate('/setup')}>
              Go to Setup
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleAnswerChange = (answer: string, checked: boolean) => {
    let newAnswers: string[];
    
    if (currentQuestion.type === 'single') {
      newAnswers = checked ? [answer] : [];
    } else if (currentQuestion.type === 'multiple') {
      if (checked) {
        newAnswers = [...selectedAnswers, answer];
      } else {
        newAnswers = selectedAnswers.filter(a => a !== answer);
      }
    } else {
      newAnswers = [answer];
    }
    
    setSelectedAnswers(newAnswers);
    setAnswer(currentQuestion.id, newAnswers);
  };

  const handleTextAnswerChange = (value: string) => {
    const newAnswers = [value];
    setSelectedAnswers(newAnswers);
    setAnswer(currentQuestion.id, newAnswers);
  };

  const handleNext = () => {
    if (currentQuestionIndex < session.questions.length - 1) {
      setCurrentQuestion(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestion(currentQuestionIndex - 1);
    }
  };

  const handleQuestionJump = (index: number) => {
    setCurrentQuestion(index);
  };

  const handleFlag = () => {
    toggleFlag(currentQuestion.id);
  };

  const handleSubmit = () => {
    stopTimer();
    submitQuiz();
  };

  const handleExit = () => {
    resetQuiz();
    navigate('/');
  };

  const checkAnswer = () => {
    if (session.mode !== 'practice' || selectedAnswers.length === 0) return;
    
    const correct = currentQuestion.correctAnswers.every(ca => 
      selectedAnswers.includes(ca)
    ) && selectedAnswers.every(sa => 
      currentQuestion.correctAnswers.includes(sa)
    );
    
    setCurrentFeedback({
      correct,
      explanation: currentQuestion.explanation,
      correctAnswers: correct ? null : currentQuestion.correctAnswers,
    });
    setShowFeedback(true);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getQuestionStatus = (index: number) => {
    const question = session.questions[index];
    const answered = isQuestionAnswered(question.id);
    const flagged = isQuestionFlagged(question.id);
    
    if (flagged) return 'flagged';
    if (answered) return 'answered';
    return 'unanswered';
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
                <Home className="w-4 h-4" />
              </Button>
              <h1 className="text-xl font-semibold">StudyQuiz AI</h1>
            </div>
            
            <div className="flex items-center gap-4">
              {session.mode === 'exam' ? (
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span className={`font-mono text-lg ${timeRemaining < 300 ? 'text-destructive' : ''}`}>
                    {formatTime(timeRemaining)}
                  </span>
                </div>
              ) : (
                <Badge variant="secondary">Practice Mode</Badge>
              )}
              
              <div className="flex gap-2">
                {session.mode === 'exam' && (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button size="sm">
                        <Send className="w-4 h-4 mr-2" />
                        Submit Now
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Submit Exam?</AlertDialogTitle>
                        <AlertDialogDescription>
                          You have answered {progress.answered} out of {progress.total} questions.
                          Are you sure you want to submit your exam?
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleSubmit}>Submit</AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                )}
                
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline" size="sm">Exit</Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Exit Quiz?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Your progress will be lost. Are you sure you want to exit?
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleExit}>Exit</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Question Navigator */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  Questions
                  <Badge variant="outline">
                    {progress.answered}/{progress.total}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-2">
                  {session.questions.map((_, index) => {
                    const status = getQuestionStatus(index);
                    const isCurrent = index === currentQuestionIndex;
                    
                    return (
                      <Button
                        key={index}
                        variant={isCurrent ? "default" : "outline"}
                        size="sm"
                        className={`relative ${
                          status === 'answered' ? 'border-success' :
                          status === 'flagged' ? 'border-warning' :
                          'border-muted'
                        }`}
                        onClick={() => handleQuestionJump(index)}
                      >
                        {index + 1}
                        {status === 'answered' && (
                          <CheckCircle className="absolute -top-1 -right-1 w-3 h-3 text-success" />
                        )}
                        {status === 'flagged' && (
                          <Flag className="absolute -top-1 -right-1 w-3 h-3 text-warning" />
                        )}
                      </Button>
                    );
                  })}
                </div>
                
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-success" />
                    <span>Answered: {progress.answered}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Circle className="w-4 h-4 text-muted-foreground" />
                    <span>Unanswered: {progress.total - progress.answered}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Flag className="w-4 h-4 text-warning" />
                    <span>Flagged: {progress.flagged}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Question Area */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>
                    Question {currentQuestionIndex + 1} of {session.questions.length}
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleFlag}
                    className={isQuestionFlagged(currentQuestion.id) ? 'text-warning border-warning' : ''}
                  >
                    <Flag className="w-4 h-4 mr-2" />
                    {isQuestionFlagged(currentQuestion.id) ? 'Flagged' : 'Flag'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-lg leading-relaxed">
                  {currentQuestion.question}
                </div>

                {/* Answer Options */}
                <div className="space-y-3">
                  {currentQuestion.type === 'single' && currentQuestion.options && (
                    <div className="space-y-2">
                      {currentQuestion.options.map((option, index) => (
                        <label key={index} className="flex items-center space-x-3 p-3 rounded-lg border cursor-pointer hover:bg-secondary/50">
                          <input
                            type="radio"
                            name="answer"
                            value={option}
                            checked={selectedAnswers.includes(option)}
                            onChange={(e) => handleAnswerChange(option, e.target.checked)}
                            className="text-primary"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  )}

                  {currentQuestion.type === 'multiple' && currentQuestion.options && (
                    <div className="space-y-2">
                      {currentQuestion.options.map((option, index) => (
                        <label key={index} className="flex items-center space-x-3 p-3 rounded-lg border cursor-pointer hover:bg-secondary/50">
                          <input
                            type="checkbox"
                            value={option}
                            checked={selectedAnswers.includes(option)}
                            onChange={(e) => handleAnswerChange(option, e.target.checked)}
                            className="text-primary"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  )}

                  {currentQuestion.type === 'text' && (
                    <textarea
                      className="w-full p-3 border rounded-lg resize-none"
                      rows={4}
                      placeholder="Enter your answer..."
                      value={selectedAnswers[0] || ''}
                      onChange={(e) => handleTextAnswerChange(e.target.value)}
                    />
                  )}
                </div>

                {/* Practice Mode Feedback */}
                {session.mode === 'practice' && selectedAnswers.length > 0 && !showFeedback && (
                  <Button onClick={checkAnswer} className="w-full">
                    Check Answer
                  </Button>
                )}

                {showFeedback && currentFeedback && (
                  <Card className={`border-2 ${currentFeedback.correct ? 'border-success bg-success/5' : 'border-destructive bg-destructive/5'}`}>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-2 mb-2">
                        {currentFeedback.correct ? (
                          <CheckCircle className="w-5 h-5 text-success" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-destructive" />
                        )}
                        <span className="font-semibold">
                          {currentFeedback.correct ? 'Correct!' : 'Incorrect'}
                        </span>
                      </div>
                      {!currentFeedback.correct && currentFeedback.correctAnswers && currentQuestion.type !== 'text' && ( 
                        <p className="text-sm text-destructive-foreground mb-2">
                          **Correct Answer(s):** {currentFeedback.correctAnswers.join(', ')}
                        </p>
                      )}
                      {currentFeedback.explanation && (
                        <p className="text-sm text-muted-foreground">
                          {currentFeedback.explanation}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={currentQuestionIndex === 0}
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>

                  <div className="text-sm text-muted-foreground">
                    Question {currentQuestionIndex + 1} of {session.questions.length}
                  </div>

                  <Button
                    onClick={handleNext}
                    disabled={currentQuestionIndex === session.questions.length - 1}
                  >
                    Next
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Quiz;