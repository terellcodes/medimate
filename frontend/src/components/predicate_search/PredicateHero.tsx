interface PredicateHeroProps {
  onTryNowClick: () => void;
}

export default function PredicateHero({ onTryNowClick }: PredicateHeroProps) {
  return (
    <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-green-900 py-20 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-6">
            Find Your Perfect Predicate Device
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            Search FDA&apos;s comprehensive 510(k) database with AI-powered precision to discover 
            the ideal predicate devices for your substantial equivalence analysis. Access 
            official device classifications and download PDFs instantly.
          </p>
          <button 
            onClick={onTryNowClick}
            className="bg-green-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-green-600 transition duration-200 shadow-xl border border-green-400"
          >
            Start Searching
          </button>
        </div>
      </div>
    </section>
  );
}