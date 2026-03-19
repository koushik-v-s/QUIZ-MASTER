import { useState } from 'react';
import { useAuthStore } from '../../store/auth';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, Mail, Lock, Loader2, Eye, EyeOff, Zap } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const login = useAuthStore(state => state.login);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await login(email, password);
    setLoading(false);
    if (success) {
      navigate('/');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full"
    >
      {/* Header */}
      <div className="mb-10 text-center lg:text-left">
        <motion.div 
          initial={{ scale: 0.8, opacity: 0 }} 
          animate={{ scale: 1, opacity: 1 }} 
          transition={{ delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-accent/10 border border-brand-accent/20 mb-5"
        >
          <Zap className="w-3.5 h-3.5 text-brand-accent" />
          <span className="text-xs font-semibold text-brand-accent uppercase tracking-wider">Secure Access</span>
        </motion.div>

        <h2 className="text-4xl font-extrabold mb-3 tracking-tight">
          Welcome <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-accent to-emerald-300">Back</span>
        </h2>
        <p className="text-gray-400 text-base">Sign in to continue your learning journey.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">Email Address</label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-accent transition-colors">
              <Mail className="h-5 w-5" />
            </div>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="block w-full pl-12 pr-4 py-3.5 border border-[#2a2a2a] rounded-xl bg-[#0d0d0d] text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-accent/50 focus:border-brand-accent transition-all"
              placeholder="you@example.com"
              required
            />
          </div>
        </div>

        {/* Password with toggle */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">Password</label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-accent transition-colors">
              <Lock className="h-5 w-5" />
            </div>
            <input
              id="login-password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="block w-full pl-12 pr-12 py-3.5 border border-[#2a2a2a] rounded-xl bg-[#0d0d0d] text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-accent/50 focus:border-brand-accent transition-all"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-gray-300 transition-colors"
            >
              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Submit */}
        <motion.button
          type="submit"
          disabled={loading}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          className="w-full flex justify-center items-center gap-2 py-4 px-4 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-brand-accent to-emerald-600 hover:from-emerald-600 hover:to-brand-accent shadow-[0_0_25px_rgba(16,185,129,0.25)] hover:shadow-[0_0_35px_rgba(16,185,129,0.35)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Sign In
              <LogIn className="w-4 h-4" />
            </>
          )}
        </motion.button>
      </form>

      {/* Divider */}
      <div className="relative my-8">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#222]" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-[#0a0a0a] px-4 text-xs text-gray-500 uppercase tracking-wider">New here?</span>
        </div>
      </div>

      {/* Register Link */}
      <div className="text-center">
        <Link 
          to="/register" 
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-[#2a2a2a] text-gray-300 hover:text-white hover:border-brand-accent/50 hover:bg-brand-accent/5 transition-all duration-300 font-medium text-sm"
        >
          Create a free account
          <span className="text-brand-accent">→</span>
        </Link>
      </div>
    </motion.div>
  );
}
