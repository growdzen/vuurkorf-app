import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vuurkorf Personalisatie | Growdzen",
  description:
    "Ontwerp uw gepersonaliseerde vuurkorf. Upload een foto en wij zetten het om naar een prachtig lasersnijpatroon.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="nl">
      <body className="min-h-screen bg-gray-50 font-sans antialiased">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🔥</span>
              <span className="font-bold text-gray-900 text-lg">
                Vuurkorf<span className="text-orange-600">Persoonlijk</span>
              </span>
            </div>
            <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
              <a href="/" className="hover:text-orange-600 transition-colors">
                Home
              </a>
              <a
                href="/configurator"
                className="hover:text-orange-600 transition-colors"
              >
                Configurator
              </a>
              <a
                href="mailto:dennis@growdzen.com"
                className="hover:text-orange-600 transition-colors"
              >
                Contact
              </a>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="bg-gray-900 text-gray-400 text-sm py-8 mt-20">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <p>
              &copy; {new Date().getFullYear()} Growdzen &mdash; Vuurkorf
              Personalisatie. Alle rechten voorbehouden.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
