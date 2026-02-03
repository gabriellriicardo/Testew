"use client";

import { useState, FormEvent } from "react";
import { Download, Bot, Settings, Users, LogOut, Play, Square, Save, ExternalLink } from "lucide-react";

export default function Home() {
    const [activeTab, setActiveTab] = useState("download");
    const [url, setUrl] = useState("");
    const [downloadStatus, setDownloadStatus] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    // Bot Config States
    const [botToken, setBotToken] = useState("");
    const [maintenance, setMaintenance] = useState(false);
    const [botStatus, setBotStatus] = useState("Parado");

    const handleDownload = async (e: FormEvent) => {
        e.preventDefault();
        if (!url) return;

        setLoading(true);
        setDownloadStatus("Iniciando download...");

        try {
            const res = await fetch("/api/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });

            const data = await res.json();

            if (res.ok) {
                setDownloadStatus(`Sucesso! Vídeo pronto: ${data.title}`);
                // In a real app, trigger prompt or show video player
            } else {
                setDownloadStatus("Erro: " + data.error);
            }
        } catch (err) {
            setDownloadStatus("Erro de conexão ao servidor.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-[#F0F2F5] flex flex-col items-center py-10 px-4">
            {/* Header */}
            <header className="w-full max-w-5xl bg-primary text-white rounded-2xl shadow-lg p-6 mb-8 flex justify-between items-center transition-transform hover:scale-[1.01] duration-300">
                <div className="flex items-center gap-4">
                    <div className="bg-white/20 p-3 rounded-full">
                        <Download className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">AlfaVision Web</h1>
                        <p className="text-white/80 text-sm">Painel de Controle & Downloader</p>
                    </div>
                </div>
                <div className="text-right hidden sm:block">
                    <p className="font-semibold">Status: <span className="text-green-300">Online</span></p>
                    <p className="text-xs text-white/70">Vercel Edition</p>
                </div>
            </header>

            {/* Main Content */}
            <div className="w-full max-w-5xl flex flex-col md:flex-row gap-6">

                {/* Sidebar */}
                <nav className="w-full md:w-64 bg-white rounded-xl shadow-sm p-4 h-fit sticky top-6">
                    <ul className="space-y-2">
                        <li>
                            <button
                                onClick={() => setActiveTab("download")}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${activeTab === "download"
                                        ? "bg-primary/10 text-primary border-l-4 border-primary"
                                        : "text-gray-600 hover:bg-gray-50"
                                    }`}
                            >
                                <Download className="w-5 h-5" />
                                Baixar Vídeos
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => setActiveTab("bot")}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${activeTab === "bot"
                                        ? "bg-telegram/10 text-telegram border-l-4 border-telegram"
                                        : "text-gray-600 hover:bg-gray-50"
                                    }`}
                            >
                                <Bot className="w-5 h-5" />
                                Gerenciar Bot
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => setActiveTab("cookies")}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${activeTab === "cookies"
                                        ? "bg-purple-100 text-purple-600 border-l-4 border-purple-600"
                                        : "text-gray-600 hover:bg-gray-50"
                                    }`}
                            >
                                <Settings className="w-5 h-5" />
                                Cookies & Acesso
                            </button>
                        </li>
                        <li className="pt-4 mt-4 border-t border-gray-100">
                            <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium text-red-500 hover:bg-red-50 transition-colors">
                                <LogOut className="w-5 h-5" />
                                Sair
                            </button>
                        </li>
                    </ul>
                </nav>

                {/* Content Area */}
                <div className="flex-1 bg-white rounded-xl shadow-sm p-8 min-h-[500px]">

                    {/* TAB: DOWNLOAD */}
                    {activeTab === "download" && (
                        <div className="space-y-6 animate-fadeIn">
                            <div className="border-b pb-4">
                                <h2 className="text-2xl font-bold text-gray-800">Baixar Vídeo Manualmente</h2>
                                <p className="text-gray-500">Suporta Shopee, TikTok, Kwai, Instagram, Facebook, YouTube.</p>
                            </div>

                            <form onSubmit={handleDownload} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Cole o Link do Vídeo</label>
                                    <input
                                        type="text"
                                        placeholder="https://..."
                                        className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                        value={url}
                                        onChange={(e) => setUrl(e.target.value)}
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className={`w-full py-3 rounded-lg font-bold text-white shadow-md transition-all ${loading ? "bg-gray-400 cursor-not-allowed" : "bg-primary hover:bg-primary_dark active:scale-[0.98]"
                                        }`}
                                >
                                    {loading ? "Processando..." : "🚀 Baixar Agora"}
                                </button>
                            </form>

                            {downloadStatus && (
                                <div className={`p-4 rounded-lg mt-4 ${downloadStatus.includes("Sucesso") ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
                                    <p className="font-medium">{downloadStatus}</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* TAB: BOT */}
                    {activeTab === "bot" && (
                        <div className="space-y-6 animate-fadeIn">
                            <div className="border-b pb-4 flex justify-between items-center">
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-800">Configuração do Bot Telegram</h2>
                                    <p className="text-gray-500">Controle o status e comportamento do bot.</p>
                                </div>
                                <div className={`px-4 py-1 rounded-full text-sm font-bold ${botStatus === "Rodando" ? "bg-green-100 text-green-600" : "bg-gray-200 text-gray-600"}`}>
                                    {botStatus}
                                </div>
                            </div>

                            <div className="grid grid-cols-1 gap-6">
                                <div className="bg-gray-50 p-5 rounded-lg border border-gray-200">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">Token do Bot (BotFather)</label>
                                    <div className="flex gap-2">
                                        <input
                                            type="password"
                                            placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                                            className="flex-1 px-4 py-2 rounded border border-gray-300 focus:outline-none focus:border-telegram"
                                            value={botToken}
                                            onChange={(e) => setBotToken(e.target.value)}
                                        />
                                        <button className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded font-medium transition-colors">
                                            <Save className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>

                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setBotStatus("Rodando")}
                                        className="flex-1 bg-telegram hover:bg-[#0077b5] text-white py-4 rounded-xl shadow-lg flex flex-col items-center justify-center gap-2 transition-transform hover:-translate-y-1"
                                    >
                                        <Play className="w-8 h-8" />
                                        <span className="font-bold">INICIAR BOT</span>
                                    </button>
                                    <button
                                        onClick={() => setBotStatus("Parado")}
                                        className="flex-1 bg-red-500 hover:bg-red-600 text-white py-4 rounded-xl shadow-lg flex flex-col items-center justify-center gap-2 transition-transform hover:-translate-y-1"
                                    >
                                        <Square className="w-8 h-8" />
                                        <span className="font-bold">PARAR BOT</span>
                                    </button>
                                </div>

                                <div className="flex items-center gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800">
                                    <input
                                        type="checkbox"
                                        id="maintenance"
                                        checked={maintenance}
                                        onChange={(e) => setMaintenance(e.target.checked)}
                                        className="w-5 h-5 text-primary rounded focus:ring-primary"
                                    />
                                    <label htmlFor="maintenance" className="font-medium cursor-pointer select-none">
                                        Ativar Modo Manutenção (Responde usuários que está em reforma)
                                    </label>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* TAB: COOKIES */}
                    {activeTab === "cookies" && (
                        <div className="space-y-6 animate-fadeIn">
                            <div className="border-b pb-4">
                                <h2 className="text-2xl font-bold text-gray-800">Gerenciamento de Cookies</h2>
                                <p className="text-gray-500">Adicione cookies manualmente para sites que exigem login (Instagram, TikTok, Shopee).</p>
                            </div>

                            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 text-blue-700 text-sm">
                                <p><strong>Nota:</strong> Em ambiente Serverless (Vercel), não podemos usar navegadores automatizados. Você deve pegar os cookies do seu navegador (usando extensões como "Get cookies.txt") e colar aqui.</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Conteúdo do Cookie (Netscape Format)</label>
                                <textarea
                                    className="w-full h-48 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none font-mono text-xs"
                                    placeholder="# Netscape HTTP Cookie File..."
                                ></textarea>
                                <button className="mt-3 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium shadow transition-colors w-full sm:w-auto">
                                    Salvar Cookies
                                </button>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </main>
    );
}
