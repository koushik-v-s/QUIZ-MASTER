import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import api from '../lib/axios';
import { Link } from 'react-router-dom';
import { 
  Users, Database, Activity, TrendingUp, PlusCircle, 
  BrainCircuit, AlertTriangle, CheckCircle2, Loader2, 
  BarChart3, Sparkles, RefreshCw, Eye, Trash2
} from 'lucide-react';
import ElectricBorder from '../components/ElectricBorder';
import toast from 'react-hot-toast';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [myQuizzes, setMyQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statsRes, quizzesRes] = await Promise.all([
        api.get('/admin/stats/'),
        api.get('/quizzes/my/')
      ]);
      setStats(statsRes.data.data);
      setMyQuizzes(quizzesRes.data.data?.results || quizzesRes.data.data || []);
    } catch (err) {
      console.error('Admin dashboard load failed', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteQuiz = async (quizId, quizTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${quizTitle}"? This cannot be undone.`)) return;
    try {
      await api.delete(`/quizzes/${quizId}/`);
      toast.success('Quiz deleted successfully');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to delete quiz');
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-[60vh]">
      <Loader2 className="w-10 h-10 animate-spin text-brand-accent" />
    </div>
  );

  const StatCard = ({ icon: Icon, label, value, color, borderColor }) => (
    <ElectricBorder color={borderColor || '#10b981'}>
      <motion.div 
        whileHover={{ y: -4, scale: 1.01 }}
        className="p-6 flex items-center gap-5 transition-all"
      >
        <div className={`p-4 rounded-xl ${color}`}>
          <Icon className="w-7 h-7" />
        </div>
        <div>
          <p className="text-gray-400 text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-0.5">{value}</p>
        </div>
      </motion.div>
    </ElectricBorder>
  );

  const statusColor = (s) => {
    if (s === 'ready') return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (s === 'generating') return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-red-400 bg-red-500/10 border-red-500/30';
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Activity className="w-8 h-8 text-brand-accent" />
            Admin Dashboard
          </h1>
          <p className="text-gray-400 mt-1">Platform overview and quiz management at a glance.</p>
        </div>
        <Link 
          to="/create-quiz" 
          className="flex items-center gap-2 bg-brand-accent hover:bg-emerald-600 text-white px-5 py-2.5 rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(16,185,129,0.2)] w-fit"
        >
          <PlusCircle className="w-5 h-5" />
          Generate New Quiz
        </Link>
      </div>

      {/* Platform Stats Grid — ElectricBorder */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard icon={Users} label="Total Users" value={stats?.total_users || 0} color="bg-blue-500/15 text-blue-400" borderColor="#3b82f6" />
        <StatCard icon={Database} label="Total Quizzes" value={stats?.total_quizzes || 0} color="bg-purple-500/15 text-purple-400" borderColor="#8b5cf6" />
        <StatCard icon={BarChart3} label="Total Attempts" value={stats?.total_attempts || 0} color="bg-emerald-500/15 text-emerald-400" borderColor="#10b981" />
        <StatCard icon={TrendingUp} label="Avg Platform Score" value={`${stats?.average_score ? stats.average_score.toFixed(1) : 0}%`} color="bg-amber-500/15 text-amber-400" borderColor="#f59e0b" />
      </div>

      {/* AI Pipeline + Recent Quizzes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* AI Pipeline — Ready & Failed only */}
        <div className="bg-[#111]/80 backdrop-blur-sm border border-[#222] rounded-2xl p-6">
          <h2 className="text-lg font-bold mb-5 flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-brand-accent" />
            AI Pipeline
          </h2>
          <div className="space-y-4">
            <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-5 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <span className="text-gray-300 font-medium">Ready</span>
              </div>
              <span className="text-2xl font-bold text-emerald-400">{stats?.quizzes_by_status?.ready || 0}</span>
            </div>
            <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-5 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <span className="text-gray-300 font-medium">Failed</span>
              </div>
              <span className="text-2xl font-bold text-red-400">{stats?.quizzes_by_status?.failed || 0}</span>
            </div>
          </div>
        </div>

        {/* My Recent Quizzes — with Preview button */}
        <div className="lg:col-span-2 bg-[#111]/80 backdrop-blur-sm border border-[#222] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-bold">My Recent Quizzes</h2>
            <button onClick={fetchData} className="text-gray-500 hover:text-gray-300 transition-colors">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          
          {myQuizzes.length === 0 ? (
            <div className="text-center py-12">
              <BrainCircuit className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500">No quizzes generated yet.</p>
              <Link to="/create-quiz" className="text-brand-accent hover:underline text-sm mt-2 inline-block">
                Create your first quiz →
              </Link>
            </div>
          ) : (
            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {myQuizzes.slice(0, 8).map((quiz) => (
                <div 
                  key={quiz.id} 
                  className="flex items-center justify-between p-4 rounded-xl bg-[#0a0a0a] border border-[#1a1a1a] hover:border-[#333] transition-colors"
                >
                  <div className="flex-1 min-w-0 mr-4">
                    <h3 className="font-semibold text-white truncate">{quiz.title}</h3>
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                      <span>{quiz.topic}</span>
                      <span>•</span>
                      <span className="capitalize">{quiz.difficulty}</span>
                      <span>•</span>
                      <span>{quiz.question_count} Qs</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 text-xs font-medium rounded-full border ${statusColor(quiz.status)}`}>
                      {quiz.status === 'ready' && <CheckCircle2 className="w-3 h-3 inline mr-1" />}
                      {quiz.status}
                    </span>
                    {quiz.status === 'ready' && (
                      <Link
                        to={`/quiz/${quiz.id}/preview`}
                        className="flex items-center gap-1 px-3 py-1.5 bg-brand-accent/10 text-brand-accent hover:bg-brand-accent hover:text-white rounded-lg text-xs font-medium transition-all"
                      >
                        <Eye className="w-3 h-3" />
                        View
                      </Link>
                    )}
                    <button
                      onClick={() => handleDeleteQuiz(quiz.id, quiz.title)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white rounded-lg text-xs font-medium transition-all"
                    >
                      <Trash2 className="w-3 h-3" />
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
