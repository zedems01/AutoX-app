import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/shared/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import { PageHeader } from "@/components/shared/page-header";
import { ModeToggle } from "@/components/shared/theme-toggle";
import { WorkflowProvider } from "@/contexts/WorkflowProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "X Automation",
  description: "Automate your X presence with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <WorkflowProvider>
            <div className="container mx-auto p-4">
              <PageHeader title="X Automation" description="Let's automate your X presence">
                <ModeToggle />
              </PageHeader>
              <main className="mt-6">{children}</main>
            </div>
            <Toaster />
          </WorkflowProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
