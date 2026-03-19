import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../lib/axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Loader2, Clock, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import ElectricBorder from '../components/ElectricBorder';

export default function TakeQuiz() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [quiz, setQuiz] = useState(null);
  const [attemptId, setAttemptId] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedChoice, setSelectedChoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);

  // Initial load
  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const { data } = await api.get(`/quizzes/${id}/`);
        setQuiz(data.data);
        if (data.data.status !== 'ready') {
          toast.error("This quiz isn't ready yet.");
          navigate('/');
        }
      } catch (err) {
        toast.error('Failed to load quiz');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    fetchQuiz();
  }, [id, navigate]);

  // Timer logic
  useEffect(() => {
    if (!attemptId || timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleCompleteAttempt();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [attemptId, timeLeft]);

  const handleStartAttempt = async () => {
    setLoading(true);
    try {
      const { data } = await api.post('/attempts/', { quiz_id: id });
      setAttemptId(data.data.id);
      
      // Calculate remaining time if resumed
      if (data.data.status === 'in_progress' && data.data.started_at) {
        const elapsed = Math.floor((new Date() - new Date(data.data.started_at)) / 1000);
        const remaining = (quiz.time_limit_minutes * 60) - elapsed;
        setTimeLeft(remaining > 0 ? remaining : 0);
      } else {
        setTimeLeft(quiz.time_limit_minutes * 60);
      }
      
    } catch (err) {
      toast.error('Failed to start attempt');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedChoice) return;
    setSubmitting(true);
    
    const question = quiz.questions[currentQuestionIndex];
    try {
      await api.post(`/attempts/${attemptId}/answer/`, {
        question_id: question.id,
        choice_id: selectedChoice,
        time_taken_seconds: 15 // simplified for now
      });
      
      if (currentQuestionIndex < quiz.questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
        setSelectedChoice(null);
      } else {
        await handleCompleteAttempt();
      }
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCompleteAttempt = async () => {
    try {
      await api.post(`/attempts/${attemptId}/complete/`);
      toast.success('Quiz completed!');
      navigate(`/attempt/${attemptId}/results`);
    } catch (err) {
      toast.error('Failed to complete attempt');
    }
  };

  if (loading && !quiz) return <div className="flex justify-center py-20"><Loader2 className="w-10 h-10 animate-spin text-brand-accent" /></div>;

  const currentQuestion = quiz?.questions?.[currentQuestionIndex];
  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      {!attemptId ? (
        // Start Screen
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="bg-[#111] border border-[#222] p-10 rounded-2xl text-center"
        >
          <h1 className="text-4xl font-extrabold mb-4">{quiz.title}</h1>
          <div className="flex items-center justify-center gap-6 text-gray-400 mb-10">
            <span className="capitalize px-3 py-1 bg-[#1a1a1a] rounded-full text-sm">{quiz.topic}</span>
            <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> {quiz.time_limit_minutes} minutes</span>
            <span>{quiz.question_count} Questions</span>
          </div>

          <button 
            onClick={handleStartAttempt}
            disabled={loading}
            className="inline-flex items-center gap-2 bg-brand-accent hover:bg-emerald-600 text-white font-bold text-xl px-10 py-5 rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <><Play className="w-6 h-6 fill-current" /> Start Quiz</>}
          </button>
        </motion.div>
      ) : (
        // Active Quiz Screen
        <div className="space-y-6">
          {/* Header Bar */}
          <div className="flex items-center justify-between bg-[#111] p-4 rounded-xl border border-[#222]">
            <div>
              <p className="text-sm text-gray-400">Question {currentQuestionIndex + 1} of {quiz.questions.length}</p>
              <div className="w-64 h-2 bg-[#222] rounded-full mt-2 overflow-hidden">
                <div 
                  className="h-full bg-brand-accent transition-all duration-300"
                  style={{ width: `${((currentQuestionIndex) / quiz.questions.length) * 100}%` }}
                />
              </div>
            </div>
            <div className={`flex items-center gap-2 font-mono text-xl font-bold px-4 py-2 rounded-lg ${timeLeft < 60 ? 'bg-red-500/20 text-red-400' : 'bg-[#1a1a1a] text-brand-accent'}`}>
              <Clock className="w-5 h-5" />
              {formatTime(timeLeft)}
            </div>
          </div>

          {/* Question View */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentQuestion.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-[#111] p-8 rounded-2xl border border-[#222]"
            >
              <h2 className="text-2xl font-bold text-white mb-8">{currentQuestion.question_text}</h2>
              
              <div className="space-y-4">
                {currentQuestion.choices.map((choice) => (
                  <button
                    key={choice.id}
                    onClick={() => setSelectedChoice(choice.id)}
                    className={`w-full text-left p-5 rounded-xl border-2 transition-all ${
                      selectedChoice === choice.id 
                        ? 'border-brand-accent bg-brand-accent/10 border-brand-accent shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                        : 'border-[#333] hover:border-gray-500 bg-[#0a0a0a]'
                    }`}
                  >
                    <div className="flex justify-between items-center text-lg">
                      <span>{choice.choice_text}</span>
                      {selectedChoice === choice.id && <CheckCircle2 className="w-6 h-6 text-brand-accent" />}
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-10 flex justify-end">
                <button
                  onClick={handleSubmitAnswer}
                  disabled={!selectedChoice || submitting}
                  className="px-8 py-4 rounded-xl font-bold bg-white text-black hover:bg-gray-200 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 
                    currentQuestionIndex === quiz.questions.length - 1 ? 'Submit & Finish' : 'Next Question'
                  }
                </button>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
