import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "./components/layout/Sidebar";
import TopNav from "./components/layout/TopNav";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "The Comic OS",
  description: "AI Powered Scanlation Operating System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased bg-slate-950 text-slate-50 overflow-hidden font-sans`}>
        <div className="flex h-screen w-full">
          {/* Sidebar */}
          <Sidebar />

          <div className="flex-1 flex flex-col ml-64">
            {/* Header */}
            <TopNav />

            {/* Main Content Area */}
            <main className="flex-1 mt-16 overflow-y-auto p-8 relative">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
