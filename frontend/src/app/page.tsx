export default function Home() {
  return (
    <div className="flex h-screen items-center justify-center bg-slate-950 text-white">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-cyan-400">
          The Comic OS
        </h1>
        <p className="text-slate-400 text-lg">
          Booting Design System...
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <a href="/legacy-playground" className="text-sm text-slate-500 hover:text-slate-300 transition underline">
            Legacy Playground
          </a>
          <a href="/dashboard" className="text-sm text-slate-500 hover:text-slate-300 transition underline">
            Old Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
