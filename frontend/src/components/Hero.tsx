interface HeroProps {
  onTryNowClick: () => void;
}

export default function Hero({ onTryNowClick }: HeroProps) {
  return (
    <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 py-20 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-6">
            Streamline Your 510(k) Process
          </h1>
          <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            Vera uses AI-powered analysis to help medical device companies 
            determine substantial equivalence faster and more accurately. Upload your 
            predicate device documentation and get instant regulatory insights.
          </p>
          <button 
            onClick={onTryNowClick}
            className="bg-blue-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-600 transition duration-200 shadow-xl border border-blue-400"
          >
            Get Started
          </button>
        </div>
      </div>
    </section>
  );
}