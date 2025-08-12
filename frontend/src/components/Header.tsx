import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-slate-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="flex items-center">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">V</span>
              </div>
              <h1 className="text-2xl font-bold text-white">
                Vera
              </h1>
            </div>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link 
              href="/" 
              className="text-slate-300 hover:text-white transition duration-200"
            >
              Analyze
            </Link>
            <Link 
              href="/predicate-search" 
              className="text-slate-300 hover:text-white transition duration-200"
            >
              Find Predicates
            </Link>
            <Link 
              href="/chat" 
              className="text-slate-300 hover:text-white transition duration-200"
            >
              Chat Assistant
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}