import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/shared/providers";
import { PageHeader } from "@/components/shared/page-header";
import { ModeToggle } from "@/components/shared/theme-toggle";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

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
      <body className={inter.className}>
        <Providers>
          <PageHeader>
            <ModeToggle />
          </PageHeader>
          <main className="container mx-auto p-4 pt-20 md:p-8 md:pt-24">
            {children}
          </main>
          <Toaster richColors />
        </Providers>
      </body>
    </html>
  );
}
