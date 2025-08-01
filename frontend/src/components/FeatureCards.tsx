const features = [
  {
    title: "AI-Powered Analysis",
    description: "Advanced language models analyze your predicate device documentation against FDA guidelines to determine substantial equivalence.",
    icon: "🤖"
  },
  {
    title: "Instant Results", 
    description: "Get comprehensive equivalence analysis in minutes, not weeks. Our system provides detailed reasoning and regulatory insights.",
    icon: "⚡"
  },
  {
    title: "Regulatory Compliance",
    description: "Built on official FDA 510(k) guidelines and best practices to ensure your analysis meets regulatory standards.",
    icon: "✅"
  }
];

export default function FeatureCards() {
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
              <p className="text-slate-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}