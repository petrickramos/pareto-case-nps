import "./globals.css";
import { Manrope, Sora } from "next/font/google";

const titleFont = Sora({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-title"
});

const bodyFont = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body"
});

export const metadata = {
  title: "Pareto NPS Monitor",
  description: "Dashboard de monitoramento e intervenção do bot NPS"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={`${titleFont.variable} ${bodyFont.variable}`}>
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
