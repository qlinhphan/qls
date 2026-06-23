import { useEffect, useMemo, useState } from 'react';
import { Send, Settings, Stethoscope } from 'lucide-react';

const API_URL = 'http://10.10.50.226:8001/chat';
const SYSTEM_PROMPT_API_URL = 'http://10.10.50.226:8001/system-prompt';
const THREAD_STORAGE_KEY = 'medical-chat-thread-id';
const welcomeMessage =
  'Xin chào, tôi là trợ lý AI của bạn, sẽ giúp đỡ bạn hôm nay.';

const modes = [
  {
    id: 'classification',
    label: 'Phân loại bệnh nhân',
    icon: Stethoscope,
  },
  // {
  //   id: 'record-check',
  //   label: 'Kiểm tra bệnh án',
  //   icon: ClipboardCheck,
  // },
];

function getAssistantText(data) {
  if (typeof data === 'string') return data;

  const answer =
    data?.answer ??
    data?.response ??
    data?.reply ??
    data?.message ??
    data?.content;

  if (typeof answer === 'string') return answer;

  if (answer && typeof answer === 'object') {
    return Object.entries(answer)
      .map(([key, value]) => `- ${key}: ${value}`)
      .join('\n');
  }

  return 'Đã nhận được phản hồi từ hệ thống.';
}

function createThreadId() {
  if (crypto.randomUUID) {
    return `record-${crypto.randomUUID()}`;
  }

  return `record-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getThreadId() {
  const savedThreadId = localStorage.getItem(THREAD_STORAGE_KEY);

  if (savedThreadId) return savedThreadId;

  const threadId = createThreadId();
  localStorage.setItem(THREAD_STORAGE_KEY, threadId);
  return threadId;
}

export default function App() {
  const [activeMode, setActiveMode] = useState(modes[0].id);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [threadId] = useState(getThreadId);
  const [typedWelcome, setTypedWelcome] = useState('');
  const [isPromptOpen, setIsPromptOpen] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [isPromptLoading, setIsPromptLoading] = useState(false);
  const [promptStatus, setPromptStatus] = useState('');

  const modeTitle = useMemo(
    () => modes.find((mode) => mode.id === activeMode)?.label ?? modes[0].label,
    [activeMode],
  );

  useEffect(() => {
    if (messages.length > 0) return undefined;

    setTypedWelcome('');
    let currentIndex = 0;
    const intervalId = window.setInterval(() => {
      currentIndex += 1;
      setTypedWelcome(welcomeMessage.slice(0, currentIndex));

      if (currentIndex >= welcomeMessage.length) {
        window.clearInterval(intervalId);
      }
    }, 34);

    return () => window.clearInterval(intervalId);
  }, [messages.length]);

  async function handleSubmit(event) {
    event.preventDefault();

    const value = input.trim();
    if (!value || isSending) return;

    setInput('');
    setIsSending(true);
    setMessages((current) => [...current, { role: 'user', text: value }]);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          message: value,
        }),
      });

      if (!response.ok) {
        throw new Error(`API trả về lỗi ${response.status}`);
      }

      const data = await response.json();
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: getAssistantText(data),
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: `Không thể gọi API: ${error.message}`,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  async function openPromptSettings() {
    setIsPromptOpen(true);
    setIsPromptLoading(true);
    setPromptStatus('');

    try {
      const response = await fetch(SYSTEM_PROMPT_API_URL);
      if (!response.ok) {
        throw new Error(`API trả về lỗi ${response.status}`);
      }

      const data = await response.json();
      setSystemPrompt(data.prompt ?? '');
    } catch (error) {
      setPromptStatus(`Không thể tải prompt: ${error.message}`);
    } finally {
      setIsPromptLoading(false);
    }
  }

  async function saveSystemPrompt() {
    const value = systemPrompt.trim();
    if (!value || isPromptLoading) return;

    setIsPromptLoading(true);
    setPromptStatus('');

    try {
      const response = await fetch(SYSTEM_PROMPT_API_URL, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: value,
        }),
      });

      if (!response.ok) {
        throw new Error(`API trả về lỗi ${response.status}`);
      }

      const data = await response.json();
      setSystemPrompt(data.prompt ?? value);
      setPromptStatus('Đã lưu prompt hệ thống.');
    } catch (error) {
      setPromptStatus(`Không thể lưu prompt: ${error.message}`);
    } finally {
      setIsPromptLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Stethoscope aria-hidden="true" size={42} strokeWidth={1.8} />
          </div>
          <div>
            <p className="brand-kicker">Bệnh Viện ĐKQT Bắc Hà</p>
            <h1>Medic AI</h1>
          </div>
        </div>

        <nav className="mode-panel" aria-label="Chọn chế độ">
          <p className="section-label">Chế độ</p>
          {modes.map((mode) => {
            const Icon = mode.icon;
            return (
              <button
                className={`mode-button ${activeMode === mode.id ? 'is-active' : ''}`}
                key={mode.id}
                onClick={() => setActiveMode(mode.id)}
                type="button"
              >
                <Icon aria-hidden="true" size={20} />
                <span>{mode.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <section className="chat-area">
        <header className="chat-header">
          <div className="chat-title">
            <div className="chat-title-row">
              <p className="section-label">Đang dùng</p>
              <button className="prompt-settings-button" onClick={openPromptSettings} type="button">
                <Settings aria-hidden="true" size={16} />
                <span>Thiết lập prompt</span>
              </button>
            </div>
            <h2>{modeTitle}</h2>
          </div>
        </header>

        <div className="conversation" aria-live="polite">
          {messages.length === 0 ? (
            <div className="welcome-panel">
              <p>{typedWelcome}</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
                <span>{message.role === 'user' ? 'Người dùng' : 'Trả lời'}</span>
                <p>{message.text}</p>
              </article>
            ))
          )}

          {isSending && (
            <article className="message assistant">
              <span>Trả lời</span>
              <p>Đang xử lý...</p>
            </article>
          )}
        </div>

        <footer className="chat-composer">
          <form className="message-form" onSubmit={handleSubmit}>
            <input
              aria-label="Nhập câu hỏi"
              disabled={isSending}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Nhập nội dung cần hỏi..."
              type="text"
              value={input}
            />
            <button aria-label="Gửi tin nhắn" disabled={isSending} type="submit">
              <Send aria-hidden="true" size={18} />
            </button>
          </form>
        </footer>
      </section>

      {isPromptOpen && (
        <div className="prompt-modal-backdrop">
          <section className="prompt-modal" aria-label="Thiết lập prompt hệ thống">
            <header className="prompt-modal-header">
              <div>
                <p className="section-label">Prompt hệ thống</p>
                <h2>Thiết lập prompt</h2>
              </div>
              <button
                className="prompt-modal-close"
                onClick={() => setIsPromptOpen(false)}
                type="button"
              >
                Đóng
              </button>
            </header>

            <textarea
              disabled={isPromptLoading}
              onChange={(event) => setSystemPrompt(event.target.value)}
              value={systemPrompt}
            />

            <footer className="prompt-modal-actions">
              <span>{promptStatus}</span>
              <button disabled={isPromptLoading || !systemPrompt.trim()} onClick={saveSystemPrompt} type="button">
                {isPromptLoading ? 'Đang xử lý...' : 'Lưu prompt'}
              </button>
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}
