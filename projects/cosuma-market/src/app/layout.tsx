import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "COSUMA Market | The Smartest AI Tools Selection",
  description: "Curated AI toolbox for modern businesses. Discover, compare, and implement the best AI tools from globally.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">
        <header className="fixed top-0 w-full z-50 glass">
          <div className="container mx-auto px-6 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-black gradient-text">COSUMA</h1>
            <nav>
              <ul className="flex space-x-8 text-sm font-medium">
                <li><a href="#" className="hover:text-brand transition">Home</a></li>
                <li><a href="#" className="hover:text-brand transition">Reviews</a></li>
                <li><a href="#" className="hover:text-brand transition">K-Specialized</a></li>
              </ul>
            </nav>
          </div>
        </header>
        <main className="pt-24 min-h-screen">
          {children}
        </main>
        <footer className="py-12 border-t border-white/5 bg-[#080808]">
          <div className="container mx-auto px-6 text-center text-gray-500 text-sm">
            <p>&copy; 2026 COSUMA Market. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
