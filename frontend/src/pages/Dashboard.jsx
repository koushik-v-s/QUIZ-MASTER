import { useAuthStore } from '../store/auth';
import AdminDashboard from './AdminDashboard';
import UserDashboard from './UserDashboard';

/**
 * Role-aware Dashboard router.
 * Admins see the platform management overview.
 * Users see their learning progress and available quizzes.
 */
export default function Dashboard() {
  const { user } = useAuthStore();

  if (user?.role === 'admin') {
    return <AdminDashboard />;
  }

  return <UserDashboard />;
}
