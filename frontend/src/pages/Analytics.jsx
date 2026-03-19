import { useState, useEffect } from 'react';
import api from '../lib/axios';
import { motion } from 'framer-motion';
import { Loader2, TrendingUp, Award, BarChart4 } from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';

export default function Analytics() {
  const [history, setHistory] = useState([]);
  const [topics, setTopics] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('performance'); // performance | leaderboard

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [historyRes, topicsRes, leaderboardRes] = await Promise.all([
          api.get('/analytics/history/'),
          api.get('/analytics/topics/'),
          api.get('/analytics/leaderboard/')
        ]);
        
        // Format dates for the chart
        const formattedHistory = historyRes.data.data.map(item => ({
          ...item,
          displayDate: new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        }));
        
        setHistory(formattedHistory);
        setTopics(topicsRes.data.data);
        setLeaderboard(leaderboardRes.data.data);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-10 h-10 animate-spin text-brand-accent" /></div>;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#111] border border-[#333] p-4 rounded-xl shadow-xl">
          <p className="text-gray-400 mb-1">{label}</p>
          <p className="text-white font-bold text-lg">{payload[0].value}%</p>
          {payload[0].payload.quiz_title && (
            <p className="text-brand-accent text-sm mt-1">{payload[0].payload.quiz_title}</p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-6xl mx-auto py-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <BarChart4 className="w-8 h-8 text-brand-accent" /> Analytics Hub
          </h1>
          <p className="text-gray-400 mt-2">Track your progress, identify weaknesses, and see how you rank.</p>
        </div>
        
        <div className="flex bg-[#111] p-1 rounded-xl border border-[#222]">
          <button 
            onClick={() => setActiveTab('performance')}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${activeTab === 'performance' ? 'bg-[#222] text-white shadow' : 'text-gray-400 hover:text-white'}`}
          >
            My Performance
          </button>
          <button 
            onClick={() => setActiveTab('leaderboard')}
            className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${activeTab === 'leaderboard' ? 'bg-[#222] text-white shadow' : 'text-gray-400 hover:text-white'}`}
          >
            Global Ranking
          </button>
        </div>
      </div>

      {activeTab === 'performance' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
          
          {/* Main Chart */}
          <div className="bg-[#111] p-6 md:p-8 rounded-2xl border border-[#222]">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <TrendingUp className="text-blue-400 w-5 h-5" /> Recent Score History
            </h2>
            
            {history.length > 0 ? (
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
                    <XAxis dataKey="displayDate" stroke="#666" tick={{ fill: '#666' }} axisLine={false} tickLine={false} />
                    <YAxis stroke="#666" tick={{ fill: '#666' }} axisLine={false} tickLine={false} domain={[0, 100]} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="score" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 border border-dashed border-[#333] rounded-xl">
                Not enough data. Take a quiz to generate your progress chart.
              </div>
            )}
          </div>

          {/* Topics Chart */}
          <div className="bg-[#111] p-6 md:p-8 rounded-2xl border border-[#222]">
            <h2 className="text-xl font-bold mb-6">Topic Mastery</h2>
            
            {topics.length > 0 ? (
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topics} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#222" horizontal={true} vertical={false} />
                    <XAxis type="number" domain={[0, 100]} stroke="#666" tick={{ fill: '#666' }} />
                    <YAxis dataKey="topic" type="category" stroke="#ccc" tick={{ fill: '#ccc', fontSize: 13 }} width={120} />
                    <RechartsTooltip cursor={{ fill: '#1a1a1a' }} content={<CustomTooltip />} />
                    <Bar dataKey="average_score" fill="#3b82f6" radius={[0, 4, 4, 0]} maxBarSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 border border-dashed border-[#333] rounded-xl">
                Topics will appear here after you complete quizzes.
              </div>
            )}
          </div>

        </motion.div>
      )}

      {activeTab === 'leaderboard' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
            <div className="p-6 border-b border-[#222] flex items-center justify-between">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Award className="text-amber-400 w-6 h-6" /> Top Performers
              </h2>
              <span className="text-sm text-gray-400">Requires min 3 quizzes</span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-[#1a1a1a] text-xs uppercase text-gray-400">
                  <tr>
                    <th className="px-6 py-4 rounded-tl-xl font-semibold">Rank</th>
                    <th className="px-6 py-4 font-semibold">User</th>
                    <th className="px-6 py-4 font-semibold text-center">Quizzes Taken</th>
                    <th className="px-6 py-4 font-semibold text-center">Avg Score</th>
                    <th className="px-6 py-4 rounded-tr-xl font-semibold text-right">Rating</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#222]">
                  {leaderboard.map((user, index) => (
                    <tr key={index} className="hover:bg-[#161616] transition-colors">
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                          index === 0 ? 'bg-amber-500/20 text-amber-500' : 
                          index === 1 ? 'bg-gray-300/20 text-gray-300' : 
                          index === 2 ? 'bg-amber-700/20 text-amber-600' : 'bg-[#222] text-gray-400'
                        }`}>
                          {index + 1}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-medium text-white">{user.username}</td>
                      <td className="px-6 py-4 text-center text-gray-300">{user.total_quizzes_taken}</td>
                      <td className="px-6 py-4 text-center">
                        <span className={`font-semibold ${user.average_score >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {user.average_score.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right font-mono font-bold text-brand-accent">
                        {user.overall_rating}
                      </td>
                    </tr>
                  ))}
                  {leaderboard.length === 0 && (
                    <tr>
                      <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                        Not enough users have qualified for the leaderboard yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
