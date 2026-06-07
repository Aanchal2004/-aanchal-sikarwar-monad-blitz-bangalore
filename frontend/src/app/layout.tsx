import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Monad Agent Hackathon Kit",
  description: "Ship AI agents + blockchain MVPs in one day",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
