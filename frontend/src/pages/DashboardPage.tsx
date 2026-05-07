import { useSelector } from 'react-redux'
import { RootState } from '../store'

export default function DashboardPage() {
  const user = useSelector((state: RootState) => state.auth.user)

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Welcome, {user?.username}!
        </h1>
        <p className="text-gray-600">
          This is your Scrapling Web UI dashboard. More features coming soon.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">Total Tasks</h3>
          <p className="text-3xl font-bold text-gray-800 mt-2">0</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">Success Rate</h3>
          <p className="text-3xl font-bold text-gray-800 mt-2">0%</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">Total Data</h3>
          <p className="text-3xl font-bold text-gray-800 mt-2">0 B</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-500 text-sm font-medium">This Month</h3>
          <p className="text-3xl font-bold text-gray-800 mt-2">0</p>
        </div>
      </div>
    </div>
  )
}
