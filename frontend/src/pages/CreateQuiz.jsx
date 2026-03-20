import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../lib/axios';
import { motion, AnimatePresence } from 'framer-motion';
import { BrainCircuit, Loader2, Sparkles, AlertCircle, CheckCircle2, PlusCircle, Eye } from 'lucide-react';
import toast from 'react-hot-toast';
import ElectricBorder from '../components/ElectricBorder';

export default function CreateQuiz() {
  const navigate = useNavigate();
  const [step, setStep] = useState('form'); // 'form' | 'generating' | 'done' | 'error'
  const [errorMsg, setErrorMsg] = useState('');
  const [createdQuizId, setCreatedQuizId] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    topic: '',
    difficulty: 'medium',
    question_count: 5,
    time_limit_minutes: 10,
    is_public: true
  });

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStep('generating');
    try {
      const { data } = await api.post('/quizzes/', formData);
      setCreatedQuizId(data.data.id);
    } catch (err) {
      setErrorMsg(err.response?.data?.error?.message || 'Failed to start AI generation.');
      setStep('error');
    }
  };

  // Poll for status
  useEffect(() => {
    if (step === 'generating' && createdQuizId) {
      const interval = setInterval(async () => {
        try {
          const { data } = await api.get(`/quizzes/${createdQuizId}/status/`);
          const status = data.data.status;
          
          if (status === 'ready') {
            clearInterval(interval);
            toast.success('Quiz generated successfully!');
            setStep('done');
          } else if (status === 'failed') {
            clearInterval(interval);
            setErrorMsg(data.data.error_message || 'AI Generation failed.');
            setStep('error');
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    }
  }, [step, createdQuizId, navigate]);

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold flex items-center justify-center gap-3">
          <BrainCircuit className="text-brand-accent w-10 h-10" />
          AI Quiz Studio
        </h1>
        <p className="text-gray-400 mt-3 text-lg">Define your parameters. Let the AI do the heavy lifting.</p>
      </div>

      <AnimatePresence mode="wait">
        {step === 'form' && (
          <motion.div
            key="form"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-[#111] border border-[#222] p-8 rounded-2xl shadow-xl"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-medium text-gray-300 mb-2">Quiz Title</label>
                  <input
                    type="text"
                    name="title"
                    required
                    value={formData.title}
                    onChange={handleChange}
                    className="w-full bg-[#0a0a0a] border border-[#333] rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-accent outline-none"
                    placeholder="e.g. Advanced Python Generators"
                  />
                </div>

                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-medium text-gray-300 mb-2">Specific Topic (Prompt for AI)</label>
                  <textarea
                    name="topic"
                    required
                    rows="3"
                    value={formData.topic}
                    onChange={handleChange}
                    className="w-full bg-[#0a0a0a] border border-[#333] rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-accent outline-none"
                    placeholder="Describe exactly what you want the quiz to test. E.g., 'Python decorators and closures, focusing on real-world web development scenarios.'"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Difficulty</label>
                  <select
                    name="difficulty"
                    value={formData.difficulty}
                    onChange={handleChange}
                    className="w-full bg-[#0a0a0a] border border-[#333] rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-accent outline-none appearance-none"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Number of Questions</label>
                  <input
                    type="number"
                    name="question_count"
                    min="1"
                    max="20"
                    required
                    value={formData.question_count}
                    onChange={handleChange}
                    className="w-full bg-[#0a0a0a] border border-[#333] rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-accent outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Time Limit (Minutes)</label>
                  <input
                    type="number"
                    name="time_limit_minutes"
                    min="1"
                    max="120"
                    required
                    value={formData.time_limit_minutes}
                    onChange={handleChange}
                    className="w-full bg-[#0a0a0a] border border-[#333] rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-accent outline-none"
                  />
                </div>

                <div className="flex items-center mt-8">
                  <input
                    type="checkbox"
                    name="is_public"
                    id="is_public"
                    checked={formData.is_public}
                    onChange={handleChange}
                    className="w-5 h-5 bg-[#0a0a0a] border border-[#333] rounded focus:ring-brand-accent text-brand-accent appearance-none checked:bg-brand-accent relative after:content-['✓'] after:absolute after:hidden after:checked:block after:text-white after:left-[3px] after:-top-[2px] after:text-sm font-bold cursor-pointer"
                  />
                  <label htmlFor="is_public" className="ml-3 text-sm font-medium text-gray-300 cursor-pointer">
                    Make this quiz public
                  </label>
                </div>
              </div>

              <div className="pt-4 border-t border-[#222]">
                <button
                  type="submit"
                  className="w-full flex items-center justify-center gap-2 py-4 px-6 rounded-xl text-white font-bold text-lg bg-emerald-600 hover:bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all"
                >
                  <Sparkles className="w-6 h-6" />
                  Generate with Grok AI
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {step === 'generating' && (
          <motion.div
            key="generating"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center p-16 text-center bg-[#111] rounded-2xl border border-brand-accent/30 shadow-[0_0_40px_rgba(16,185,129,0.1)]"
          >
            <div className="relative">
              <div className="absolute inset-0 rounded-full blur-xl bg-brand-accent/30 animate-pulse" />
              <Loader2 className="w-20 h-20 text-brand-accent animate-spin relative z-10" />
            </div>
            <h3 className="text-2xl font-bold mt-8 mb-2">AI is Thinking...</h3>
            <p className="text-gray-400 max-w-sm">
              Grok is researching your topic, writing challenging questions, and generating detailed explanations. This might take 10-30 seconds.
            </p>
          </motion.div>
        )}

        {step === 'done' && (
          <motion.div
            key="done"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center p-16 text-center bg-[#111] rounded-2xl border border-emerald-500/30 shadow-[0_0_40px_rgba(16,185,129,0.15)]"
          >
            <div className="relative">
              <div className="absolute inset-0 rounded-full blur-xl bg-emerald-500/20" />
              <CheckCircle2 className="w-20 h-20 text-emerald-400 relative z-10" />
            </div>
            <h3 className="text-2xl font-bold mt-8 mb-2 text-emerald-300">Quiz Generated Successfully!</h3>
            <p className="text-gray-400 max-w-sm mb-8">
              Your AI-powered quiz has been created and is ready for users to attempt.
            </p>
            <div className="flex items-center gap-4">
              <Link
                to={`/quiz/${createdQuizId}/preview`}
                className="flex items-center gap-2 px-6 py-3 bg-[#222] hover:bg-[#333] rounded-xl text-white font-medium transition-colors border border-[#444]"
              >
                <Eye className="w-5 h-5" />
                View Quiz
              </Link>
              <button
                onClick={() => {
                  setStep('form');
                  setCreatedQuizId(null);
                  setFormData({
                    title: '',
                    topic: '',
                    difficulty: 'medium',
                    question_count: 5,
                    time_limit_minutes: 10,
                    is_public: true
                  });
                }}
                className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-white font-bold transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)]"
              >
                <PlusCircle className="w-5 h-5" />
                Generate Another Quiz
              </button>
            </div>
          </motion.div>
        )}

        {step === 'error' && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center p-12 text-center bg-[#1a0a0a] rounded-2xl border border-red-500/30"
          >
            <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
            <h3 className="text-2xl font-bold text-red-400 mb-2">Generation Failed</h3>
            <p className="text-gray-300 mb-8 max-w-md">{errorMsg}</p>
            <button
              onClick={() => setStep('form')}
              className="px-6 py-3 bg-[#222] hover:bg-[#333] rounded-xl text-white font-medium transition-colors border border-[#444]"
            >
              Back to Editor
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
