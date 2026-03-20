import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/auth';
import { motion } from 'framer-motion';
import api from '../lib/axios';
import { Brain, Target, Trophy, Clock, PlayCircle, Loader2, Flame, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import ElectricBorder from '../components/ElectricBorder';

export default function UserDashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [availableQuizzes, setAvailableQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const timestamp = Date.now();
        const [statsRes, attemptsRes, quizzesRes] = await Promise.all([
          api.get(`/analytics/me/?t=${timestamp}`),
          api.get(`/attempts/?t=${timestamp}`),
          api.get(`/quizzes/?t=${timestamp}`)
        ]);
        setStats(statsRes.data.data);
        
        const attemptsData = attemptsRes.data.data;
        const allAttempts = Array.isArray(attemptsData) 
          ? attemptsData
          : (attemptsData?.results || []);
        setAttempts(allAttempts.slice(0, 5));
        
        const quizzesData = quizzesRes.data.data;
        setAvailableQuizzes(
          Array.isArray(quizzesData) 
            ? quizzesData 
            : (quizzesData?.results || [])
        );
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) return (
    <div className="flex h-[60vh] items-center justify-center">
      <Brain className="w-10 h-10 animate-pulse text-brand-accent" />
    </div>
  );

  // Build a set of quiz IDs the user has already completed (no retakes)
  const completedQuizIds = new Set(
    attempts
      .filter(a => a.status === 'completed')
      .map(a => a.quiz?.id || a.quiz_id || a.quiz)
  );

  const StatCard = ({ icon: Icon, label, value, color, borderColor }) => (
    <ElectricBorder color={borderColor || '#10b981'}>
      <motion.div 
        whileHover={{ y: -4, scale: 1.01 }}
        className="p-6 flex flex-col gap-4 transition-all"
      >
        <div className={`p-3 rounded-xl w-fit ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-gray-400 text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
        </div>
      </motion.div>
    </ElectricBorder>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, <span className="text-brand-accent">{user?.username}</span>
        </h1>
        <p className="text-gray-400 mt-1">Here's a summary of your learning progress.</p>
      </div>

      {/* Stats Grid — ElectricBorder */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard icon={Brain} label="Quizzes Taken" value={stats?.total_quizzes_taken || 0} color="bg-purple-500/15 text-purple-400" borderColor="#8b5cf6" />
        <StatCard icon={Target} label="Average Score" value={`${stats?.average_score ? stats.average_score.toFixed(1) : 0}%`} color="bg-emerald-500/15 text-emerald-400" borderColor="#10b981" />
        <StatCard icon={Flame} label="Current Streak" value={`${stats?.streak_days || 0} Days`} color="bg-amber-500/15 text-amber-400" borderColor="#f59e0b" />
        <StatCard icon={TrendingUp} label="Best Score" value={`${stats?.best_score ? stats.best_score.toFixed(1) : 0}%`} color="bg-blue-500/15 text-blue-400" borderColor="#3b82f6" />
      </div>

      {/* Topic Highlights */}
      {(stats?.strongest_topic || stats?.weakest_topic) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {stats?.strongest_topic && (
            <div className="bg-gradient-to-r from-emerald-500/10 to-transparent border border-emerald-500/20 p-5 rounded-2xl flex items-center gap-4 backdrop-blur-sm">
              <Trophy className="w-8 h-8 text-emerald-400" />
              <div>
                <p className="text-gray-400 text-sm">Strongest Topic</p>
                <p className="text-white font-bold text-lg">{stats.strongest_topic}</p>
              </div>
            </div>
          )}
          {stats?.weakest_topic && (
            <div className="bg-gradient-to-r from-amber-500/10 to-transparent border border-amber-500/20 p-5 rounded-2xl flex items-center gap-4 backdrop-blur-sm">
              <Target className="w-8 h-8 text-amber-400" />
              <div>
                <p className="text-gray-400 text-sm">Needs Improvement</p>
                <p className="text-white font-bold text-lg">{stats.weakest_topic}</p>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Available Quizzes */}
        <div className="bg-[#111]/80 backdrop-blur-sm border border-[#222] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-bold">Available Quizzes</h2>
            <span className="text-sm text-gray-500">{availableQuizzes.filter(q => q.status === 'ready').length} available</span>
          </div>
          {availableQuizzes.filter(q => q.status === 'ready').length === 0 ? (
            <div className="text-center py-10">
              <Brain className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500">No quizzes available right now.</p>
              <p className="text-gray-600 text-sm mt-1">Check back soon!</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {availableQuizzes.filter(q => q.status === 'ready').map((quiz) => {
                const isCompleted = completedQuizIds.has(quiz.id);
                return (
                  <motion.div 
                    key={quiz.id} 
                    whileHover={{ x: 4 }}
                    className="flex items-center justify-between p-4 rounded-xl bg-[#0a0a0a] border border-[#1a1a1a] hover:border-brand-accent/30 transition-all"
                  >
                    <div className="flex-1 min-w-0 mr-4">
                      <h3 className="font-semibold text-white truncate">{quiz.title}</h3>
                      <div className="flex items-center gap-2 mt-1.5 text-sm text-gray-500 flex-wrap">
                        <span className={`px-2 py-0.5 rounded-full text-xs border ${
                          quiz.difficulty === 'easy' ? 'border-emerald-500/30 text-emerald-400' :
                          quiz.difficulty === 'medium' ? 'border-amber-500/30 text-amber-400' :
                          'border-red-500/30 text-red-400'
                        }`}>{quiz.difficulty}</span>
                        <span>{quiz.question_count} Qs</span>
                        {quiz.time_limit_minutes && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />{quiz.time_limit_minutes}m
                          </span>
                        )}
                      </div>
                    </div>
                    {isCompleted ? (
                      <span className="flex items-center gap-1.5 px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-lg text-sm font-medium shrink-0 border border-emerald-500/20">
                        <CheckCircle2 className="w-4 h-4" />
                        Completed
                      </span>
                    ) : (
                      <Link 
                        to={`/quiz/${quiz.id}/take`} 
                        className="flex items-center gap-2 px-4 py-2 bg-brand-accent/10 text-brand-accent hover:bg-brand-accent hover:text-white rounded-lg text-sm font-medium transition-all shrink-0"
                      >
                        <PlayCircle className="w-4 h-4" />
                        Take
                      </Link>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>

        {/* Recent Activities */}
        <div className="bg-[#111]/80 backdrop-blur-sm border border-[#222] rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-5">Recent Activity</h2>
          {attempts.length === 0 ? (
            <div className="text-center py-10">
              <Target className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500">No quiz attempts yet.</p>
              <p className="text-gray-600 text-sm mt-1">Take your first quiz to get started!</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {attempts.map((attempt) => (
                <div key={attempt.id} className="flex items-center justify-between p-4 rounded-xl bg-[#0a0a0a] border border-[#1a1a1a]">
                  <div className="flex-1 min-w-0 mr-4">
                    <h3 className="font-semibold text-white truncate">{attempt.quiz_title || 'Quiz'}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                      <span className={`capitalize ${attempt.status === 'completed' ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {attempt.status}
                      </span>
                      {attempt.score !== null && attempt.score !== undefined && (
                        <>
                          <span>•</span>
                          <span className="text-brand-accent font-medium">{attempt.score}%</span>
                        </>
                      )}
                    </div>
                  </div>
                  {attempt.status === 'completed' && (
                    <Link
                      to={`/attempt/${attempt.id}/results`}
                      className="text-xs font-medium px-3 py-1.5 bg-[#222] hover:bg-[#333] rounded-lg text-gray-300 transition-colors border border-[#444]"
                    >
                      Results
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
