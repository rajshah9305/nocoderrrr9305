function Console({ logs }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <div className="font-mono text-sm text-gray-300">
        {logs.map((log, index) => (
          <div key={index} className="py-1">
            {log}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Console
