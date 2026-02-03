"use client";

import { useState, FormEvent } from "react";
import { Download, Bot, Settings, Users, LogOut, Play, Square, Save, Radio, BarChart3, Megaphone, Heart } from "lucide-react";

export default function Home() {
    const [activeTab, setActiveTab] = useState("download");
    const [url, setUrl] = useState("");
    const [downloadStatus, setDownloadStatus] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [botToken, setBotToken] = useState("");

    // Fake Data for UI Layout
    const [users] = useState([
        { id: 1, name: "Maria", user: "@mary", last: "Hoje 10:00" },
        { id: 2, name: "Joao", user: "@john", last: "Ontem 14:00" },
    ]);

    const handleDownload = async (e: FormEvent) => {
        e.preventDefault();
        if (!url) return;
        setLoading(true);
        setDownloadStatus("Processando...");
        try {
            const res = await fetch("/api/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });
            const data = await res.json();
            if (res.ok && data.download_url) {
                setDownloadStatus("✅ Sucesso! Clique abaixo para baixar.");
                window.open(data.download_url, '_blank');
            } else {
                setDownloadStatus("❌ Erro: " + (data.error || "Desconhecido"));
            }
        } catch { setDownloadStatus("❌ Erro de conexão."); }
        setLoading(false);
    };

    const handleSetWebhook = async () => {
        if (!botToken) return alert("Insira o token!");
        setLoading(true);
        try {
            const res = await fetch("/api/bot/setup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: botToken }),
            });
            const data = await res.json();

            if (res.ok) {
                alert("✅ " + data.detail);
            } else {
                alert("❌ Erro: " + (data.error || "Falha desconhecida"));
            }
        } catch (e) {
            alert("Erro de conexão ao tentar configurar o bot.");
        }
        setLoading(false);
    };

    return (
        <main className="min-h-screen bg-[#F0F2F5] flex flex-col items-center py-10 px-4 font-sans">
            <header className="w-full max-w-6xl bg-gradient-to-r from-primary to-primary_dark text-white rounded-2xl shadow-xl p-6 mb-8 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="bg-white/20 p-3 rounded-full backdrop-blur-sm">
                        <Download className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">AlfaVision Web</h1>
                        <p className="text-white/90 text-sm">Painel de Controle Completo</p>
                    </div>
                </div>
                <div className="text-right hidden sm:block">
                    <p className="font-semibold flex items-center gap-2 justify-end"><span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span> Online</p>
                </div>
            </header>

            <div className="w-full max-w-6xl flex flex-col lg:flex-row gap-8">
                {/* Sidebar Navigation */}
                <nav className="w-full lg:w-72 bg-white rounded-2xl shadow-lg p-5 h-fit sticky top-6">
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 px-2">Menu Principal</p>
                    <ul className="space-y-2">
                        {[
                            { id: "download", icon: Download, label: "Baixar Vídeos" },
                            { id: "bot", icon: Bot, label: "Telegram Bot" },
                            { id: "broadcast", icon: Megaphone, label: "Broadcast" },
                            { id: "users", icon: Users, label: "Usuários" },
                            { id: "donors", icon: Heart, label: "Doadores" },
                            { id: "cookies", icon: Settings, label: "Configurar Cookies" },
                        ].map((item) => (
                            <li key={item.id}>
                                <button
                                    onClick={() => setActiveTab(item.id)}
                                    className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium transition-all duration-200 ${activeTab === item.id
                                        ? "bg-primary text-white shadow-md transform scale-[1.02]"
                                        : "text-gray-600 hover:bg-gray-50 hover:pl-5"
                                        }`}
                                >
                                    <item.icon className="w-5 h-5" />
                                    {item.label}
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>

                {/* Content Area */}
                <div className="flex-1 bg-white rounded-2xl shadow-lg p-8 min-h-[600px] border border-gray-100">

                    {activeTab === "download" && (
                        <div className="animate-fade-in-up">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2"><Download className="text-primary" /> Baixar Vídeos</h2>
                            <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
                                <input
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="Cole o link aqui (Shopee, TikTok, Instagram, Youtube...)"
                                    className="w-full px-5 py-4 rounded-xl border border-gray-200 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all text-lg mb-4 shadow-sm"
                                />
                                <button
                                    onClick={handleDownload}
                                    disabled={loading}
                                    className="w-full py-4 rounded-xl font-bold text-white bg-gradient-to-r from-primary to-primary_dark hover:shadow-lg transform active:scale-[0.99] transition-all flex justify-center items-center gap-2"
                                >
                                    {loading ? <span className="animate-spin">⌛</span> : <Download />}
                                    BAIXAR AGORA
                                </button>
                                {downloadStatus && (
                                    <div className="mt-4 p-4 rounded-lg bg-blue-50 text-blue-800 font-medium border border-blue-100 animate-pulse">
                                        {downloadStatus}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === "bot" && (
                        <div className="animate-fade-in-up">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2"><Bot className="text-telegram" /> Configuração do Bot</h2>
                            <div className="space-y-6">
                                <div className="bg-blue-50 p-5 rounded-xl border-l-4 border-telegram">
                                    <h3 className="font-bold text-telegram mb-2">🚀 Como ativar no Vercel (Webhooks)</h3>
                                    <p className="text-sm text-blue-800 mb-4">Diferente do PC, o bot na web precisa de um Webhook para funcionar.</p>
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            placeholder="Cole o Token do BotFather aqui..."
                                            className="flex-1 px-4 py-2 rounded-lg border border-blue-200 focus:outline-none"
                                            value={botToken}
                                            onChange={(e) => setBotToken(e.target.value)}
                                        />
                                        <button
                                            onClick={handleSetWebhook}
                                            className="bg-telegram text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-600 transition-colors"
                                        >
                                            ATIVAR BOT
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === "broadcast" && (
                        <div className="animate-fade-in-up">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2"><Megaphone className="text-orange-500" /> Enviar Mensagem (Broadcast)</h2>
                            <div className="bg-orange-50 p-6 rounded-xl border border-orange-100">
                                <p className="text-orange-800 mb-4 text-sm font-medium">⚠️ Envie mensagens para todos os usuários do bot.</p>
                                <textarea
                                    className="w-full h-32 px-4 py-3 rounded-xl border border-orange-200 focus:ring-2 focus:ring-orange-400 outline-none resize-none mb-4"
                                    placeholder="Digite sua mensagem aqui..."
                                ></textarea>
                                <button className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-xl font-bold shadow transition-colors flex items-center gap-2">
                                    <Megaphone className="w-5 h-5" /> ENVIAR PARA TODOS
                                </button>
                            </div>
                        </div>
                    )}

                    {activeTab === "users" && (
                        <div className="animate-fade-in-up">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2"><Users className="text-purple-600" /> Usuários do Bot</h2>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b-2 border-gray-100 text-gray-500 text-sm uppercase">
                                            <th className="py-3">Nome</th>
                                            <th className="py-3">Usuário</th>
                                            <th className="py-3">Último Acesso</th>
                                            <th className="py-3">Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-gray-700">
                                        {users.map(u => (
                                            <tr key={u.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                                <td className="py-3 font-medium">{u.name}</td>
                                                <td className="py-3 text-blue-500">{u.user}</td>
                                                <td className="py-3">{u.last}</td>
                                                <td className="py-3"><button className="text-red-500 text-sm hover:underline">Bloquear</button></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {activeTab === "donors" && (
                        <div className="animate-fade-in-up">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2"><Heart className="text-pink-500" /> Histórico de Doações</h2>
                            <div className="bg-pink-50 p-8 rounded-xl text-center border border-pink-100">
                                <Heart className="w-16 h-16 text-pink-300 mx-auto mb-4" />
                                <p className="text-pink-800 font-medium">Nenhuma doação registrada ainda.</p>
                            </div>
                        </div>
                    )}

                    {activeTab === "cookies" && (
                        <div className="animate-fade-in-up">
                            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2"><Settings className="text-gray-600" /> Configuração de Cookies</h2>
                            <div className="bg-gray-50 border-l-4 border-gray-400 p-4 text-gray-700 text-sm mb-6">
                                <p>Cole aqui os cookies para permitir downloads de TikTok, Instagram, etc.</p>
                            </div>
                            <textarea
                                className="w-full h-48 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none font-mono text-xs"
                                placeholder="# Netscape HTTP Cookie File..."
                            ></textarea>
                            <button className="mt-4 bg-gray-800 hover:bg-black text-white px-8 py-3 rounded-xl font-bold shadow transition-colors">
                                SALVAR COOKIES
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </main>
    );
}
