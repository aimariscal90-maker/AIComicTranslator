import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Sidebar from "./components/layout/Sidebar";
import TopNav from "./components/layout/TopNav";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
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
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-950 text-slate-50 overflow-hidden`}>
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
