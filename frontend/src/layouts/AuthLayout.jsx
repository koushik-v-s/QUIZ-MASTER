import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Cpu } from 'lucide-react';
import LiquidEther from '../components/LiquidEther';
import BorderGlow from '../components/BorderGlow';

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex text-brand-light bg-brand-dark">
      
      {/* Visual Side (Hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-black flex-col justify-center px-12 z-0">
        
        {/* LiquidEther animated background */}
        <LiquidEther 
          color1="#10b981" 
          color2="#3b82f6" 
          color3="#8b5cf6" 
          color4="#06b6d4" 
          speed={0.003} 
        />
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="z-10 relative"
        >
          <div className="flex items-center gap-3 mb-8">
            <Cpu className="w-12 h-12 text-brand-accent" />
            <h1 className="text-4xl font-bold tracking-tight">Teach Edison</h1>
          </div>
          
          <h2 className="text-5xl font-extrabold leading-tight mb-6">
            Intelligent Quizzes,<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-accent to-blue-500">
              Powered by AI.
            </span>
          </h2>
          
          <p className="text-lg text-gray-400 max-w-md">
            Generate complex multiple-choice questions instantly, track your performance, and master new topics with dynamic, real-time feedback.
          </p>
        </motion.div>
        
      </div>

      {/* Form Side */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#0a0a0a] border-l border-[#1a1a1a]">
        <div className="w-full max-w-md">
          {/* Mobile Header */}
          <div className="flex lg:hidden items-center gap-2 mb-10 justify-center">
            <Cpu className="w-8 h-8 text-brand-accent" />
            <span className="text-2xl font-bold">Teach Edison</span>
          </div>

          {/* BorderGlow wrapper around form */}
          <BorderGlow color="#10b981">
            <div className="p-8">
              <Outlet />
            </div>
          </BorderGlow>
          
        </div>
      </div>
      
    </div>
  );
}
