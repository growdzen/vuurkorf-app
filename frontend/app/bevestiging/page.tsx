"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function BevestigingContent() {
  const params = useSearchParams();
  const orderId = params.get("order_id");
  const name = params.get("name") || "klant";

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center px-4 py-20">
      <div className="max-w-xl w-full text-center">
        <div className="text-7xl mb-6">🎉</div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Bedankt, {decodeURIComponent(name)}!
        </h1>
        <p className="text-gray-500 text-lg mb-6">
          Uw bestelling is succesvol geplaatst. Wij nemen binnen 1 werkdag
          contact met u op voor betalingsinstructies en levertijd.
        </p>

        {orderId && (
          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6 mb-8">
            <p className="text-sm text-gray-500 mb-1">Bestelnummer</p>
            <p className="font-mono text-orange-700 font-semibold text-lg break-all">
              {orderId}
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Bewaar dit nummer voor uw administratie.
            </p>
          </div>
        )}

        <div className="bg-gray-50 rounded-2xl p-6 mb-8 text-left">
          <h2 className="font-semibold text-gray-800 mb-4">Wat gebeurt er nu?</h2>
          <ol className="space-y-3">
            {[
              "U ontvangt een bevestigingsmail met uw bestelnummer.",
              "Ons team controleert het snijbestand en neemt contact op.",
              "Na betaling starten wij met lasersnijden (levertijd: 5-10 werkdagen).",
              "Uw gepersonaliseerde vuurkorf wordt verzonden of afgehaald.",
            ].map((step, i) => (
              <li key={i} className="flex gap-3 text-sm text-gray-600">
                <span className="w-6 h-6 rounded-full bg-orange-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="border border-gray-300 text-gray-600 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 transition-colors"
          >
            Terug naar home
          </Link>
          <Link
            href="/configurator"
            className="bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-6 rounded-xl transition-colors"
          >
            Nog een vuurkorf configureren
          </Link>
        </div>

        <p className="text-sm text-gray-400 mt-8">
          Vragen?{" "}
          <a
            href="mailto:dennis@growdzen.com"
            className="text-orange-600 hover:underline"
          >
            dennis@growdzen.com
          </a>
        </p>
      </div>
    </div>
  );
}

export default function BevestigingPage() {
  return (
    <Suspense fallback={<div className="text-center py-20">Laden...</div>}>
      <BevestigingContent />
    </Suspense>
  );
}
