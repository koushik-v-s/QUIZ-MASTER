import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import { LayoutDashboard, PlusCircle, BarChart3, Settings, LogOut, Cpu } from 'lucide-react';
import MagicBento from '../components/MagicBento';
import LiquidEther from '../components/LiquidEther';

export default function MainLayout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  ];

  if (user?.role === 'admin') {
    navItems.push({ name: 'Create Quiz', path: '/create-quiz', icon: PlusCircle });
    navItems.push({ name: 'Admin Panel', path: '/admin', icon: Settings });
  } else {
    navItems.push({ name: 'Analytics', path: '/analytics', icon: BarChart3 });
  }

  const isActive = (path) => location.pathname === path || (path !== '/' && location.pathname.startsWith(path));

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-brand-dark flex flex-col relative">
      
      {/* LiquidEther Background — mouse-following */}
      <LiquidEther 
        color1="#10b981" 
        color2="#3b82f6" 
        color3="#7c3aed" 
        color4="#06b6d4" 
        speed={0.002} 
      />

      {/* Top Navigation Bar — MagicBento */}
      <div className="sticky top-0 z-50 px-4 pt-3">
        <MagicBento glowColor="#10b981" className="w-full">
          <div className="flex items-center justify-between px-6 py-3">
            
            {/* Brand */}
            <Link to="/" className="flex items-center gap-2.5 shrink-0">
              <Cpu className="text-brand-accent w-7 h-7" />
              <span className="font-bold text-xl tracking-wide text-white hidden sm:inline">Teach Edison</span>
            </Link>

            {/* Nav Links — centered */}
            <nav className="flex items-center gap-1.5">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                      active
                        ? 'bg-brand-accent/15 text-brand-accent shadow-[0_0_12px_rgba(16,185,129,0.15)]'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden md:inline">{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* User + Logout */}
            <div className="flex items-center gap-3 shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-brand-accent/20 flex items-center justify-center text-brand-accent font-bold text-sm border border-brand-accent/30">
                  {user?.username?.[0]?.toUpperCase()}
                </div>
                <div className="hidden lg:block">
                  <p className="text-sm font-medium text-white leading-none">{user?.username}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{user?.role}</p>
                </div>
              </div>
              <button 
                onClick={handleLogout}
                className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </MagicBento>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 relative z-10 p-4 md:p-8">
        <Outlet />
      </div>
    </div>
  );
}
