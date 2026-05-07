import { Link } from 'react-router-dom'

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 text-white">
      <div className="p-6">
        <h2 className="text-xl font-bold">Menu</h2>
      </div>
      <nav className="space-y-2 px-4">
        <Link to="/" className="block px-4 py-2 rounded hover:bg-gray-700">
          Dashboard
        </Link>
        <Link to="/tasks" className="block px-4 py-2 rounded hover:bg-gray-700">
          Tasks
        </Link>
        <Link to="/results" className="block px-4 py-2 rounded hover:bg-gray-700">
          Results
        </Link>
        <Link to="/history" className="block px-4 py-2 rounded hover:bg-gray-700">
          History
        </Link>
      </nav>
    </aside>
  )
}
