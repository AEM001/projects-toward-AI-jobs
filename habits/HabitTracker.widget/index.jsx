import { React, run } from "uebersicht";

// === Configuration ===
const HABITS = [
  { id: "exercise", name: "Exercise", color: "#10b981" },
  { id: "reading", name: "Reading", color: "#3b82f6" },
  { id: "meditation", name: "Meditation", color: "#8b5cf6" },
  { id: "coding", name: "Coding", color: "#f59e0b" },
  { id: "writing", name: "Writing", color: "#ec4899" },
];

const DATA_FILE = `${process.env.HOME}/.habit-tracker-data.json`;
const WEEKS_TO_SHOW = 20; // Show ~5 months of data

// === Styles ===
export const className = `
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 800px;
  background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(31, 41, 55, 0.98));
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(75, 85, 99, 0.3);
  color: #f9fafb;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  font-size: 13px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 8px 16px rgba(0, 0, 0, 0.2),
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

const getWeeksData = (weeksCount) => {
  const weeks = [];
  const today = new Date();
  const startDate = new Date(today);
  startDate.setDate(today.getDate() - (weeksCount * 7) + 1);
  
  // Adjust to start from Sunday
  const dayOfWeek = startDate.getDay();
  startDate.setDate(startDate.getDate() - dayOfWeek);
  
  for (let w = 0; w < weeksCount; w++) {
    const week = [];
    for (let d = 0; d < 7; d++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + (w * 7) + d);
      week.push({
        date: new Date(date),
        dateString: getDateString(date),
        isToday: getDateString(date) === getDateString(today),
        isFuture: date > today,
      });
    }
    weeks.push(week);
  }
  
  return weeks;
};

const loadData = async () => {
  try {
    const cmd = `cat "${DATA_FILE}" 2>/dev/null || echo '{}'`;
    const output = await run(cmd);
    return JSON.parse(output);
  } catch (e) {
    return {};
  }
};

const saveData = async (data) => {
  const json = JSON.stringify(data, null, 2);
  const cmd = `cat > "${DATA_FILE}" <<'EOF'\n${json}\nEOF`;
  await run(cmd);
};

// === Main Component ===
function HabitTrackerInner() {
  const [habitData, setHabitData] = React.useState({});
  const [selectedHabit, setSelectedHabit] = React.useState(HABITS[0].id);
  const [loading, setLoading] = React.useState(true);
  const [hoveredCell, setHoveredCell] = React.useState(null);
  const [stats, setStats] = React.useState({ total: 0, completed: 0, streak: 0 });

  const weeks = React.useMemo(() => getWeeksData(WEEKS_TO_SHOW), []);

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

  const toggleHabit = async (dateString) => {
    const newData = { ...habitData };
    if (!newData[selectedHabit]) {
      newData[selectedHabit] = {};
    }
    newData[selectedHabit][dateString] = !newData[selectedHabit][dateString];
    
    setHabitData(newData);
    await saveData(newData);
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
      
      if (month !== lastMonth && weekIndex % 4 === 0) {
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
          padding: 20px 24px;
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
          border-bottom: 1px solid rgba(75, 85, 99, 0.3);
        }
        
        .habit-title {
          font-size: 18px;
          font-weight: 600;
          background: linear-gradient(135deg, #60a5fa, #a78bfa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 16px;
        }
        
        .habit-selector {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        
        .habit-btn {
          padding: 8px 16px;
          border-radius: 8px;
          border: 1px solid rgba(75, 85, 99, 0.3);
          background: rgba(31, 41, 55, 0.5);
          color: #d1d5db;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 12px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 6px;
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
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        .stats-bar {
          display: flex;
          gap: 24px;
          padding: 16px 24px;
          background: rgba(17, 24, 39, 0.5);
          border-bottom: 1px solid rgba(75, 85, 99, 0.3);
        }
        
        .stat-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        
        .stat-label {
          font-size: 11px;
          color: #9ca3af;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .stat-value {
          font-size: 20px;
          font-weight: 600;
          background: linear-gradient(135deg, #60a5fa, #a78bfa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .heatmap-container {
          padding: 24px;
          overflow-x: auto;
        }
        
        .month-labels {
          display: flex;
          margin-bottom: 8px;
          margin-left: 32px;
          position: relative;
          height: 16px;
        }
        
        .month-label {
          position: absolute;
          font-size: 10px;
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
          height: 12px;
          font-size: 10px;
          color: #9ca3af;
          display: flex;
          align-items: center;
          line-height: 12px;
        }
        
        .week-column {
          display: flex;
          flex-direction: column;
          gap: 3px;
        }
        
        .day-cell {
          width: 12px;
          height: 12px;
          border-radius: 2px;
          cursor: pointer;
          transition: all 0.15s ease;
          border: 1px solid transparent;
        }
        
        .day-cell:hover {
          transform: scale(1.3);
          border-color: rgba(255, 255, 255, 0.3);
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
        
        .legend {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 16px;
          font-size: 11px;
          color: #9ca3af;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        
        .legend-box {
          width: 12px;
          height: 12px;
          border-radius: 2px;
        }
      `}</style>

      <div className="habit-header">
        <div className="habit-title">🔥 Habit Tracker</div>
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

      <div className="stats-bar">
        <div className="stat-item">
          <div className="stat-label">Current Streak</div>
          <div className="stat-value">{stats.streak} days</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Total Days</div>
          <div className="stat-value">{stats.completed}</div>
        </div>
        <div className="stat-item">
          <div className="stat-label">Completion Rate</div>
          <div className="stat-value">
            {stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0}%
          </div>
        </div>
      </div>

      <div className="heatmap-container">
        <div className="month-labels">
          {monthLabels.map(({ weekIndex, label }) => (
            <div
              key={weekIndex}
              className="month-label"
              style={{ left: `${weekIndex * 15}px` }}
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
                      onClick={() => !day.isFuture && toggleHabit(day.dateString)}
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

        <div className="legend">
          <span>Less</span>
          <div className="legend-item">
            <div className="legend-box" style={{ backgroundColor: 'rgba(55, 65, 81, 0.5)' }} />
          </div>
          <div className="legend-item">
            <div className="legend-box" style={{ backgroundColor: getColor(1, selectedHabit) }} />
          </div>
          <span>More</span>
        </div>
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
