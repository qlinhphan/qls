import { useEffect, useMemo, useState } from 'react';
import {
  Archive,
  BarChart3,
  Bell,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  Folder,
  KeyRound,
  LogOut,
  Send,
  Settings,
  Stethoscope,
  User,
  Users,
  Upload,
} from 'lucide-react';

const API_URL = 'http://10.10.50.226:8001/chat';
const SYSTEM_PROMPT_API_URL = 'http://10.10.50.226:8001/system-prompt';
const MEDICAL_RECORD_CHECK_API_URL = 'http://10.10.50.226:8001/medical-record/check-json';
const THREAD_STORAGE_KEY = 'medical-chat-thread-id';
const welcomeMessage =
  'Xin chào, tôi là trợ lý AI của bạn, sẽ giúp đỡ bạn hôm nay.';

const modes = [
  {
    id: 'classification',
    label: 'Phân loại bệnh nhân',
    icon: Stethoscope,
  },
  {
    id: 'record-check',
    label: 'Kiểm tra bệnh án',
    icon: ClipboardCheck,
  },
];

const recordReviewSections = [
  {
    key: 'TomTatHoSoBenhAn',
    label: 'Tóm tắt hồ sơ bệnh án',
  },
  {
    key: 'GiayRaVien',
    label: 'Giấy ra viện',
  },
  {
    key: 'ThongTinTongKetBenhAn',
    label: 'Thông tin tổng kết bệnh án',
  },
  {
    key: 'ThongTinRaVien',
    label: 'Thông tin ra viện',
  },
  {
    key: 'ThongTinBenhAn',
    label: 'Thông tin bệnh án',
  },
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

function hasReviewError(text) {
  const value = String(text ?? '').toUpperCase();
  return value.includes('❌') || value.includes('NÊN XEM LẠI') || value.includes('NEN XEM LAI');
}

function getReviewStatus(text) {
  const value = String(text ?? '').toUpperCase();
  if (value.includes('NÊN XEM LẠI') || value.includes('NEN XEM LAI') || value.includes('❌')) {
    return {
      className: 'is-warning',
      label: 'Nên Xem Lại',
    };
  }
  if (value.includes('ĐẠT') || value.includes('DAT')) {
    return {
      className: 'is-ok',
      label: 'Đạt',
    };
  }
  return {
    className: 'is-unknown',
    label: 'Chưa rõ',
  };
}

function cleanReviewText(text) {
  return String(text ?? '').replaceAll('*', '');
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
  const [savedSystemPrompt, setSavedSystemPrompt] = useState('');
  const [isPromptLoading, setIsPromptLoading] = useState(false);
  const [promptStatus, setPromptStatus] = useState('');
  const [toastMessage, setToastMessage] = useState('');
  const [isToastVisible, setIsToastVisible] = useState(false);
  const [recordFile, setRecordFile] = useState(null);
  const [recordCheckResult, setRecordCheckResult] = useState(null);
  const [recordCheckError, setRecordCheckError] = useState('');
  const [isCheckingRecord, setIsCheckingRecord] = useState(false);
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(true);
  const [isModeMenuOpen, setIsModeMenuOpen] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

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
      const prompt = data.prompt ?? '';
      setSystemPrompt(prompt);
      setSavedSystemPrompt(prompt);
    } catch (error) {
      setPromptStatus(`Không thể tải prompt: ${error.message}`);
    } finally {
      setIsPromptLoading(false);
    }
  }

  async function saveSystemPrompt() {
    const value = systemPrompt.trim();
    if (!value || value === savedSystemPrompt.trim() || isPromptLoading) return;

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
      const savedPrompt = data.prompt ?? value;
      setSystemPrompt(savedPrompt);
      setSavedSystemPrompt(savedPrompt);
      setPromptStatus('');
      setToastMessage('Thành công, bạn đã lưu thay đổi prompt thành công');
      setIsToastVisible(true);
      window.setTimeout(() => setIsToastVisible(false), 2600);
      window.setTimeout(() => setToastMessage(''), 3200);
    } catch (error) {
      setPromptStatus(`Không thể lưu prompt: ${error.message}`);
    } finally {
      setIsPromptLoading(false);
    }
  }

  async function handleRecordCheck(event) {
    event.preventDefault();
    if (!recordFile || isCheckingRecord) return;

    const formData = new FormData();
    formData.append('file', recordFile);

    setIsCheckingRecord(true);
    setRecordCheckError('');
    setRecordCheckResult(null);

    try {
      const response = await fetch(MEDICAL_RECORD_CHECK_API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API trả về lỗi ${response.status}`);
      }

      const data = await response.json();
      setRecordCheckResult(data);
    } catch (error) {
      setRecordCheckError(`Không thể kiểm tra bệnh án: ${error.message}`);
    } finally {
      setIsCheckingRecord(false);
    }
  }

  return (
    <main className={`app-shell ${isSidebarOpen ? '' : 'is-sidebar-collapsed'}`}>
      {toastMessage && (
        <div className={`toast-success ${isToastVisible ? 'is-visible' : 'is-hidden'}`}>
          <div className="toast-success-icon">✓</div>
          <div>
            <strong>Thành công</strong>
            <span>{toastMessage.replace('Thành công, ', '')}</span>
          </div>
        </div>
      )}

      <aside className="sidebar">
        <button
          className="sidebar-toggle"
          onClick={() => setIsSidebarOpen((current) => !current)}
          type="button"
        >
          {isSidebarOpen ? (
            <ChevronLeft aria-hidden="true" size={18} />
          ) : (
            <ChevronRight aria-hidden="true" size={18} />
          )}
        </button>

        <div className="brand">
          <div className="brand-mark">
            <Stethoscope aria-hidden="true" size={24} strokeWidth={2} />
          </div>
          <div className="brand-text">
            <h1>Medic AI</h1>
            <p>Bệnh Viện ĐKQT Bắc Hà</p>
          </div>
        </div>

        <nav className="mode-panel" aria-label="Menu chính">
          <p className="sidebar-menu-label">Menu chính</p>

          <button
            className={`sidebar-parent-button ${isAccountMenuOpen ? 'is-open' : ''}`}
            onClick={() => setIsAccountMenuOpen((current) => !current)}
            type="button"
          >
            <User aria-hidden="true" size={17} />
            <span>Quản Lý Tài Khoản</span>
            <ChevronDown aria-hidden="true" size={15} />
          </button>

          {isAccountMenuOpen && (
            <div className="sidebar-submenu">
              <button className="sidebar-subitem" type="button">
                <KeyRound aria-hidden="true" size={14} />
                <span>Thông tin cá nhân</span>
              </button>
              <button className="sidebar-subitem" type="button">
                <Settings aria-hidden="true" size={14} />
                <span>Cài đặt mật khẩu</span>
              </button>
              <button className="sidebar-subitem" type="button">
                <Users aria-hidden="true" size={14} />
                <span>Danh sách người dùng</span>
              </button>
              <button className="sidebar-subitem" type="button">
                <Archive aria-hidden="true" size={14} />
                <span>Phân quyền</span>
              </button>
            </div>
          )}

          <button
            className={`sidebar-parent-button ${isModeMenuOpen ? 'is-open' : ''}`}
            onClick={() => setIsModeMenuOpen((current) => !current)}
            type="button"
          >
            <Folder aria-hidden="true" size={17} />
            <span>Quản Lý Tài Liệu</span>
            <ChevronDown aria-hidden="true" size={15} />
          </button>

          {isModeMenuOpen && (
            <div className="sidebar-submenu">
              {modes.map((mode) => {
                const Icon = mode.icon;
                return (
                  <button
                    className={`sidebar-subitem ${activeMode === mode.id ? 'is-active' : ''}`}
                    key={mode.id}
                    onClick={() => setActiveMode(mode.id)}
                    type="button"
                    title={mode.label}
                  >
                    <Icon aria-hidden="true" size={14} />
                    <span>{mode.label}</span>
                  </button>
                );
              })}
            </div>
          )}

          <button className="sidebar-link-button" type="button">
            <Settings aria-hidden="true" size={17} />
            <span>Cấu hình Hệ thống</span>
          </button>
          <button className="sidebar-link-button" type="button">
            <BarChart3 aria-hidden="true" size={17} />
            <span>Báo cáo & Thống kê</span>
          </button>
          <button className="sidebar-link-button" type="button">
            <Bell aria-hidden="true" size={17} />
            <span>Thông báo & Tin nhắn</span>
          </button>
        </nav>

        <div className="sidebar-user">
          <div className="sidebar-avatar" aria-hidden="true">
            AI
          </div>
          <div className="sidebar-user-text">
            <strong>Admin</strong>
            <span>Medic AI</span>
          </div>
          <button className="sidebar-logout" type="button" title="Đăng xuất">
            <LogOut aria-hidden="true" size={18} />
          </button>
        </div>
      </aside>

      <section className="chat-area">
        {activeMode === 'record-check' && isCheckingRecord && (
          <div className="top-loading-bar" aria-hidden="true" />
        )}
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

        {activeMode === 'record-check' ? (
          <div className="record-check-area">
            <form className="record-upload-panel" onSubmit={handleRecordCheck}>
              <label className="record-file-picker">
                <Upload aria-hidden="true" size={24} />
                <span>{recordFile ? recordFile.name : 'Chọn file JSON bệnh án'}</span>
                <input
                  accept="application/json,.json"
                  disabled={isCheckingRecord}
                  onChange={(event) => {
                    setRecordFile(event.target.files?.[0] ?? null);
                    setRecordCheckError('');
                    setRecordCheckResult(null);
                  }}
                  type="file"
                />
              </label>

              <button disabled={!recordFile || isCheckingRecord} type="submit">
                {isCheckingRecord ? 'Đang kiểm tra...' : 'Kiểm tra bệnh án'}
              </button>
            </form>

            {recordCheckError && <p className="record-check-error">{recordCheckError}</p>}

            {recordCheckResult && (
              <section className="record-check-result">
                <h3>
                  {recordReviewSections
                    .map((section) => cleanReviewText(recordCheckResult.details?.[section.key]))
                    .some(hasReviewError)
                    ? 'Cần rà soát bệnh án'
                    : 'Bệnh án hợp lệ'}
                </h3>
                <div className="record-check-grid">
                  {recordReviewSections.map((section) => {
                    const detail = cleanReviewText(recordCheckResult.details?.[section.key]);
                    const status = getReviewStatus(detail);
                    return (
                      <article key={section.key}>
                        <span>{section.label}</span>
                        <strong className={status.className}>{status.label}</strong>
                        <p>{detail}</p>
                      </article>
                    );
                  })}
                </div>
              </section>
            )}
          </div>
        ) : (
          <>
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
          </>
        )}
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
              <button
                disabled={
                  isPromptLoading ||
                  !systemPrompt.trim() ||
                  systemPrompt.trim() === savedSystemPrompt.trim()
                }
                onClick={saveSystemPrompt}
                type="button"
              >
                {isPromptLoading ? 'Đang xử lý...' : 'Lưu prompt'}
              </button>
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}
