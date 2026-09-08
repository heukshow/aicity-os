import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SheetProof | 엑셀·CSV 오류 자동 검사",
  description: "XLSX, XLSM, CSV 파일의 누락값, 중복값, 형식 불일치, 계산 오류 가능성을 자동으로 검사하는 SheetProof by COSHUMA.",
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
          <div className="container mx-auto px-6 py-4 flex justify-between items-center gap-6">
            <a href="#" className="flex flex-col">
              <span className="text-2xl font-black gradient-text tracking-tighter leading-none">SheetProof</span>
              <span className="text-[10px] font-bold text-black/40 uppercase tracking-widest pl-1">by COSHUMA</span>
            </a>
            <nav>
              <ul className="flex space-x-5 md:space-x-8 text-xs md:text-sm font-medium">
                <li><a href="#analyze" className="hover:text-brand transition">무료 검사</a></li>
                <li><a href="#features" className="hover:text-brand transition">검사 항목</a></li>
                <li><a href="#limits" className="hover:text-brand transition">안내</a></li>
                <li><a href="#pricing" className="hover:text-brand transition">가격</a></li>
              </ul>
            </nav>
          </div>
        </header>
        <main className="pt-24 min-h-screen">{children}</main>
        <footer className="py-12 border-t border-white/5 bg-[#080808]">
          <div className="container mx-auto px-6 text-center text-gray-500 text-sm space-y-2">
            <p className="font-bold text-gray-300">SheetProof by COSHUMA</p>
            <p>엑셀·CSV 데이터 검수 자동화 서비스</p>
            <p className="text-xs">© 2026 COSHUMA. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
