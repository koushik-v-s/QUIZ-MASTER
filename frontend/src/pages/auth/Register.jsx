import { useState } from 'react';
import { useAuthStore } from '../../store/auth';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User, Loader2, Eye, EyeOff, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Register() {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const register = useAuthStore(state => state.register);
  const navigate = useNavigate();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    const success = await register(formData.username, formData.email, formData.password);
    setLoading(false);
    
    if (success) navigate('/');
  };

  // Password strength indicator
  const getPasswordStrength = (pwd) => {
    if (!pwd) return { level: 0, label: '', color: '' };
    let score = 0;
    if (pwd.length >= 8) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    
    if (score <= 1) return { level: 1, label: 'Weak', color: 'bg-red-500' };
    if (score === 2) return { level: 2, label: 'Fair', color: 'bg-amber-500' };
    if (score === 3) return { level: 3, label: 'Good', color: 'bg-blue-500' };
    return { level: 4, label: 'Strong', color: 'bg-emerald-500' };
  };

  const strength = getPasswordStrength(formData.password);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full"
    >
      {/* Header */}
      <div className="mb-8 text-center lg:text-left">
        <motion.div 
          initial={{ scale: 0.8, opacity: 0 }} 
          animate={{ scale: 1, opacity: 1 }} 
          transition={{ delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 mb-5"
        >
          <Shield className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Free Account</span>
        </motion.div>

        <h2 className="text-4xl font-extrabold mb-3 tracking-tight">
          Join <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-brand-accent">Edison</span>
        </h2>
        <p className="text-gray-400 text-base">Create your account and start generating AI quizzes.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Username */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">Username</label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-accent transition-colors">
              <User className="h-5 w-5" />
            </div>
            <input
              id="register-username"
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="block w-full pl-12 pr-4 py-3.5 border border-[#2a2a2a] rounded-xl bg-[#0d0d0d] text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-accent/50 focus:border-brand-accent transition-all"
              placeholder="johndoe"
              required
              minLength={3}
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">Email Address</label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-accent transition-colors">
              <Mail className="h-5 w-5" />
            </div>
            <input
              id="register-email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
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
              id="register-password"
              type={showPassword ? 'text' : 'password'}
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="block w-full pl-12 pr-12 py-3.5 border border-[#2a2a2a] rounded-xl bg-[#0d0d0d] text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-accent/50 focus:border-brand-accent transition-all"
              placeholder="Min. 8 characters"
              required
              minLength={8}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-gray-300 transition-colors"
            >
              {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
            </button>
          </div>

          {/* Password strength bar */}
          {formData.password && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }} 
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2.5"
            >
              <div className="flex gap-1.5 mb-1.5">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                      i <= strength.level ? strength.color : 'bg-[#222]'
                    }`}
                  />
                ))}
              </div>
              <p className={`text-xs font-medium ${strength.color.replace('bg-', 'text-')}`}>
                {strength.label}
              </p>
            </motion.div>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">Confirm Password</label>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 group-focus-within:text-brand-accent transition-colors">
              <Lock className="h-5 w-5" />
            </div>
            <input
              id="register-confirm-password"
              type={showConfirmPassword ? 'text' : 'password'}
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={`block w-full pl-12 pr-12 py-3.5 border rounded-xl bg-[#0d0d0d] text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-accent/50 transition-all ${
                formData.confirmPassword && formData.confirmPassword !== formData.password
                  ? 'border-red-500/50 focus:border-red-500'
                  : formData.confirmPassword && formData.confirmPassword === formData.password
                  ? 'border-emerald-500/50 focus:border-emerald-500'
                  : 'border-[#2a2a2a] focus:border-brand-accent'
              }`}
              placeholder="Repeat your password"
              required
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-gray-300 transition-colors"
            >
              {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
            </button>
          </div>
          {formData.confirmPassword && formData.confirmPassword !== formData.password && (
            <p className="text-xs text-red-400 mt-1.5">Passwords don't match</p>
          )}
        </div>

        {/* Submit */}
        <div className="pt-2">
          <motion.button
            type="submit"
            disabled={loading || (formData.password !== formData.confirmPassword && formData.confirmPassword !== '')}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            className="w-full flex justify-center items-center gap-2 py-4 px-4 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-blue-500 to-brand-accent hover:from-blue-600 hover:to-emerald-600 shadow-[0_0_25px_rgba(59,130,246,0.2)] hover:shadow-[0_0_35px_rgba(59,130,246,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Create Account
                <UserPlus className="w-4 h-4" />
              </>
            )}
          </motion.button>
        </div>
      </form>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#222]" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-[#0a0a0a] px-4 text-xs text-gray-500 uppercase tracking-wider">Already a member?</span>
        </div>
      </div>

      {/* Login Link */}
      <div className="text-center">
        <Link 
          to="/login" 
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-[#2a2a2a] text-gray-300 hover:text-white hover:border-blue-500/50 hover:bg-blue-500/5 transition-all duration-300 font-medium text-sm"
        >
          Sign in to your account
          <span className="text-blue-400">→</span>
        </Link>
      </div>
    </motion.div>
  );
}
