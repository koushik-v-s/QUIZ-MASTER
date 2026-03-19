import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../lib/axios';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle2, Loader2, BrainCircuit, Hash } from 'lucide-react';

export default function QuizPreview() {
  const { id } = useParams();
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const { data } = await api.get(`/quizzes/${id}/`);
        setQuiz(data.data);
      } catch (err) {
        console.error('Failed to load quiz', err);
      } finally {
        setLoading(false);
      }
    };
    fetchQuiz();
  }, [id]);

  if (loading) return (
    <div className="flex items-center justify-center h-[60vh]">
      <Loader2 className="w-10 h-10 animate-spin text-brand-accent" />
    </div>
  );

  if (!quiz) return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-gray-400">
      <BrainCircuit className="w-16 h-16 mb-4" />
      <p className="text-xl">Quiz not found.</p>
      <Link to="/" className="text-brand-accent hover:underline mt-4">← Back to Dashboard</Link>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto py-8 space-y-8">
      {/* Header */}
      <div>
        <Link to="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-brand-accent transition-colors mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-white">{quiz.title}</h1>
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-400">
          <span className="capitalize">{quiz.difficulty} difficulty</span>
          <span>•</span>
          <span>{quiz.questions?.length || quiz.question_count} questions</span>
          <span>•</span>
          <span>{quiz.time_limit_minutes} min time limit</span>
          {quiz.ai_model_used && (
            <>
              <span>•</span>
              <span className="text-brand-accent">AI: {quiz.ai_model_used}</span>
            </>
          )}
        </div>
      </div>

      {/* Questions */}
      <div className="space-y-6">
        {quiz.questions?.map((q, qIdx) => (
          <motion.div
            key={q.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: qIdx * 0.05 }}
            className="bg-[#111] border border-[#222] rounded-2xl p-6 space-y-4"
          >
            {/* Question header */}
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-accent/10 text-brand-accent font-bold text-sm shrink-0">
                {qIdx + 1}
              </div>
              <p className="text-white font-medium text-lg leading-relaxed">{q.question_text}</p>
            </div>

            {/* Choices */}
            <div className="space-y-2 ml-11">
              {q.choices?.map((c, cIdx) => (
                <div
                  key={c.id || cIdx}
                  className={`flex items-center gap-3 p-3 rounded-xl border transition-colors ${
                    c.is_correct 
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' 
                      : 'bg-[#0a0a0a] border-[#1a1a1a] text-gray-300'
                  }`}
                >
                  {c.is_correct ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-[#333] shrink-0" />
                  )}
                  <span className="text-sm">{c.choice_text}</span>
                  {c.is_correct && (
                    <span className="ml-auto text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                      Correct
                    </span>
                  )}
                </div>
              ))}
            </div>

            {/* Explanation */}
            {q.explanation && (
              <div className="ml-11 bg-blue-500/5 border border-blue-500/10 rounded-xl p-4">
                <p className="text-xs font-semibold text-blue-400 mb-1">EXPLANATION</p>
                <p className="text-sm text-gray-300 leading-relaxed">{q.explanation}</p>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {!quiz.questions?.length && (
        <div className="text-center py-16 text-gray-500">
          <BrainCircuit className="w-12 h-12 mx-auto mb-4" />
          <p>No questions available for this quiz yet.</p>
        </div>
      )}
    </div>
  );
}
