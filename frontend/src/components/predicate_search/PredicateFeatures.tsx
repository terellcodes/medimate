const features = [
  {
    title: "Intelligent Search",
    description: "Combine device keywords with FDA product codes for precise predicate discovery. Search by technology, indication, or manufacturer.",
    icon: "🔍"
  },
  {
    title: "Complete Device Data", 
    description: "Get comprehensive device metadata, clearance dates, document availability, and safety status from the official FDA database.",
    icon: "📊"
  },
  {
    title: "Official FDA Database",
    description: "Search directly from openFDA 510(k) database with real-time data covering devices from 1976 to present.",
    icon: "🏛️"
  }
];

export default function PredicateFeatures() {
  return (
    <section className="py-16 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="text-center p-8 bg-white rounded-xl border border-slate-200 hover:shadow-xl transition duration-300 hover:border-green-300">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-slate-800 mb-4">
                {feature.title}
              </h3>
              <p className="text-slate-800 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}