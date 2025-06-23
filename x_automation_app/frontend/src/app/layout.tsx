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
          <div className="container mx-auto p-4 md:p-8">
            <PageHeader
              title="AutoX Content Creator"
              description="Let's automate your X presence"
            >
              <ModeToggle />
            </PageHeader>
            <main className="mt-6">{children}</main>
            <Toaster richColors />
          </div>
        </Providers>
      </body>
    </html>
  );
}
