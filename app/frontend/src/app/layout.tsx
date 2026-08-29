import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-mono-jb',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'ThermalEye — Autonomous Multi-Satellite Industrial Thermal Surveillance',
  description:
    'NTRO SIH 2026 (SIH26162YELLOW) · 7-Class Thermal Classifier & Automated Section 31A Regulatory Enforcement System.',
  keywords: ['thermal intelligence', 'VIIRS 375m', 'gas flaring', 'brick kilns', 'wildfire', 'NTRO', 'SIH 2026'],
  authors: [{ name: 'ThermalEye Team' }],
  openGraph: {
    title: 'ThermalEye — Autonomous Multi-Satellite Thermal Surveillance',
    description: 'Autonomous Earth Observation & Thermal Anomaly Attribution Engine',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      data-theme="dark"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-[#0b0c0e] text-[#e7e9ec] antialiased overflow-hidden font-sans">
        {children}
      </body>
    </html>
  );
}
