import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/auth';
import { Toaster } from 'react-hot-toast';
import ClickSpark from './components/ClickSpark';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

import Dashboard from './pages/Dashboard';
import CreateQuiz from './pages/CreateQuiz';
import TakeQuiz from './pages/TakeQuiz';
import Results from './pages/Results';
import Analytics from './pages/Analytics';
import AdminPanel from './pages/AdminPanel';
import QuizPreview from './pages/QuizPreview';

// Protected Route Component
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, user, isLoading } = useAuthStore();

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen bg-brand-dark text-brand-accent">Loading...</div>;
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requireAdmin && user?.role !== 'admin') return <Navigate to="/" replace />;
  
  return children;
};

// Public Route (Login/Register - bypass if already logged in)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) return <div>Loading...</div>;
  if (isAuthenticated) return <Navigate to="/" replace />;
  
  return children;
};

function App() {
  return (
    <ClickSpark sparkColor="#10b981" sparkSize={12} sparkRadius={20} sparkCount={10} duration={500}>
      <div className="min-h-screen bg-brand-dark text-brand-light font-sans selection:bg-brand-accent/30 selection:text-brand-accent">
        <Toaster position="top-right" toastOptions={{
          style: { background: '#1a1a1a', color: '#f3f4f6', border: '1px solid #333' }
        }} />
        
        <Routes>
          {/* Auth Routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          </Route>

          {/* Dashboard & App Routes */}
          <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quiz/:id/take" element={<TakeQuiz />} />
            <Route path="/quiz/:id/preview" element={
              <ProtectedRoute requireAdmin={true}>
                <QuizPreview />
              </ProtectedRoute>
            } />
            <Route path="/attempt/:id/results" element={<Results />} />
            <Route path="/analytics" element={<Analytics />} />
            
            {/* Admin Routes */}
            <Route path="/create-quiz" element={
              <ProtectedRoute requireAdmin={true}>
                <CreateQuiz />
              </ProtectedRoute>
            } />
            
            {/* Admin Routes */}
            <Route path="/admin/*" element={
              <ProtectedRoute requireAdmin={true}>
                <AdminPanel />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </div>
    </ClickSpark>
  );
}

export default App;
