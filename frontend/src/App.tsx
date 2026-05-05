import { useState, useEffect } from 'react';
import { ActiveCallFeed } from './components/ActiveCallFeed';
import { TranscriptView } from './components/TranscriptView';
import { LeadBadge } from './components/LeadBadge';
import { WatiAction } from './components/WatiAction';
import { PostCallSummary } from './components/PostCallSummary';
import { PhoneOff } from 'lucide-react';

function App() {
  const [calls, setCalls] = useState<any[]>([]);
  const [activeCallId, setActiveCallId] = useState<string | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [isCallEnded, setIsCallEnded] = useState(false);
  const [postCallData, setPostCallData] = useState<any>(null);

  const activeCall = calls.find(c => c.id === activeCallId);

  // Poll for calls
  useEffect(() => {
    const fetchCalls = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/calls');
        const data = await res.json();
        setCalls(data);
        if (data.length > 0 && !activeCallId) {
          setActiveCallId(data[0].id);
        }
      } catch (e) { console.error(e); }
    };
    fetchCalls();
    const interval = setInterval(fetchCalls, 3000);
    return () => clearInterval(interval);
  }, [activeCallId]);

  // Poll for messages
  useEffect(() => {
    if (!activeCallId) return;
    setIsCallEnded(false);
    setPostCallData(null);
    
    const fetchMessages = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/calls/${activeCallId}/messages`);
        const data = await res.json();
        setMessages(data);
      } catch (e) { console.error(e); }
    };
    fetchMessages();
    const interval = setInterval(fetchMessages, 2000);
    return () => clearInterval(interval);
  }, [activeCallId]);

  const handleEndCall = async () => {
    if (!activeCall) return;
    setIsCallEnded(true);
    
    const fullTranscript = messages.map(m => `${m.sender === 'ai' ? 'Agent' : 'Customer'}: ${m.text}`).join('\n');
    
    try {
      const res = await fetch('http://localhost:8000/api/post-call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          call_id: activeCall.id
        })
      });
      const data = await res.json();
      setPostCallData(data);
    } catch (e) {
      console.error(e);
      setPostCallData({
        summary: "Error communicating with backend API.",
        next_steps: ["Ensure FastAPI server is running on port 8000"],
        whatsapp_message: "Error...",
        whatsapp_sent: false
      });
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-6 flex flex-col max-w-7xl mx-auto gap-6">
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-4 md:p-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            VaaniAI RM Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">Live Call Intelligence & Interventions</p>
        </div>
        
        {activeCall && (
          <div className="flex flex-wrap items-center gap-4 mt-2 md:mt-0">
            <LeadBadge score={activeCall.score} />
            <WatiAction phoneNumber={activeCall.phone} />
            {!isCallEnded && (
              <button 
                onClick={handleEndCall}
                className="flex items-center gap-2 bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg transition-colors"
              >
                <PhoneOff size={18} /> End Call
              </button>
            )}
          </div>
        )}
      </header>

      <main className="flex flex-col md:flex-row gap-6 flex-1 min-h-0">
        <ActiveCallFeed 
          calls={calls} 
          activeId={activeCallId || ''} 
          onSelect={setActiveCallId} 
        />
        {isCallEnded ? (
          <PostCallSummary data={postCallData} />
        ) : (
          <TranscriptView messages={messages} />
        )}
      </main>
    </div>
  );
}

export default App;
