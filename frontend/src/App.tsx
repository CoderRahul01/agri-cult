import React, { useState, useEffect, useRef } from "react";
import {
  Send,
  Leaf,
  Layout,
  Book,
  Settings,
  MessageCircle,
  TrendingUp,
  ExternalLink,
  Database,
  Cloud,
  Sun,
  Thermometer,
  ArrowUpRight,
  ArrowDownRight,
  Phone,
  Briefcase,
  Globe,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import "./index.css";

interface Message {
  role: "farmer" | "advisor";
  content: string;
  sources?: { document: string; page?: string | number }[];
  searchTriggered?: boolean;
}

interface WeatherData {
  temperature: number;
  condition: string;
  location: string;
}

interface MarketItem {
  crop: string;
  price: number;
  change: number;
  mandi: string;
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<
    "dashboard" | "consult" | "market" | "library"
  >("dashboard");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "advisor",
      content:
        "Explore the future of farming. Ask me about citrus diseases, government subsidies, or latest market trends. I am powered by your private agricultural database.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [market, setMarket] = useState<MarketItem[]>([]);
  const [language, setLanguage] = useState<"EN" | "HI">("EN");

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const wRes = await fetch(
        "http://localhost:8000/api/v1/dashboard/weather",
      );
      const wData = await wRes.json();
      setWeather(wData);

      const mRes = await fetch("http://localhost:8000/api/v1/dashboard/market");
      const mData = await mRes.json();
      setMarket(mData);
    } catch (e) {
      console.error("Failed to load dashboard data");
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: "farmer", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input, session_id: "default" }),
      });

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "advisor",
          content: data.answer,
          sources: data.sources,
          searchTriggered: data.search_triggered,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "advisor",
          content: "Connection lost. I am currently offline.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const Dashboard = () => (
    <div className="dashboard-view">
      <div className="welcome-header">
        <h1>{language === "EN" ? "Welcome, Krishak" : "नमस्ते, कृषक"}</h1>
        <p>
          {language === "EN"
            ? "Here is your farm's overview for today."
            : "आज के लिए आपके खेत का विवरण।"}
        </p>
      </div>

      <div className="grid-layout">
        <div className="card weather-card">
          <div className="weather-main">
            <div>
              <Cloud size={48} />
              <p>{weather?.condition || "Loading..."}</p>
            </div>
            <div className="temp">{weather?.temperature || "--"}°C</div>
          </div>
          <p>{weather?.location || "Detecting location..."}</p>
        </div>

        <div className="card market-card">
          <h3>{language === "EN" ? "Mandi Prices" : "मंडी भाव"}</h3>
          {market.slice(0, 3).map((item, id) => (
            <div key={id} className="market-item">
              <span>{item.crop}</span>
              <div style={{ textAlign: "right" }}>
                <div>₹{item.price}</div>
                <div className={item.change >= 0 ? "price-up" : "price-down"}>
                  {item.change >= 0 ? (
                    <ArrowUpRight size={14} />
                  ) : (
                    <ArrowDownRight size={14} />
                  )}
                  {Math.abs(item.change)}%
                </div>
              </div>
            </div>
          ))}
          <button
            onClick={() => setActiveTab("market")}
            style={{
              width: "100%",
              marginTop: 12,
              border: "none",
              background: "none",
              color: "#1a4d2e",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            View All Prices
          </button>
        </div>

        <div className="action-grid">
          <button
            className="action-btn"
            onClick={() => setActiveTab("consult")}
          >
            <MessageCircle color="#1a4d2e" size={32} />
            <span>AI Advisor</span>
          </button>
          <button className="action-btn">
            <Leaf color="#1a4d2e" size={32} />
            <span>Disease ID</span>
          </button>
          <button className="action-btn">
            <Briefcase color="#1a4d2e" size={32} />
            <span>Schemes</span>
          </button>
          <button className="action-btn">
            <Phone color="#1a4d2e" size={32} />
            <span>Call Expert</span>
          </button>
        </div>
      </div>
    </div>
  );

  const Consultation = () => (
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
                      {s.document}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="msg-row advisor">
            <div className="msg-card loading-dots">Thinking...</div>
          </div>
        )}
      </div>

      <div className="input-dock">
        <div className="glass-pill">
          <input
            type="text"
            placeholder={
              language === "EN"
                ? "Ask about citrus diseases, schemes..."
                : "नींबू के रोगों, योजनाओं के बारे में पूछें..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
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
  );

  return (
    <div className="app-wrapper">
      <aside className="sidebar">
        <div className="brand">
          <Leaf size={28} color="#1a4d2e" fill="#1a4d2e" />
          <h2>Agri-Cult</h2>
        </div>

        <nav className="nav-links">
          <div
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <Layout size={20} />
            <span>{language === "EN" ? "Dashboard" : "डैशबोर्ड"}</span>
          </div>
          <div
            className={`nav-item ${activeTab === "consult" ? "active" : ""}`}
            onClick={() => setActiveTab("consult")}
          >
            <MessageCircle size={20} />
            <span>{language === "EN" ? "AI Consult" : "सलाह"}</span>
          </div>
          <div
            className={`nav-item ${activeTab === "market" ? "active" : ""}`}
            onClick={() => setActiveTab("market")}
          >
            <TrendingUp size={20} />
            <span>{language === "EN" ? "Market" : "मंडी"}</span>
          </div>
          <div
            className={`nav-item ${activeTab === "library" ? "active" : ""}`}
            onClick={() => setActiveTab("library")}
          >
            <Book size={20} />
            <span>{language === "EN" ? "Knowledge" : "ज्ञान"}</span>
          </div>
        </nav>

        <div
          style={{ marginTop: "auto" }}
          className="nav-item"
          onClick={() => setLanguage(language === "EN" ? "HI" : "EN")}
        >
          <Globe size={20} />
          <span>
            {language === "EN" ? "Hindi / हिंदी" : "English / अंग्रेजी"}
          </span>
        </div>
      </aside>

      <main className="main-stage">
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "consult" && <Consultation />}
        {activeTab !== "dashboard" && activeTab !== "consult" && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#666",
            }}
          >
            Soon to be integrated Knowledge Base
          </div>
        )}
      </main>

      <a
        href="https://wa.me/91XXXXXXXXXX"
        className="expert-float"
        target="_blank"
        rel="noopener noreferrer"
      >
        <MessageCircle size={20} />
        <span>{language === "EN" ? "Expert Help" : "विशेषज्ञ सहायता"}</span>
      </a>
    </div>
  );
};

export default App;
