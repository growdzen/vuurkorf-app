import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-140px)]">
      {/* Hero */}
      <section className="bg-gradient-to-br from-gray-900 via-gray-800 to-orange-900 text-white py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="text-6xl mb-6">🔥</div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            Uw eigen motief
            <span className="text-orange-400"> in metaal</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-2xl mx-auto">
            Upload een foto en wij zetten het om naar een uniek lasersnijpatroon
            voor uw vuurkorf.
          </p>
          <p className="text-gray-400 mb-10 max-w-xl mx-auto">
            AI verwerkt uw afbeelding automatisch tot een scherp silhouet.
            Kies uw materiaal, bekijk de preview en bestel direct online.
          </p>
          <Link
            href="/configurator"
            className="inline-block bg-orange-600 hover:bg-orange-500 text-white font-bold py-4 px-10 rounded-xl text-lg transition-all duration-150 shadow-lg hover:shadow-xl hover:-translate-y-0.5"
          >
            Start configurator
          </Link>
        </div>
      </section>

      {/* Steps */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-14">
            Hoe werkt het?
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              {
                icon: "🎨",
                title: "Kies materiaal",
                desc: "Cortenstaal, RVS of zwart staal — in 2, 3, 4 of 6mm dikte.",
              },
              {
                icon: "📷",
                title: "Upload foto",
                desc: "Elk JPG, PNG of WEBP-bestand tot 20MB. Portret, dier, logo — alles kan.",
              },
              {
                icon: "🤖",
                title: "AI verwerking",
                desc: "Onze AI verwijdert de achtergrond en maakt een schoon vectorsilhouet.",
              },
              {
                icon: "✅",
                title: "Bestel & ontvang",
                desc: "Bekijk de preview, pas aan en bestel. Wij snijden en leveren.",
              },
            ].map((step, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl mb-4">{step.icon}</div>
                <div className="w-8 h-8 rounded-full bg-orange-600 text-white text-sm font-bold flex items-center justify-center mx-auto mb-3">
                  {i + 1}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-500 text-sm">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Materials */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-14">
            Beschikbare materialen
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                name: "Cortenstaal",
                price: "v.a. €89",
                desc: "Roestig patina, tijdloos karakter. Ideaal voor buiten.",
                color: "bg-amber-50 border-amber-200",
              },
              {
                name: "RVS",
                price: "v.a. €149",
                desc: "Glanzend en weerbestendig. Modern en strak.",
                color: "bg-slate-50 border-slate-200",
              },
              {
                name: "Zwart staal",
                price: "v.a. €69",
                desc: "Klassiek mat zwart. Strak en betaalbaar.",
                color: "bg-gray-50 border-gray-300",
              },
            ].map((mat, i) => (
              <div
                key={i}
                className={`border-2 rounded-xl p-6 ${mat.color}`}
              >
                <h3 className="font-bold text-gray-900 text-lg mb-1">
                  {mat.name}
                </h3>
                <p className="text-orange-600 font-semibold mb-3">
                  {mat.price}
                </p>
                <p className="text-gray-600 text-sm">{mat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-orange-600 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">
          Klaar om uw vuurkorf te personaliseren?
        </h2>
        <p className="text-orange-100 mb-8 max-w-md mx-auto">
          Het duurt slechts een paar minuten. Geen account nodig.
        </p>
        <Link
          href="/configurator"
          className="inline-block bg-white text-orange-600 font-bold py-4 px-10 rounded-xl text-lg hover:bg-orange-50 transition-colors shadow-lg"
        >
          Start nu &rarr;
        </Link>
      </section>
    </div>
  );
}
