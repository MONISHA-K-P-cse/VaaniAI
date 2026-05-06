import { useState, useEffect } from 'react';
import { ActiveCallFeed } from '../components/ActiveCallFeed';
import { TranscriptView } from '../components/TranscriptView';
import { LeadBadge } from '../components/LeadBadge';
import { WatiAction } from '../components/WatiAction';
import { PostCallSummary } from '../components/PostCallSummary';
import { PhoneOff, Activity } from 'lucide-react';

export function Dashboard() {
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
      } catch (e) { console.error("Poll calls error:", e); }
    };
    fetchCalls();
    const interval = setInterval(fetchCalls, 2000);
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
      } catch (e) { console.error("Poll messages error:", e); }
    };
    fetchMessages();
    const interval = setInterval(fetchMessages, 1500);
    return () => clearInterval(interval);
  }, [activeCallId]);

  const handleEndCall = async () => {
    if (!activeCall) return;
    setIsCallEnded(true);
    
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
      console.error("Post-call error:", e);
      setPostCallData({
        summary: "Error communicating with backend API.",
        next_steps: ["Ensure FastAPI server is running on port 8000"],
        whatsapp_message: "Error...",
        whatsapp_sent: false
      });
    }
  };

  return (
    <div className="p-6 flex flex-col gap-6 max-w-7xl mx-auto h-full">
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Activity className="text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Live Intelligence
            </h1>
            <p className="text-slate-400 text-sm mt-1 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
              Real-time Call Monitoring & Analysis
            </p>
          </div>
        </div>
        
        {activeCall && (
          <div className="flex flex-wrap items-center gap-4 mt-2 md:mt-0">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${activeCall.isActive ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-700 text-slate-400'}`}>
              {activeCall.isActive ? 'Live' : 'Disconnected'}
            </div>
            <LeadBadge score={activeCall.score} />
            <WatiAction phoneNumber={activeCall.phone} />
            {!isCallEnded && (
              <button 
                onClick={handleEndCall}
                className="flex items-center gap-2 bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-xl font-semibold shadow-lg shadow-rose-600/20 transition-all hover:scale-105 active:scale-95"
              >
                <PhoneOff size={18} /> End Call
              </button>
            )}
          </div>
        )}
      </header>

      <div className="flex flex-col md:flex-row gap-6 flex-1 min-h-0">
        <div className="md:w-1/3 flex flex-col gap-4">
          <ActiveCallFeed 
            calls={calls} 
            activeId={activeCallId || ''} 
            onSelect={setActiveCallId} 
          />
        </div>
        <div className="flex-1 flex flex-col gap-4 min-h-0 relative">
          {isCallEnded ? (
            <PostCallSummary data={postCallData} />
          ) : (
            <TranscriptView messages={messages} />
          )}
        </div>
      </div>
    </div>
  );
}
