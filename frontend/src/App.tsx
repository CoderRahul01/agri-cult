import React, { useState, useEffect, useRef } from 'react';
import {
    Send,
    Leaf,
    Layout,
    Book,
    Settings,
    HelpCircle,
    MessageCircle,
    TrendingUp,
    ExternalLink,
    ChevronRight,
    PlusCircle,
    Cpu,
    Database
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';

interface Message {
    role: 'farmer' | 'advisor';
    content: string;
    sources?: { document: string; page?: string | number }[];
    searchTriggered?: boolean;
}

const App: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'advisor', content: 'Explore the future of farming. Ask me about citrus diseases, government subsidies, or latest market trends. I am powered by your private agricultural database.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: Message = { role: 'farmer', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: input, session_id: 'default' })
            });

            const data = await response.json();
            setMessages(prev => [...prev, {
                role: 'advisor',
                content: data.answer,
                sources: data.sources,
                searchTriggered: data.search_triggered
            }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'advisor', content: 'Connection lost. I am currently offline.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app-wrapper">
            <aside className="sidebar">
                <div className="brand">
                    <Leaf size={28} color="#1a4d2e" fill="#1a4d2e" />
                    <h2>Agri-Cult</h2>
                </div>

                <nav className="nav-links">
                    <div className="nav-item active">
                        <Layout size={20} />
                        <span>Consult</span>
                    </div>
                    <div className="nav-item">
                        <TrendingUp size={20} />
                        <span>Market</span>
                    </div>
                    <div className="nav-item">
                        <Book size={20} />
                        <span>Library</span>
                    </div>
                    <div className="nav-item">
                        <Settings size={20} />
                        <span>Settings</span>
                    </div>
                </nav>
            </aside>

            <main className="main-stage">
                <div className="chat-container">
                    <div className="messages-grid" ref={scrollRef}>
                        {messages.map((m, i) => (
                            <div key={i} className={`msg-row ${m.role}`}>
                                <div className="msg-card">
                                    <ReactMarkdown>{m.content}</ReactMarkdown>
                                    {m.sources && m.sources.length > 0 && (
                                        <div className="citation-row">
                                            {m.sources.map((s, si) => (
                                                <span key={si} className="cite-tag">
                                                    <Database size={10} />
                                                    {s.document} {m.searchTriggered && <ExternalLink size={10} />}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="msg-row ai">
                                <div className="msg-card">
                                    <div className="loading-dots">Thinking...</div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="input-dock">
                        <div className="glass-pill">
                            <input
                                type="text"
                                placeholder="How can I optimize my citrus farm today?"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            />
                            <button
                                className="send-action"
                                onClick={handleSend}
                                disabled={isLoading || !input.trim()}
                            >
                                <Send size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            <a
                href="https://wa.me/91XXXXXXXXXX"
                className="expert-float"
                target="_blank"
                rel="noopener noreferrer"
            >
                <div className="wa-icon-box">
                    <MessageCircle size={20} />
                </div>
                <span>Expert Consult</span>
            </a>
        </div>
    );
};

export default App;
