import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/shared/providers";
import { PageHeader } from "@/components/shared/page-header";
import { ModeToggle } from "@/components/shared/theme-toggle";
import { Toaster } from "@/components/ui/sonner";
import { Analytics } from "@vercel/analytics/next";
import React from "react";


export const metadata: Metadata = {
  title: "AutoX Content Creator",
  description: "Automate your X content workflow",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`font-mono bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950`}
      >
        <Providers>
          <PageHeader>
            <ModeToggle />
          </PageHeader>
          <main className="container mx-auto p-4 pt-20 md:p-8 md:pt-24">
            {children}
          </main>
          <Toaster richColors />
        </Providers>
        <Analytics />
      </body>
    </html>
  );
}
