import { React, run } from "uebersicht";

// === Configuration ===
const HABITS = [
  { id: "coding", name: "Coding", color: "#3b82f6" },
  { id: "no_scrolling", name: "No Scrolling", color: "#10b981" },
  { id: "journal", name: "Journal", color: "#8b5cf6" },
];

const WEB_INTERFACE_PORT = 8788; // Backend server port

const getHomeDir = async () => {
  const output = await run('echo $HOME');
  return output.trim();
};

// === Styles ===
export const className = `
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 420px;
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(31, 41, 55, 0.98));
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(75, 85, 99, 0.3);
  color: #f9fafb;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  font-size: 12px;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  z-index: 1000;
`;

export const refreshFrequency = false;

// === Utility Functions ===
const getDateString = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

const getDayOfWeek = (date) => {
  return date.getDay(); // 0 = Sunday, 6 = Saturday
};

const getWeeksData3Months = () => {
  const weeks = [];
  const today = new Date();
  
  // Always show 2026 data only
  const currentMonth = today.getMonth(); // 0-11
  const targetYear = 2026;
  
  // Determine which 3 months to show (stay within 2026)
  let startMonth, endMonth;
  
  if (currentMonth === 0 || currentMonth === 1) {
    // Jan or Feb: show Jan, Feb, Mar (months 0, 1, 2)
    startMonth = 0;
    endMonth = 2;
  } else if (currentMonth === 10 || currentMonth === 11) {
    // Nov or Dec: show Oct, Nov, Dec (months 9, 10, 11)
    startMonth = 9;
    endMonth = 11;
  } else {
    // Other months: show current + next 2 months
    startMonth = currentMonth;
    endMonth = currentMonth + 2;
  }
  
  // Start from first day of start month
  const startDate = new Date(targetYear, startMonth, 1);
  
  // End at last day of end month
  const endDate = new Date(targetYear, endMonth + 1, 0);
  
  // Adjust to start from Sunday
  const dayOfWeek = startDate.getDay();
  startDate.setDate(startDate.getDate() - dayOfWeek);
  
  let currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    const week = [];
    for (let d = 0; d < 7; d++) {
      const date = new Date(currentDate);
      week.push({
        date: new Date(date),
        dateString: getDateString(date),
        isToday: getDateString(date) === getDateString(today),
        isFuture: date > today,
        isIn2026: date.getFullYear() === 2026,
      });
      currentDate.setDate(currentDate.getDate() + 1);
    }
    weeks.push(week);
  }
  
  return weeks;
};

const loadData = async () => {
  try {
    const homeDir = await getHomeDir();
    const dataFile = `${homeDir}/.habit-tracker-data.json`;
    const cmd = `cat "${dataFile}" 2>/dev/null || echo '{}'`;
    const output = await run(cmd);
    return JSON.parse(output);
  } catch (e) {
    return {};
  }
};

const saveData = async (data) => {
  const homeDir = await getHomeDir();
  const dataFile = `${homeDir}/.habit-tracker-data.json`;
  const json = JSON.stringify(data, null, 2);
  const cmd = `cat > "${dataFile}" <<'EOF'\n${json}\nEOF`;
  await run(cmd);
};

// === Main Component ===
function HabitTrackerInner() {
  const [habitData, setHabitData] = React.useState({});
  const [selectedHabit, setSelectedHabit] = React.useState(HABITS[0].id);
  const [loading, setLoading] = React.useState(true);
  const [hoveredCell, setHoveredCell] = React.useState(null);
  const [stats, setStats] = React.useState({ total: 0, completed: 0, streak: 0 });

  const weeks = React.useMemo(() => getWeeksData3Months(), []);

  // Load data on mount
  React.useEffect(() => {
    const load = async () => {
      const data = await loadData();
      setHabitData(data);
      setLoading(false);
    };
    load();
  }, []);

  // Calculate stats
  React.useEffect(() => {
    if (!habitData[selectedHabit]) {
      setStats({ total: 0, completed: 0, streak: 0 });
      return;
    }

    const data = habitData[selectedHabit];
    const completed = Object.values(data).filter(Boolean).length;
    const total = Object.keys(data).length;

    // Calculate current streak
    let streak = 0;
    const today = new Date();
    for (let i = 0; i < 365; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateStr = getDateString(date);
      if (data[dateStr]) {
        streak++;
      } else {
        break;
      }
    }

    setStats({ total, completed, streak });
  }, [habitData, selectedHabit]);

  const openWebInterface = async () => {
    const cmd = `open http://127.0.0.1:${WEB_INTERFACE_PORT}`;
    await run(cmd);
  };

  const getIntensity = (dateString) => {
    if (!habitData[selectedHabit] || !habitData[selectedHabit][dateString]) {
      return 0;
    }
    return 1;
  };

  const getColor = (intensity, habitId) => {
    if (intensity === 0) return "rgba(55, 65, 81, 0.5)";
    const habit = HABITS.find(h => h.id === habitId);
    return habit?.color || "#10b981";
  };

  const monthLabels = React.useMemo(() => {
    const labels = [];
    let lastMonth = -1;
    
    weeks.forEach((week, weekIndex) => {
      const firstDay = week[0].date;
      const month = firstDay.getMonth();
      
      if (month !== lastMonth) {
        labels.push({
          weekIndex,
          label: firstDay.toLocaleDateString('en-US', { month: 'short' })
        });
        lastMonth = month;
      }
    });
    
    return labels;
  }, [weeks]);

  if (loading) {
    return <div style={{ padding: 40, textAlign: 'center' }}>Loading...</div>;
  }

  return (
    <>
      <style>{`
        .habit-header {
          padding: 12px 16px;
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
          border-bottom: 1px solid rgba(75, 85, 99, 0.3);
        }
        
        .habit-title {
          font-size: 14px;
          font-weight: 600;
          background: linear-gradient(135deg, #60a5fa, #a78bfa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 10px;
        }
        
        .habit-selector {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        
        .habit-btn {
          padding: 6px 12px;
          border-radius: 6px;
          border: 1px solid rgba(75, 85, 99, 0.3);
          background: rgba(31, 41, 55, 0.5);
          color: #d1d5db;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 11px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 5px;
        }
        
        .habit-btn:hover {
          background: rgba(55, 65, 81, 0.8);
          border-color: rgba(107, 114, 128, 0.5);
          transform: translateY(-1px);
        }
        
        .habit-btn.active {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2));
          border-color: rgba(139, 92, 246, 0.5);
          color: #f9fafb;
        }
        
        .habit-color-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
        }
        
        .heatmap-container {
          padding: 16px;
          overflow-x: auto;
        }
        
        .month-labels {
          display: flex;
          margin-bottom: 6px;
          margin-left: 28px;
          position: relative;
          height: 14px;
        }
        
        .month-label {
          position: absolute;
          font-size: 9px;
          color: #9ca3af;
          font-weight: 500;
        }
        
        .heatmap-grid {
          display: flex;
          gap: 3px;
        }
        
        .day-labels {
          display: flex;
          flex-direction: column;
          gap: 3px;
          margin-right: 8px;
          padding-top: 0px;
        }
        
        .day-label {
          height: 10px;
          font-size: 9px;
          color: #9ca3af;
          display: flex;
          align-items: center;
          line-height: 10px;
        }
        
        .week-column {
          display: flex;
          flex-direction: column;
          gap: 3px;
        }
        
        .day-cell {
          width: 10px;
          height: 10px;
          border-radius: 2px;
          cursor: default;
          transition: all 0.15s ease;
          border: 1px solid transparent;
        }
        
        .day-cell:hover {
          transform: scale(1.2);
          border-color: rgba(255, 255, 255, 0.2);
          z-index: 10;
          position: relative;
        }
        
        .day-cell.today {
          border: 1px solid rgba(255, 255, 255, 0.5);
        }
        
        .day-cell.future {
          opacity: 0.3;
          cursor: not-allowed;
        }
        
        .tooltip {
          position: fixed;
          background: rgba(17, 24, 39, 0.95);
          border: 1px solid rgba(75, 85, 99, 0.5);
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 11px;
          pointer-events: none;
          z-index: 1001;
          backdrop-filter: blur(10px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .tooltip-date {
          font-weight: 600;
          color: #f9fafb;
          margin-bottom: 4px;
        }
        
        .tooltip-status {
          color: #9ca3af;
        }
        
        .edit-btn {
          margin-top: 12px;
          width: 100%;
          padding: 8px;
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          border: 1px solid rgba(59, 130, 246, 0.3);
          color: #ffffff;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .edit-btn:hover {
          background: linear-gradient(135deg, #2563eb, #1d4ed8);
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
        }
      `}</style>

      <div className="habit-header">
        <div className="habit-title">🔥 Habit Tracker 2026</div>
        <div className="habit-selector">
          {HABITS.map(habit => (
            <button
              key={habit.id}
              className={`habit-btn ${selectedHabit === habit.id ? 'active' : ''}`}
              onClick={() => setSelectedHabit(habit.id)}
            >
              <div className="habit-color-dot" style={{ backgroundColor: habit.color }} />
              {habit.name}
            </button>
          ))}
        </div>
      </div>

      <div className="heatmap-container">
        <div className="month-labels">
          {monthLabels.map(({ weekIndex, label }) => (
            <div
              key={weekIndex}
              className="month-label"
              style={{ left: `${weekIndex * 13}px` }}
            >
              {label}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex' }}>
          <div className="day-labels">
            <div className="day-label"></div>
            <div className="day-label">Mon</div>
            <div className="day-label"></div>
            <div className="day-label">Wed</div>
            <div className="day-label"></div>
            <div className="day-label">Fri</div>
            <div className="day-label"></div>
          </div>

          <div className="heatmap-grid">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="week-column">
                {week.map((day, dayIndex) => {
                  const intensity = getIntensity(day.dateString);
                  const color = getColor(intensity, selectedHabit);
                  
                  return (
                    <div
                      key={dayIndex}
                      className={`day-cell ${day.isToday ? 'today' : ''} ${day.isFuture ? 'future' : ''}`}
                      style={{ backgroundColor: color }}
                      onClick={undefined}
                      onMouseEnter={(e) => {
                        if (!day.isFuture) {
                          setHoveredCell({
                            date: day.date.toLocaleDateString('en-US', { 
                              weekday: 'short', 
                              year: 'numeric', 
                              month: 'short', 
                              day: 'numeric' 
                            }),
                            completed: intensity > 0,
                            x: e.clientX,
                            y: e.clientY,
                          });
                        }
                      }}
                      onMouseLeave={() => setHoveredCell(null)}
                    />
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        <button className="edit-btn" onClick={openWebInterface}>
          ✏️ Edit Habits (Open Web Interface)
        </button>
      </div>

      {hoveredCell && (
        <div
          className="tooltip"
          style={{
            left: hoveredCell.x + 10,
            top: hoveredCell.y + 10,
          }}
        >
          <div className="tooltip-date">{hoveredCell.date}</div>
          <div className="tooltip-status">
            {hoveredCell.completed ? '✓ Completed' : '○ Not completed'}
          </div>
        </div>
      )}
    </>
  );
}

export const render = () => <HabitTrackerInner />;
