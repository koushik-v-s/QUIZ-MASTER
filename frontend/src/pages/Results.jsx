import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../lib/axios';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, Clock, Trophy, ArrowRight, Loader2, Sparkles } from 'lucide-react';
import LightRays from '../components/LightRays';
import PixelCard from '../components/PixelCard';

export default function Results() {
  const { id } = useParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const { data } = await api.get(`/attempts/${id}/results/`);
        setResults(data.data);
      } catch (err) {
        console.error("Failed to load results", err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [id]);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-10 h-10 animate-spin text-brand-accent" /></div>;
  if (!results) return <div className="text-center py-20 text-red-400">Failed to load results</div>;

  const scoreColor = results.score >= 80 ? 'text-emerald-400' : results.score >= 50 ? 'text-amber-400' : 'text-red-400';
  const scoreBg = results.score >= 80 ? 'border-emerald-500/30 bg-emerald-500/10' : results.score >= 50 ? 'border-amber-500/30 bg-amber-500/10' : 'border-red-500/30 bg-red-500/10';

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Overview Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="bg-[#111] border border-[#222] p-8 md:p-12 rounded-2xl text-center mb-10 overflow-hidden relative"
      >
        <div className="absolute top-0 right-0 p-32 bg-brand-accent/5 rounded-full blur-3xl -z-10" />
        
        <h1 className="text-3xl font-bold mb-8">Quiz Completed</h1>
        
        <div className="flex flex-col md:flex-row items-center justify-center gap-10 mb-10">
          <div className={`w-48 h-48 rounded-full border-8 flex flex-col items-center justify-center ${scoreBg} ${scoreColor}`}>
            <span className="text-5xl font-extrabold">{results.score}%</span>
            <span className="text-sm font-medium mt-1 uppercase tracking-wider opacity-80">Score</span>
          </div>

          <div className="flex flex-col gap-4 text-left">
            <div className="bg-[#1a1a1a] px-6 py-4 rounded-xl border border-[#333] flex items-center gap-4">
              <Trophy className="w-6 h-6 text-brand-accent" />
              <div>
                <p className="text-sm text-gray-400">Points Earned</p>
                <p className="text-xl font-bold">{results.total_points_earned} / {results.total_points_possible}</p>
              </div>
            </div>
            
            <div className="bg-[#1a1a1a] px-6 py-4 rounded-xl border border-[#333] flex items-center gap-4">
              <Clock className="w-6 h-6 text-blue-400" />
              <div>
                <p className="text-sm text-gray-400">Time Taken</p>
                <p className="text-xl font-bold">{formatTime(results.time_taken_seconds)}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center gap-4">
          <Link to="/" className="px-6 py-3 bg-[#222] hover:bg-[#333] border border-[#444] rounded-xl font-medium transition-colors">
            Back to Dashboard
          </Link>
          <button onClick={() => window.scrollTo({ top: 500, behavior: 'smooth' })} className="px-6 py-3 bg-brand-accent hover:bg-emerald-600 rounded-xl font-medium text-white transition-colors flex items-center gap-2">
            Review Answers <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </motion.div>

      {/* Answer Breakdown */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold mb-6 pl-2">Detailed Review</h2>
        
        {results.answers.map((item, index) => {
          const { question, user_selected_choice_id, is_correct } = item;
          
          return (
            <motion.div 
              key={question.id}
              initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              className={`p-6 rounded-2xl border ${is_correct ? 'bg-[#0a110d] border-emerald-900/50' : 'bg-[#110505] border-red-900/50'}`}
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="shrink-0 mt-1">
                  {is_correct ? <CheckCircle2 className="w-6 h-6 text-emerald-500" /> : <XCircle className="w-6 h-6 text-red-500" />}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    <span className="text-gray-500 mr-2">{index + 1}.</span> 
                    {question.question_text}
                  </h3>
                </div>
              </div>

              <div className="space-y-3 pl-10 mb-6">
                {question.choices.map((choice) => {
                  const isSelected = choice.id === user_selected_choice_id;
                  const isActuallyCorrect = choice.is_correct;
                  
                  let choiceClass = "p-4 border border-[#333] bg-[#111] rounded-xl text-gray-300";
                  if (isSelected && isActuallyCorrect) choiceClass = "p-4 border-2 border-emerald-500 bg-emerald-500/10 text-emerald-100 font-medium";
                  else if (isSelected && !isActuallyCorrect) choiceClass = "p-4 border-2 border-red-500 bg-red-500/10 text-red-100 font-medium";
                  else if (!isSelected && isActuallyCorrect) choiceClass = "p-4 border-2 border-emerald-500/50 bg-[#111] text-emerald-400 font-medium border-dashed"; // Show correct answer if missed

                  return (
                    <div key={choice.id} className={choiceClass}>
                      {choice.choice_text}
                    </div>
                  );
                })}
              </div>

              <div className="pl-10">
                <div className="bg-[#1a1a1a] border border-[#333] p-4 rounded-lg flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-1">AI Explanation</h4>
                    <p className="text-gray-400 text-sm leading-relaxed">{question.explanation}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
