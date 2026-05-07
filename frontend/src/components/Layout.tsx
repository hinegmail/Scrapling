import { Outlet, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logout } from '../store/authSlice'
import { RootState } from '../store'
import { authAPI } from '../api/auth'

export default function Layout() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const user = useSelector((state: RootState) => state.auth.user)

  const handleLogout = async () => {
    try {
      await authAPI.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      dispatch(logout())
      navigate('/login')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Scrapling Web UI</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700">{user?.username}</span>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Sidebar and Main Content */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-800 text-white p-4">
          <nav className="space-y-2">
            <a
              href="/"
              className="block px-4 py-2 rounded hover:bg-gray-700"
            >
              Dashboard
            </a>
            <a
              href="/tasks"
              className="block px-4 py-2 rounded hover:bg-gray-700"
            >
              Tasks
            </a>
            <a
              href="/results"
              className="block px-4 py-2 rounded hover:bg-gray-700"
            >
              Results
            </a>
            <a
              href="/history"
              className="block px-4 py-2 rounded hover:bg-gray-700"
            >
              History
            </a>
            <a
              href="/settings"
              className="block px-4 py-2 rounded hover:bg-gray-700"
            >
              Settings
            </a>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
