import { React, run } from "uebersicht";

// === Configuration ===
const API_BASE = "http://127.0.0.1:8787";
const AUTH_TOKEN = "f8a3b7e6d2c1a0b9e8f7d6c5b4a32109";

// === Main Component: Styles ===
export const className = `
  position: fixed;
  left: 50%;
  top: 35px;
  transform: translateX(-50%);
  width: 360px;
  max-height: 80vh;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.95));
  -webkit-backdrop-filter: blur(24px);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  border: 1px solid rgba(99, 102, 241, 0.25);
  color: #e2e8f0;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  font-size: 13px;
  line-height: 1.5;
  box-shadow:
    0 24px 48px rgba(0, 0, 0, 0.4),
    0 8px 16px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 1000;
`;
export const refreshFrequency = 300000; // Auto-refresh every 5 minutes

// === API Helpers ===
const fetchWords = async () => {
  const cmd = `curl -sS -H "X-Auth: ${AUTH_TOKEN}" "${API_BASE}/words"`;
  const out = await run(cmd);
  try {
    return JSON.parse(out);
  } catch (e) {
    throw new Error(out || String(e));
  }
};

const toggleWord = async (index) => {
  const payload = JSON.stringify({ index });
  const cmd = `curl -sS -X POST -H "X-Auth: ${AUTH_TOKEN}" -H "Content-Type: application/json" -d '${payload}' "${API_BASE}/words/toggle"`;
  const out = await run(cmd);
  try {
    return JSON.parse(out);
  } catch (e) {
    throw new Error(out || String(e));
  }
};

const addWords = async (words) => {
  const payload = JSON.stringify({ words });
  const escaped = payload.replace(/'/g, "'\"'\"'");
  const cmd = `curl -sS -X POST -H "X-Auth: ${AUTH_TOKEN}" -H "Content-Type: application/json" -d '${escaped}' "${API_BASE}/words/add"`;
  const out = await run(cmd);
  try {
    return JSON.parse(out);
  } catch (e) {
    throw new Error(out || String(e));
  }
};

// === Main Component ===
function WordsWidget() {
  const [state, setState] = React.useState({
    loading: true, error: "", words: [], total: 0, checked: 0, unchecked: 0,
  });
  const [toggling, setToggling] = React.useState(null);
  const [adding, setAdding] = React.useState(false);
  const [newWord, setNewWord] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const inputRef = React.useRef(null);

  const load = React.useCallback(async () => {
    try {
      setState((s) => ({ ...s, loading: !s.words.length, error: "" }));
      const data = await fetchWords();
      setState({
        loading: false, error: "",
        words: data.words || [],
        total: data.total || 0,
        checked: data.checked || 0,
        unchecked: data.unchecked || 0,
      });
    } catch (e) {
      setState((s) => ({ ...s, loading: false, error: String(e) }));
    }
  }, []);

  React.useEffect(() => { load(); }, [load]);

  const onToggle = async (wordObj) => {
    setToggling(wordObj.index);
    // Optimistic update
    setState((s) => {
      const updated = s.words.map((w) =>
        w.index === wordObj.index ? { ...w, checked: !w.checked } : w
      );
      const checked = updated.filter((w) => w.checked).length;
      return { ...s, words: updated, checked, unchecked: updated.length - checked };
    });
    try {
      await toggleWord(wordObj.index);
    } catch (e) {
      setState((s) => ({ ...s, error: String(e) }));
      await load();
    } finally {
      setToggling(null);
    }
  };

  const onAdd = async () => {
    const word = newWord.trim();
    if (!word || submitting) return;
    setSubmitting(true);
    try {
      await addWords([word]);
      setNewWord("");
      await load();
    } catch (e) {
      setState((s) => ({ ...s, error: String(e) }));
    } finally {
      setSubmitting(false);
    }
  };

  React.useEffect(() => {
    if (adding && inputRef.current) inputRef.current.focus();
  }, [adding]);

  const uncheckedWords = state.words.filter((w) => !w.checked);
  const progressPct = state.total > 0 ? Math.round((state.checked / state.total) * 100) : 0;

  if (state.loading && !state.words.length) {
    return <div className="wd-loading">Loading words...</div>;
  }

  return (
    <>
      <style>{`
        .wd-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 14px 18px 10px;
          border-bottom: 1px solid rgba(99, 102, 241, 0.15);
          flex-shrink: 0;
        }
        .wd-title {
          font-size: 15px;
          font-weight: 700;
          background: linear-gradient(135deg, #a78bfa, #818cf8);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          letter-spacing: 0.3px;
        }
        

        .wd-progress-section {
          padding: 10px 18px 8px;
          flex-shrink: 0;
        }
        .wd-stats {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          color: #94a3b8;
          margin-bottom: 6px;
        }
        .wd-stats-highlight {
          color: #a78bfa;
          font-weight: 600;
        }
        .wd-progress-bar {
          width: 100%;
          height: 6px;
          background: rgba(99, 102, 241, 0.1);
          border-radius: 3px;
          overflow: hidden;
        }
        .wd-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #818cf8, #a78bfa);
          border-radius: 3px;
          transition: width 0.4s ease;
        }

        .wd-list {
          padding: 6px 12px 12px;
          overflow-y: auto;
          flex-grow: 1;
        }
        .wd-word-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 10px;
          margin-bottom: 4px;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.2s ease;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(99, 102, 241, 0.08);
        }
        .wd-word-item:hover {
          background: rgba(99, 102, 241, 0.1);
          border-color: rgba(99, 102, 241, 0.2);
          transform: translateX(3px);
        }
        .wd-word-item.is-toggling {
          opacity: 0.5;
          pointer-events: none;
        }
        .wd-checkbox {
          width: 18px;
          height: 18px;
          border-radius: 5px;
          border: 2px solid rgba(99, 102, 241, 0.4);
          background: transparent;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          transition: all 0.2s ease;
        }
        .wd-word-item:hover .wd-checkbox {
          border-color: #818cf8;
          background: rgba(99, 102, 241, 0.1);
        }
        .wd-word-text {
          flex-grow: 1;
          font-size: 15px;
          font-weight: 500;
          color: #e2e8f0;
          letter-spacing: 0.2px;
          font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }
        .wd-word-index {
          font-size: 10px;
          color: #475569;
          font-variant-numeric: tabular-nums;
          min-width: 18px;
          text-align: right;
        }

        .wd-empty {
          padding: 30px 20px;
          text-align: center;
          color: #64748b;
          font-style: italic;
        }
        .wd-empty-icon {
          font-size: 28px;
          margin-bottom: 8px;
          opacity: 0.6;
        }
        .wd-loading {
          padding: 30px;
          text-align: center;
          color: #64748b;
          font-style: italic;
        }
        .wd-header-btns {
          display: flex;
          gap: 6px;
        }
        .wd-header-btn {
          cursor: pointer;
          background: rgba(99, 102, 241, 0.15);
          border: 1px solid rgba(99, 102, 241, 0.25);
          color: #a5b4fc;
          border-radius: 8px;
          width: 30px;
          height: 30px;
          font-size: 16px;
          font-weight: bold;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }
        .wd-header-btn:hover {
          background: rgba(99, 102, 241, 0.25);
          color: #c4b5fd;
        }

        .wd-add-row {
          display: flex;
          gap: 8px;
          padding: 8px 14px;
          border-bottom: 1px solid rgba(99, 102, 241, 0.1);
          flex-shrink: 0;
        }
        .wd-add-input {
          flex-grow: 1;
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid rgba(99, 102, 241, 0.25);
          border-radius: 8px;
          padding: 6px 12px;
          color: #e2e8f0;
          font-size: 14px;
          font-family: "SF Pro Text", "Helvetica Neue", sans-serif;
          outline: none;
          transition: border-color 0.2s ease;
        }
        .wd-add-input:focus {
          border-color: #818cf8;
        }
        .wd-add-input::placeholder {
          color: #64748b;
        }
        .wd-add-input:disabled {
          opacity: 0.5;
        }
        .wd-add-btn {
          cursor: pointer;
          background: linear-gradient(135deg, #818cf8, #6366f1);
          border: none;
          color: #fff;
          border-radius: 8px;
          padding: 6px 14px;
          font-size: 12px;
          font-weight: 600;
          transition: all 0.2s ease;
        }
        .wd-add-btn:hover {
          background: linear-gradient(135deg, #a78bfa, #818cf8);
        }
        .wd-add-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .wd-error {
          margin: 8px 12px;
          padding: 8px 12px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 8px;
          color: #fca5a5;
          font-size: 11px;
        }
      `}</style>

      <div className="wd-header">
        <span className="wd-title">Words to Memorize</span>
        <div className="wd-header-btns">
          <button className="wd-header-btn" onClick={() => setAdding((v) => !v)} title="Add word">+</button>
          <button className="wd-header-btn" onClick={load} title="Refresh">↻</button>
        </div>
      </div>

      <div className="wd-progress-section">
        <div className="wd-stats">
          <span>
            <span className="wd-stats-highlight">{state.checked}</span> / {state.total} memorized
          </span>
          <span className="wd-stats-highlight">{progressPct}%</span>
        </div>
        <div className="wd-progress-bar">
          <div className="wd-progress-fill" style={{ width: `${progressPct}%` }} />
        </div>
      </div>

      {state.error && <div className="wd-error">{state.error}</div>}

      {adding && (
        <div className="wd-add-row">
          <input
            ref={inputRef}
            className="wd-add-input"
            type="text"
            placeholder="Type a new word…"
            value={newWord}
            onChange={(e) => setNewWord(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") onAdd(); if (e.key === "Escape") { setAdding(false); setNewWord(""); } }}
            disabled={submitting}
          />
          <button className="wd-add-btn" onClick={onAdd} disabled={submitting || !newWord.trim()}>
            {submitting ? "…" : "Add"}
          </button>
        </div>
      )}

      <div className="wd-list">
        {uncheckedWords.length === 0 ? (
          <div className="wd-empty">
            <div className="wd-empty-icon">&#10024;</div>
            <div>All words memorized!</div>
          </div>
        ) : (
          uncheckedWords.map((w, i) => (
            <div
              key={w.index}
              className={`wd-word-item ${toggling === w.index ? "is-toggling" : ""}`}
              onClick={() => onToggle(w)}
            >
              <div className="wd-checkbox" />
              <div className="wd-word-text">{w.word}</div>
              <div className="wd-word-index">{i + 1}</div>
            </div>
          ))
        )}
      </div>
    </>
  );
}

export const render = (props) => <WordsWidget {...props} />;