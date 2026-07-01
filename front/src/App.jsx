import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  LogOut,
  Mic,
  Send,
  Settings,
  Search,
  Square,
  Stethoscope,
  ThumbsDown,
  ThumbsUp,
  User,
} from 'lucide-react';

const API_URL = 'http://10.10.50.226:8083/chat';
const CHAT_FEEDBACK_API_URL = 'http://10.10.50.226:8083/chat/feedback';
const SYSTEM_PROMPT_API_URL = 'http://10.10.50.226:8083/system-prompt';
const MEDICAL_RECORD_CHECK_API_URL = 'http://10.10.50.226:8083/medical-record/check-json';
const SINGLE_DOCUMENT_CHECK_API_URL = 'http://10.10.50.226:8083/medical-record/check-json/one';
const DOCUMENT_PROMPT_API_URL = 'http://10.10.50.226:8083/medical-record/document-prompt';
const MULTI_DOCUMENT_PROMPT_API_URL = 'http://10.10.50.226:8083/medical-record/multi-document-prompt';
const VOICE_TRANSCRIBE_API_URL = 'http://10.10.50.226:8083/voice/transcribe';
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

const DEFAULT_FEEDBACK_USER_ID = 'user_123';

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

function createMessageId() {
  if (crypto.randomUUID) {
    return `message-${crypto.randomUUID()}`;
  }

  return `message-${Date.now()}-${Math.random().toString(16).slice(2)}`;
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
  const [recordReceptionCode, setRecordReceptionCode] = useState('');
  const [selectedRecordDocumentType, setSelectedRecordDocumentType] = useState('');
  const [recordCheckResult, setRecordCheckResult] = useState(null);
  const [recordCheckResultMode, setRecordCheckResultMode] = useState('');
  const [recordCheckError, setRecordCheckError] = useState('');
  const [isCheckingRecord, setIsCheckingRecord] = useState(false);
  const [documentPrompt, setDocumentPrompt] = useState('');
  const [savedDocumentPrompt, setSavedDocumentPrompt] = useState('');
  const [isDocumentPromptLoading, setIsDocumentPromptLoading] = useState(false);
  const [documentPromptStatus, setDocumentPromptStatus] = useState('');
  const [isMultiDocumentPromptOpen, setIsMultiDocumentPromptOpen] = useState(false);
  const [multiDocumentPrompt, setMultiDocumentPrompt] = useState('');
  const [savedMultiDocumentPrompt, setSavedMultiDocumentPrompt] = useState('');
  const [isMultiDocumentPromptLoading, setIsMultiDocumentPromptLoading] = useState(false);
  const [multiDocumentPromptStatus, setMultiDocumentPromptStatus] = useState('');
  const [isMainMenuOpen, setIsMainMenuOpen] = useState(true);
  const [isDocumentMenuOpen, setIsDocumentMenuOpen] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const [isTranscribingVoice, setIsTranscribingVoice] = useState(false);
  const [voiceError, setVoiceError] = useState('');
  const mediaRecorderRef = useRef(null);
  const voiceChunksRef = useRef([]);
  const voiceStreamRef = useRef(null);

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

  const selectedRecordDocument = useMemo(
    () => recordReviewSections.find((section) => section.key === selectedRecordDocumentType),
    [selectedRecordDocumentType],
  );

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

  useEffect(
    () => () => {
      if (mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      stopVoiceStream();
    },
    [],
  );

  useEffect(() => {
    setRecordReceptionCode('');
    setSelectedRecordDocumentType('');
    setRecordCheckResult(null);
    setRecordCheckResultMode('');
    setRecordCheckError('');
    setDocumentPrompt('');
    setSavedDocumentPrompt('');
    setDocumentPromptStatus('');
    setIsMultiDocumentPromptOpen(false);
    setMultiDocumentPrompt('');
    setSavedMultiDocumentPrompt('');
    setMultiDocumentPromptStatus('');
  }, [activeMode]);

  useEffect(() => {
    if (activeMode !== 'record-check-single' || !selectedRecordDocumentType) {
      setDocumentPrompt('');
      setSavedDocumentPrompt('');
      setDocumentPromptStatus('');
      return undefined;
    }

    const controller = new AbortController();

    async function loadDocumentPrompt() {
      setIsDocumentPromptLoading(true);
      setDocumentPromptStatus('');

      try {
        const response = await fetch(`${DOCUMENT_PROMPT_API_URL}/${selectedRecordDocumentType}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`API trả về lỗi ${response.status}`);
        }

        const data = await response.json();
        const prompt = data.prompt ?? '';
        setDocumentPrompt(prompt);
        setSavedDocumentPrompt(prompt);
      } catch (error) {
        if (error.name !== 'AbortError') {
          setDocumentPrompt('');
          setSavedDocumentPrompt('');
          setDocumentPromptStatus(`Không thể tải prompt: ${error.message}`);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsDocumentPromptLoading(false);
        }
      }
    }

    loadDocumentPrompt();

    return () => controller.abort();
  }, [activeMode, selectedRecordDocumentType]);

  async function handleSubmit(event) {
    event.preventDefault();

    const value = input.trim();
    if (!value || isSending) return;

    setInput('');
    setIsSending(true);
    setMessages((current) => [...current, { id: createMessageId(), role: 'user', text: value }]);

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
          id: createMessageId(),
          role: 'assistant',
          text: getAssistantText(data),
          question: value,
          feedback: null,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: 'assistant',
          text: `Không thể gọi API: ${error.message}`,
          canFeedback: false,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function stopVoiceStream() {
    voiceStreamRef.current?.getTracks().forEach((track) => track.stop());
    voiceStreamRef.current = null;
  }

  async function transcribeVoiceBlob(blob) {
    if (!blob.size) {
      setVoiceError('Khong thu duoc am thanh.');
      return;
    }

    setIsTranscribingVoice(true);
    setVoiceError('');

    try {
      const formData = new FormData();
      formData.append('file', blob, 'voice.webm');

      const response = await fetch(VOICE_TRANSCRIBE_API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let detail = `API tra ve loi ${response.status}`;
        try {
          const errorData = await response.json();
          detail = errorData.detail ?? detail;
        } catch {
          // Giu loi HTTP mac dinh neu server khong tra JSON.
        }
        throw new Error(detail);
      }

      const data = await response.json();
      const text = String(data.text ?? '').trim();
      if (!text) {
        setVoiceError('Khong nhan dien duoc noi dung giong noi.');
        return;
      }

      setInput((current) => (current.trim() ? `${current.trim()} ${text}` : text));
    } catch (error) {
      setVoiceError(`Khong the chuyen giong noi thanh text: ${error.message}`);
    } finally {
      setIsTranscribingVoice(false);
    }
  }

  async function startVoiceRecording() {
    if (isSending || isTranscribingVoice || isRecordingVoice) return;
    if (!window.isSecureContext) {
      setVoiceError('Trinh duyet chi cho ghi am tren HTTPS hoac localhost.');
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setVoiceError('Trinh duyet khong ho tro ghi am.');
      return;
    }

    setVoiceError('');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      voiceStreamRef.current = stream;
      voiceChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          voiceChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(voiceChunksRef.current, { type: mediaRecorder.mimeType || 'audio/webm' });
        voiceChunksRef.current = [];
        stopVoiceStream();
        transcribeVoiceBlob(blob);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecordingVoice(true);
    } catch (error) {
      stopVoiceStream();
      setVoiceError(`Khong the bat micro: ${error.message}`);
    }
  }

  function stopVoiceRecording() {
    const mediaRecorder = mediaRecorderRef.current;
    if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
    mediaRecorder.stop();
    mediaRecorderRef.current = null;
    setIsRecordingVoice(false);
  }

  function handleVoiceButton() {
    if (isRecordingVoice) {
      stopVoiceRecording();
      return;
    }

    startVoiceRecording();
  }

  async function handleChatFeedback(messageId, isLiked) {
    const targetMessage = messages.find((message) => message.id === messageId);
    if (!targetMessage || targetMessage.role !== 'assistant' || targetMessage.canFeedback === false) {
      return;
    }

    const content = `Câu hỏi: ${targetMessage.question ?? ''}\n\nCâu trả lời: ${targetMessage.text}`;

    setMessages((current) =>
      current.map((message) =>
        message.id === messageId
          ? {
              ...message,
              feedback: isLiked,
              isFeedbackSaving: true,
            }
          : message,
      ),
    );

    try {
      const response = await fetch(CHAT_FEEDBACK_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: DEFAULT_FEEDBACK_USER_ID,
          thread_id: threadId,
          like: isLiked,
          content,
        }),
      });

      if (!response.ok) {
        throw new Error(`API trả về lỗi ${response.status}`);
      }

      setMessages((current) =>
        current.map((message) =>
          message.id === messageId
            ? {
                ...message,
                feedback: isLiked,
                isFeedbackSaving: false,
              }
            : message,
        ),
      );
    } catch (error) {
      setMessages((current) =>
        current.map((message) =>
          message.id === messageId
            ? {
                ...message,
                feedback: null,
                isFeedbackSaving: false,
              }
            : message,
        ),
      );
      showToast(`Không thể lưu đánh giá: ${error.message}`, 'error');
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

  async function saveDocumentPrompt() {
    const value = documentPrompt.trim();
    if (
      !value ||
      value === savedDocumentPrompt.trim() ||
      isDocumentPromptLoading ||
      !selectedRecordDocumentType
    ) {
      return;
    }

    setIsDocumentPromptLoading(true);
    setDocumentPromptStatus('');

    try {
      const response = await fetch(`${DOCUMENT_PROMPT_API_URL}/${selectedRecordDocumentType}`, {
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
      setDocumentPrompt(savedPrompt);
      setSavedDocumentPrompt(savedPrompt);
      setDocumentPromptStatus('');
      showToast('Thành công, bạn đã lưu prompt giấy tờ thành công', 'success');
    } catch (error) {
      setDocumentPromptStatus(`Không thể lưu prompt: ${error.message}`);
    } finally {
      setIsDocumentPromptLoading(false);
    }
  }

  async function openMultiDocumentPrompt() {
    setIsMultiDocumentPromptOpen(true);
    setIsMultiDocumentPromptLoading(true);
    setMultiDocumentPromptStatus('');

    try {
      const response = await fetch(MULTI_DOCUMENT_PROMPT_API_URL);

      if (!response.ok) {
        throw new Error(`API trả về lỗi ${response.status}`);
      }

      const data = await response.json();
      const prompt = data.prompt ?? '';
      setMultiDocumentPrompt(prompt);
      setSavedMultiDocumentPrompt(prompt);
    } catch (error) {
      setMultiDocumentPrompt('');
      setSavedMultiDocumentPrompt('');
      setMultiDocumentPromptStatus(`Không thể tải prompt: ${error.message}`);
    } finally {
      setIsMultiDocumentPromptLoading(false);
    }
  }

  async function saveMultiDocumentPrompt() {
    const value = multiDocumentPrompt.trim();
    if (
      !value ||
      value === savedMultiDocumentPrompt.trim() ||
      isMultiDocumentPromptLoading
    ) {
      return;
    }

    setIsMultiDocumentPromptLoading(true);
    setMultiDocumentPromptStatus('');

    try {
      const response = await fetch(MULTI_DOCUMENT_PROMPT_API_URL, {
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
      setMultiDocumentPrompt(savedPrompt);
      setSavedMultiDocumentPrompt(savedPrompt);
      setMultiDocumentPromptStatus('');
      showToast('Thành công, bạn đã lưu prompt nhiều tài liệu thành công', 'success');
    } catch (error) {
      setMultiDocumentPromptStatus(`Không thể lưu prompt: ${error.message}`);
    } finally {
      setIsMultiDocumentPromptLoading(false);
    }
  }

  async function handleRecordCheck(event) {
    event.preventDefault();
    const maTiepNhan = recordReceptionCode.trim();
    if (!maTiepNhan || isCheckingRecord) return;
    if (activeMode === 'record-check-single' && !selectedRecordDocumentType) return;

    const submittedMode = activeMode;
    const requestBody = {
      ma_tiep_nhan: maTiepNhan,
    };
    if (submittedMode === 'record-check-single') {
      requestBody.type = selectedRecordDocumentType;
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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
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
      setRecordCheckError(`Không thể kiểm tra tài liệu: do sai mã tiếp nhận hoặc người bệnh không có phiếu này`);
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
              {/* Code cũ: upload file JSON tài liệu. */}
              {/* <label className="record-file-picker">...</label> */}
              <label className="record-code-picker">
                <Search aria-hidden="true" size={24} />
                <span>Mã tiếp nhận</span>
                <input
                  disabled={isCheckingRecord}
                  onChange={(event) => {
                    setRecordReceptionCode(event.target.value);
                    setRecordCheckError('');
                    setRecordCheckResult(null);
                    setRecordCheckResultMode('');
                  }}
                  placeholder="Nhập mã tiếp nhận, ví dụ: 2602260097"
                  type="text"
                  value={recordReceptionCode}
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
                          onChange={() => {
                            setSelectedRecordDocumentType(section.key);
                            setRecordCheckError('');
                            setRecordCheckResult(null);
                            setRecordCheckResultMode('');
                          }}
                          type="radio"
                          value={section.key}
                        />
                        <span>{section.label}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>
              )}

              {activeMode === 'record-check-single' && selectedRecordDocumentType && (
                <section className="record-document-prompt-panel">
                  <div className="record-document-prompt-header">
                    <div>
                      <span>Giấy tờ đã chọn</span>
                      <strong>{selectedRecordDocument?.label ?? selectedRecordDocumentType}</strong>
                    </div>
                    <button
                      disabled={
                        isDocumentPromptLoading ||
                        !documentPrompt.trim() ||
                        documentPrompt.trim() === savedDocumentPrompt.trim()
                      }
                      onClick={saveDocumentPrompt}
                      type="button"
                    >
                      {isDocumentPromptLoading ? 'Đang xử lý...' : 'Lưu prompt'}
                    </button>
                  </div>
                  <label className="record-document-prompt-editor">
                    <span>Prompt tương ứng</span>
                    <textarea
                      disabled={isDocumentPromptLoading}
                      onChange={(event) => setDocumentPrompt(event.target.value)}
                      placeholder="Prompt kiểm tra giấy tờ"
                      value={documentPrompt}
                    />
                  </label>
                  {documentPromptStatus && (
                    <p className="record-document-prompt-status">{documentPromptStatus}</p>
                  )}
                </section>
              )}

              <div className="record-note-box">
                <strong>Lưu ý:</strong>
                <span>TTHSBA: Tóm tắt hồ sơ bệnh án</span>
                <span>GRV: Giấy ra viện</span>
                <span>TTTKBA: Thông tin tổng kết bệnh án</span>
                <span>TTRV: Thông tin ra viện</span>
                <span>TTBA: Thông tin bệnh án</span>
              </div>

              <div className="record-action-row">
                <button
                  disabled={
                    !recordReceptionCode.trim() ||
                    isCheckingRecord ||
                    (activeMode === 'record-check-single' && !selectedRecordDocumentType)
                  }
                  type="submit"
                >
                  {isCheckingRecord ? 'Đang kiểm tra...' : 'Kiểm tra tài liệu'}
                </button>

                {activeMode === 'record-check-multiple' && (
                  <button
                    disabled={isMultiDocumentPromptLoading}
                    onClick={openMultiDocumentPrompt}
                    type="button"
                  >
                    {isMultiDocumentPromptOpen ? 'Xem prompt' : 'Xem/chỉnh prompt'}
                  </button>
                )}
              </div>

              {activeMode === 'record-check-multiple' && isMultiDocumentPromptOpen && (
                <section className="record-document-prompt-panel">
                  <div className="record-document-prompt-header">
                    <div>
                      <span>Prompt đang dùng</span>
                      <strong>Nhiều tài liệu</strong>
                    </div>
                    <button
                      disabled={
                        isMultiDocumentPromptLoading ||
                        !multiDocumentPrompt.trim() ||
                        multiDocumentPrompt.trim() === savedMultiDocumentPrompt.trim()
                      }
                      onClick={saveMultiDocumentPrompt}
                      type="button"
                    >
                      {isMultiDocumentPromptLoading ? 'Đang xử lý...' : 'Lưu prompt'}
                    </button>
                  </div>
                  <label className="record-document-prompt-editor">
                    <span>Prompt tương ứng</span>
                    <textarea
                      disabled={isMultiDocumentPromptLoading}
                      onChange={(event) => setMultiDocumentPrompt(event.target.value)}
                      placeholder="Prompt kiểm tra nhiều tài liệu"
                      value={multiDocumentPrompt}
                    />
                  </label>
                  {multiDocumentPromptStatus && (
                    <p className="record-document-prompt-status">{multiDocumentPromptStatus}</p>
                  )}
                </section>
              )}
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
                  <article
                    className={`message ${message.role}`}
                    key={message.id ?? `${message.role}-${index}`}
                  >
                    <span>{message.role === 'user' ? 'Người dùng' : 'Trả lời'}</span>
                    <p>{message.text}</p>
                    {message.role === 'assistant' && message.canFeedback !== false && (
                      <div className="message-feedback">
                        <button
                          aria-label="Like câu trả lời"
                          className={message.feedback === true ? 'is-selected' : ''}
                          disabled={message.isFeedbackSaving}
                          onClick={() => handleChatFeedback(message.id, true)}
                          type="button"
                        >
                          <ThumbsUp aria-hidden="true" size={14} />
                        </button>
                        <button
                          aria-label="Dislike câu trả lời"
                          className={message.feedback === false ? 'is-selected is-dislike' : ''}
                          disabled={message.isFeedbackSaving}
                          onClick={() => handleChatFeedback(message.id, false)}
                          type="button"
                        >
                          <ThumbsDown aria-hidden="true" size={14} />
                        </button>
                      </div>
                    )}
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
                <button
                  aria-label={isRecordingVoice ? 'Dung ghi am' : 'Ghi am trieu chung'}
                  className={`voice-button ${isRecordingVoice ? 'is-recording' : ''}`}
                  disabled={isSending || isTranscribingVoice}
                  onClick={handleVoiceButton}
                  type="button"
                >
                  {isRecordingVoice ? (
                    <Square aria-hidden="true" size={17} />
                  ) : (
                    <Mic aria-hidden="true" size={18} />
                  )}
                </button>
                <input
                  aria-label="Nhập câu hỏi"
                  disabled={isSending || isTranscribingVoice}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Nhập nội dung cần hỏi..."
                  type="text"
                  value={input}
                />
                <button aria-label="Gửi tin nhắn" disabled={isSending || isTranscribingVoice} type="submit">
                  <Send aria-hidden="true" size={18} />
                </button>
              </form>
              {(isRecordingVoice || isTranscribingVoice || voiceError) && (
                <p className={`voice-status ${voiceError ? 'is-error' : ''}`}>
                  {voiceError ||
                    (isRecordingVoice
                      ? 'Đang ghi âm triệu chứng, hãy bấm để dừng.'
                      : 'Đang chuyển giọng nói thành văn bản...')}
                </p>
              )}
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
