import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "AlfaVision Bot",
    description: "Painel de Controle e Downloader",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="pt-BR">
            <body>{children}</body>
        </html>
    );
}
