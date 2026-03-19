import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../lib/axios';
import { 
  Users, Activity, Loader2, ShieldAlert,
  Search, Shield, Edit2, AlertCircle, Database, Server, Settings, BarChart, X, Target, Trophy, Clock
} from 'lucide-react';

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('overview');
  const [leaderboards, setLeaderboards] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'overview') {
        const { data } = await api.get('/admin/stats/');
        setStats(data.data);
      } else if (activeTab === 'leaderboards') {
        const { data } = await api.get('/admin/leaderboards/');
        setLeaderboards(data.data || []);
      }
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Platform Overview', icon: Activity },
    { id: 'leaderboards', label: 'Quiz Leaderboards', icon: Trophy },
  ];

  return (
    <div className="max-w-7xl mx-auto py-8">
      <div className="flex items-center gap-3 mb-8">
        <ShieldAlert className="w-8 h-8 text-brand-accent" />
        <div>
          <h1 className="text-3xl font-bold text-white">System Administration</h1>
          <p className="text-gray-400 mt-1">Manage platform settings, leaderboards, and view detailed analytics.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex overflow-x-auto hide-scrollbar gap-2 mb-8 bg-[#111] p-2 rounded-2xl border border-[#222]">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${
                isActive 
                  ? 'bg-brand-accent text-white shadow-lg shadow-brand-accent/20' 
                  : 'text-gray-400 hover:text-white hover:bg-[#222]'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="min-h-[500px]">
        {loading ? (
          <div className="flex items-center justify-center h-[400px]">
            <Loader2 className="w-10 h-10 animate-spin text-brand-accent" />
          </div>
        ) : (
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="bg-[#111] border border-[#222] rounded-2xl p-8">
                  <h2 className="text-xl font-bold mb-6">AI Generation Pipeline</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-6 rounded-xl">
                      <p className="text-gray-400 font-medium mb-2">Quizzes Ready</p>
                      <p className="text-4xl font-bold text-emerald-400">{stats?.quizzes_by_status?.ready || 0}</p>
                    </div>
                    <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-6 rounded-xl">
                      <p className="text-gray-400 font-medium mb-2">Generation Failures</p>
                      <p className="text-4xl font-bold text-red-500">{stats?.quizzes_by_status?.failed || 0}</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#111] border border-[#222] rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400"><Users className="w-6 h-6" /></div>
                      <h3 className="font-semibold">User Base</h3>
                    </div>
                    <p className="text-3xl font-bold">{stats?.total_users || 0}</p>
                    <p className="text-gray-500 text-sm mt-1">Total registered users</p>
                  </div>
                  
                  <div className="bg-[#111] border border-[#222] rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 bg-purple-500/10 rounded-lg text-purple-400"><Database className="w-6 h-6" /></div>
                      <h3 className="font-semibold">Content Library</h3>
                    </div>
                    <p className="text-3xl font-bold">{stats?.total_quizzes || 0}</p>
                    <p className="text-gray-500 text-sm mt-1">Total quizzes generated</p>
                  </div>

                  <div className="bg-[#111] border border-[#222] rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400"><Target className="w-6 h-6" /></div>
                      <h3 className="font-semibold">Engagement</h3>
                    </div>
                    <p className="text-3xl font-bold">{stats?.total_attempts || 0}</p>
                    <p className="text-gray-500 text-sm mt-1">Total quiz attempts</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'leaderboards' && (
              <div className="space-y-8">
                {leaderboards.length === 0 ? (
                  <div className="bg-[#111] border border-[#222] rounded-2xl p-12 text-center">
                    <Trophy className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">No Leaderboards Yet</h3>
                    <p className="text-gray-500">When users complete the quizzes you generate, their scores will appear here.</p>
                  </div>
                ) : (
                  leaderboards.map((quiz) => (
                    <div key={quiz.quiz_id} className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
                      {/* Quiz Header */}
                      <div className="p-6 bg-[#151515] border-b border-[#222] flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                          <h3 className="text-xl font-bold text-white">{quiz.quiz_title}</h3>
                          <div className="flex items-center gap-3 mt-2 text-sm text-gray-400">
                            <span className="capitalize">{quiz.difficulty}</span>
                            <span>•</span>
                            <span>{quiz.topic}</span>
                            <span>•</span>
                            <span>{quiz.question_count} Qs</span>
                          </div>
                        </div>
                        <div className="bg-[#0a0a0a] border border-[#222] px-4 py-2 rounded-xl flex items-center gap-2">
                          <Users className="w-4 h-4 text-brand-accent" />
                          <span className="font-medium text-white">{quiz.total_attempts} Attempts</span>
                        </div>
                      </div>

                      {/* Leaderboard Table */}
                      <div className="p-0 overflow-x-auto">
                        {quiz.leaderboard.length === 0 ? (
                          <div className="p-8 text-center text-gray-500 text-sm">No attempts yet.</div>
                        ) : (
                          <table className="w-full text-left border-collapse">
                            <thead>
                              <tr className="border-b border-[#222] bg-[#0a0a0a]/50 text-gray-500 text-sm">
                                <th className="p-4 font-medium pl-6">Rank</th>
                                <th className="p-4 font-medium">User</th>
                                <th className="p-4 font-medium">Score</th>
                                <th className="p-4 font-medium">Completed Date</th>
                              </tr>
                            </thead>
                            <tbody>
                              {quiz.leaderboard.map((entry, idx) => (
                                <tr 
                                  key={idx} 
                                  className="border-b border-[#1a1a1a] last:border-0 hover:bg-[#1a1a1a] transition-colors"
                                >
                                  <td className="p-4 pl-6">
                                    <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
                                      entry.rank === 1 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                                      entry.rank === 2 ? 'bg-gray-300/20 text-gray-300 border border-gray-400/30' :
                                      entry.rank === 3 ? 'bg-orange-700/20 text-orange-400 border border-orange-700/30' :
                                      'text-gray-500 bg-[#222]'
                                    }`}>
                                      {entry.rank}
                                    </div>
                                  </td>
                                  <td className="p-4">
                                    <div className="flex items-center gap-3">
                                      <div className="w-8 h-8 rounded-full bg-brand-accent/20 flex items-center justify-center text-brand-accent font-bold text-sm">
                                        {entry.username.charAt(0).toUpperCase()}
                                      </div>
                                      <div>
                                        <p className="font-semibold text-white">{entry.username}</p>
                                        <p className="text-xs text-gray-500">{entry.email}</p>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="p-4">
                                    <span className={`font-bold ${entry.score >= 80 ? 'text-emerald-400' : entry.score >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                                      {entry.score}%
                                    </span>
                                  </td>
                                  <td className="p-4 text-sm text-gray-400">
                                    {new Date(entry.completed_at).toLocaleDateString()}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
