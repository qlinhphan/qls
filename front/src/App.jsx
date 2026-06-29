import { useEffect, useMemo, useState } from 'react';
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  LogOut,
  Send,
  Settings,
  Stethoscope,
  User,
  Upload,
} from 'lucide-react';

const API_URL = 'http://10.10.50.226:8001/chat';
const SYSTEM_PROMPT_API_URL = 'http://10.10.50.226:8001/system-prompt';
const MEDICAL_RECORD_CHECK_API_URL = 'http://10.10.50.226:8001/medical-record/check-json';
const SINGLE_DOCUMENT_CHECK_API_URL = 'http://10.10.50.226:8001/medical-record/check-json/one';
const THREAD_STORAGE_KEY = 'medical-chat-thread-id';
const welcomeMessage =
  'Xin chào, tôi là trợ lý AI của bạn, sẽ giúp đỡ bạn hôm nay.';

const mainModes = [
  {
    id: 'classification',
    label: 'Phân chuyên Khoa',
    icon: Stethoscope,
  },
];

const documentCheckModes = [
  {
    id: 'record-check-single',
    label: 'Trên một tài liệu',
    icon: ClipboardCheck,
  },
  {
    id: 'record-check-multiple',
    label: 'Trên nhiều tài liệu',
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

const extraRecordReviewLabels = {
  KiemTraNguNghiaGiuaCacFile: 'Kiểm tra ngữ nghĩa giữa các file',
};

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
  const [activeMode, setActiveMode] = useState(mainModes[0].id);
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
  const [toastVariant, setToastVariant] = useState('success');
  const [isToastVisible, setIsToastVisible] = useState(false);
  const [recordFile, setRecordFile] = useState(null);
  const [selectedRecordDocumentType, setSelectedRecordDocumentType] = useState('');
  const [recordCheckResult, setRecordCheckResult] = useState(null);
  const [recordCheckResultMode, setRecordCheckResultMode] = useState('');
  const [recordCheckError, setRecordCheckError] = useState('');
  const [isCheckingRecord, setIsCheckingRecord] = useState(false);
  const [isMainMenuOpen, setIsMainMenuOpen] = useState(true);
  const [isDocumentMenuOpen, setIsDocumentMenuOpen] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const modeTitle = useMemo(
    () =>
      [...mainModes, ...documentCheckModes].find((mode) => mode.id === activeMode)?.label ??
      mainModes[0].label,
    [activeMode],
  );

  const displayedRecordReviewSections = useMemo(() => {
    const details = recordCheckResult?.details;
    if (!details) return recordReviewSections;

    const knownSections = recordReviewSections.filter((section) =>
      Object.prototype.hasOwnProperty.call(details, section.key),
    );
    const extraSections = Object.keys(details)
      .filter((key) => !recordReviewSections.some((section) => section.key === key))
      .map((key) => ({
        key,
        label: extraRecordReviewLabels[key] ?? key,
      }));

    return [...knownSections, ...extraSections];
  }, [recordCheckResult]);

  function showToast(message, variant = 'success') {
    setToastMessage(message);
    setToastVariant(variant);
    setIsToastVisible(true);
    window.setTimeout(() => setIsToastVisible(false), 2600);
    window.setTimeout(() => setToastMessage(''), 3200);
  }

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

  useEffect(() => {
    setRecordFile(null);
    setSelectedRecordDocumentType('');
    setRecordCheckResult(null);
    setRecordCheckResultMode('');
    setRecordCheckError('');
  }, [activeMode]);

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
      showToast('Thành công, bạn đã lưu thay đổi prompt thành công', 'success');
    } catch (error) {
      setPromptStatus(`Không thể lưu prompt: ${error.message}`);
    } finally {
      setIsPromptLoading(false);
    }
  }

  async function handleRecordCheck(event) {
    event.preventDefault();
    if (!recordFile || isCheckingRecord) return;
    if (activeMode === 'record-check-single' && !selectedRecordDocumentType) return;

    const submittedMode = activeMode;
    const formData = new FormData();
    formData.append('file', recordFile);
    if (submittedMode === 'record-check-single') {
      formData.append('type', selectedRecordDocumentType);
    }
    const checkApiUrl =
      submittedMode === 'record-check-single'
        ? SINGLE_DOCUMENT_CHECK_API_URL
        : MEDICAL_RECORD_CHECK_API_URL;

    setIsCheckingRecord(true);
    setRecordCheckError('');
    setRecordCheckResult(null);
    setRecordCheckResultMode('');

    try {
      const response = await fetch(checkApiUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let detail = `API trả về lỗi ${response.status}`;
        try {
          const errorData = await response.json();
          detail = errorData.detail ?? detail;
        } catch {
          // Giữ lỗi HTTP mặc định nếu server không trả JSON.
        }
        throw new Error(detail);
      }

      const data = await response.json();
      setRecordCheckResult(data);
      setRecordCheckResultMode(submittedMode);
    } catch (error) {
      setRecordCheckError(`Không thể kiểm tra tài liệu: ${error.message}`);
      showToast(error.message, 'error');
    } finally {
      setIsCheckingRecord(false);
    }
  }

  return (
    <main className={`app-shell ${isSidebarOpen ? '' : 'is-sidebar-collapsed'}`}>
      {toastMessage && (
        <div
          className={`toast-success toast-${toastVariant} ${
            isToastVisible ? 'is-visible' : 'is-hidden'
          }`}
        >
          <div className="toast-success-icon">{toastVariant === 'error' ? '!' : '✓'}</div>
          <div>
            <strong>{toastVariant === 'error' ? 'Lỗi định dạng' : 'Thành công'}</strong>
            <span>{toastMessage.replace('Thành công, ', '').replace('Lỗi định dạng file - ', '')}</span>
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
          <p className="sidebar-menu-label">Chức năng chính</p>

          <button
            className={`sidebar-parent-button ${isMainMenuOpen ? 'is-open' : ''}`}
            onClick={() => setIsMainMenuOpen((current) => !current)}
            type="button"
          >
            <User aria-hidden="true" size={17} />
            <span>Phân luồng bệnh nhân</span>
            <ChevronDown aria-hidden="true" size={15} />
          </button>

          <div className={`sidebar-submenu ${isMainMenuOpen ? 'is-open' : 'is-closed'}`}>
            {mainModes.map((mode) => {
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

          <button
            className={`sidebar-parent-button ${isDocumentMenuOpen ? 'is-open' : ''}`}
            onClick={() => setIsDocumentMenuOpen((current) => !current)}
            type="button"
          >
            <ClipboardCheck aria-hidden="true" size={17} />
            <span>Kiểm Tra Tài Liệu</span>
            <ChevronDown aria-hidden="true" size={15} />
          </button>

          <div className={`sidebar-submenu ${isDocumentMenuOpen ? 'is-open' : 'is-closed'}`}>
            {documentCheckModes.map((mode) => {
              const Icon = mode.icon;
              const isMultipleCheck = mode.id === 'record-check-multiple';

              return (
                <div className="sidebar-subitem-wrap" key={mode.id}>
                  <button
                    className={`sidebar-subitem ${activeMode === mode.id ? 'is-active' : ''}`}
                    onClick={() => setActiveMode(mode.id)}
                    type="button"
                    title={mode.label}
                  >
                    <Icon aria-hidden="true" size={14} />
                    <span>{mode.label}</span>
                  </button>

                  {isMultipleCheck && (
                    <div className="document-hover-menu">
                      {recordReviewSections.map((section) => (
                        <span key={section.key}>{section.label}</span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
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
        {activeMode.startsWith('record-check') && isCheckingRecord && (
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

        {activeMode.startsWith('record-check') ? (
          <div className="record-check-area">
            <form className="record-upload-panel" onSubmit={handleRecordCheck}>
              <label className="record-file-picker">
                <Upload aria-hidden="true" size={24} />
                <span>{recordFile ? recordFile.name : 'Chọn file JSON tài liệu'}</span>
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

              {activeMode === 'record-check-single' && (
                <fieldset className="record-document-type-picker" disabled={isCheckingRecord}>
                  <legend>Chọn loại giấy tờ</legend>
                  <div>
                    {recordReviewSections.map((section) => (
                      <label
                        className={
                          selectedRecordDocumentType === section.key ? 'is-selected' : ''
                        }
                        key={section.key}
                      >
                        <input
                          checked={selectedRecordDocumentType === section.key}
                          name="record-document-type"
                          onChange={() => setSelectedRecordDocumentType(section.key)}
                          type="radio"
                          value={section.key}
                        />
                        <span>{section.label}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>
              )}

              <div className="record-note-box">
                <strong>Lưu ý:</strong>
                <span>TTHSBA: Tóm tắt hồ sơ bệnh án</span>
                <span>GRV: Giấy ra viện</span>
                <span>TTTKBA: Thông tin tổng kết bệnh án</span>
                <span>TTRV: Thông tin ra viện</span>
                <span>TTBA: Thông tin bệnh án</span>
              </div>

              <button
                disabled={
                  !recordFile ||
                  isCheckingRecord ||
                  (activeMode === 'record-check-single' && !selectedRecordDocumentType)
                }
                type="submit"
              >
                {isCheckingRecord ? 'Đang kiểm tra...' : 'Kiểm tra tài liệu'}
              </button>
            </form>

            {recordCheckError && <p className="record-check-error">{recordCheckError}</p>}

            {recordCheckResult && recordCheckResultMode === activeMode && (
              <section className="record-check-result">
                <h3>
                  {displayedRecordReviewSections
                    .map((section) => cleanReviewText(recordCheckResult.details?.[section.key]))
                    .some(hasReviewError)
                    ? 'Cần rà soát tài liệu'
                    : 'Tài liệu hợp lệ'}
                </h3>
                <div className="record-check-grid">
                  {displayedRecordReviewSections.map((section) => {
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
