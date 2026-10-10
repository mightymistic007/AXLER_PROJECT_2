import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { ResizeObserverGuard } from './components/ResizeObserverGuard';
import './globals.css';

const sans = Geist({ variable: '--font-sans', subsets: ['latin'] });
const mono = Geist_Mono({ variable: '--font-mono', subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'IceStream | Lakehouse Observability',
  description: 'A real-time control plane for governed, self-healing data pipelines.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className={`${sans.variable} ${mono.variable}`}><ResizeObserverGuard />{children}</body></html>;
}
