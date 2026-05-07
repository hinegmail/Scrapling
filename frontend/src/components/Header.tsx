export default function Header() {
  return (
    <header className="bg-white shadow">
      <div className="px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Scrapling Web UI</h1>
        <div className="flex items-center space-x-4">
          <button className="text-gray-600 hover:text-gray-900">Settings</button>
          <button className="text-gray-600 hover:text-gray-900">Logout</button>
        </div>
      </div>
    </header>
  )
}
