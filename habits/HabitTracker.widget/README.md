# 🔥 GitHub-Style Habit Tracker for Übersicht

A beautiful, interactive habit tracker widget for macOS that displays your habits in a GitHub contribution graph style heat map.

![Habit Tracker Preview](screenshot.png)

## ✨ Features

- **📊 GitHub-Style Heat Map** - Visual representation of your habit completion over 20 weeks (~5 months)
- **🎯 Multiple Habits** - Track up to 5 different habits simultaneously
- **📈 Real-time Statistics** - Current streak, total days, and completion rate
- **💾 Local Data Storage** - All data stored locally in JSON format
- **🎨 Beautiful UI** - Modern glassmorphic design with smooth animations
- **⚡ Interactive** - Click any day to toggle completion status
- **🖱️ Hover Tooltips** - See detailed information on hover

## 🚀 Quick Start

### Prerequisites

- macOS
- [Übersicht](https://tracesof.net/uebersicht/) installed

### Installation

1. **Install Übersicht** (if not already installed):
   ```bash
   brew install --cask ubersicht
   ```

2. **Copy the widget**:
   ```bash
   cp -r HabitTracker.widget ~/Library/Application\ Support/Übersicht/widgets/
   ```

3. **Refresh Übersicht**:
   - Open Übersicht
   - The widget should appear automatically
   - If not, click the Übersicht menu bar icon → Refresh All Widgets

## 📖 Usage

### Basic Operations

- **Switch Habits**: Click on any habit button at the top to switch between different habits
- **Mark Completion**: Click on any day cell in the heat map to toggle completion
- **View Details**: Hover over any day to see the date and completion status
- **Track Progress**: View your current streak, total completed days, and completion rate in the stats bar

### Customizing Habits

Edit the `HABITS` array in `index.jsx`:

```javascript
const HABITS = [
  { id: "exercise", name: "Exercise", color: "#10b981" },
  { id: "reading", name: "Reading", color: "#3b82f6" },
  { id: "meditation", name: "Meditation", color: "#8b5cf6" },
  { id: "coding", name: "Coding", color: "#f59e0b" },
  { id: "writing", name: "Writing", color: "#ec4899" },
];
```

### Customizing Position

Modify the `className` export in `index.jsx`:

```javascript
export const className = `
  position: fixed;
  right: 20px;        // Change horizontal position
  top: 50%;           // Change vertical position
  transform: translateY(-50%);
  // ... rest of styles
`;
```

### Customizing Weeks Displayed

Change the `WEEKS_TO_SHOW` constant:

```javascript
const WEEKS_TO_SHOW = 20; // Show ~5 months (adjust as needed)
```

## 💾 Data Storage

Data is stored in `~/.habit-tracker-data.json` in the following format:

```json
{
  "exercise": {
    "2025-01-01": true,
    "2025-01-02": false,
    "2025-01-03": true
  },
  "reading": {
    "2025-01-01": true,
    "2025-01-02": true
  }
}
```

### Backup Your Data

```bash
cp ~/.habit-tracker-data.json ~/.habit-tracker-data.backup.json
```

### Reset Data

```bash
rm ~/.habit-tracker-data.json
```

## 🎨 Customization

### Color Schemes

The widget uses a dark theme by default. You can customize colors in the styles:

```javascript
// Main container background
background: linear-gradient(145deg, rgba(17, 24, 39, 0.95), rgba(31, 41, 55, 0.98));

// Habit colors (in HABITS array)
color: "#10b981"  // Emerald green
color: "#3b82f6"  // Blue
color: "#8b5cf6"  // Purple
color: "#f59e0b"  // Amber
color: "#ec4899"  // Pink
```

### Cell Size

Adjust the heat map cell size:

```css
.day-cell {
  width: 12px;   // Change width
  height: 12px;  // Change height
  border-radius: 2px;
}
```

## 🔧 Advanced Features

### Export Data

```bash
cat ~/.habit-tracker-data.json | jq '.'
```

### Import Data

```bash
cat your-data.json > ~/.habit-tracker-data.json
```

### Statistics Calculation

The widget automatically calculates:
- **Current Streak**: Consecutive days from today backwards
- **Total Days**: All days marked as completed
- **Completion Rate**: Percentage of completed days out of tracked days

## 🐛 Troubleshooting

### Widget Not Showing

1. Check Übersicht is running
2. Verify widget is in the correct directory
3. Check Übersicht preferences → Enable widgets
4. Refresh all widgets

### Data Not Saving

1. Check file permissions: `ls -la ~/.habit-tracker-data.json`
2. Ensure you have write permissions to home directory
3. Check Übersicht console for errors

### Performance Issues

1. Reduce `WEEKS_TO_SHOW` to show fewer weeks
2. Close other resource-intensive applications
3. Restart Übersicht

## 📊 Statistics Explained

- **Current Streak**: Number of consecutive days (from today backwards) where the habit was completed
- **Total Days**: Total number of days where the habit was marked as complete
- **Completion Rate**: Percentage calculated as (completed days / total tracked days) × 100

## 🎯 Tips for Success

1. **Start Small**: Begin with 1-2 habits and gradually add more
2. **Be Consistent**: Check in daily to maintain your streak
3. **Review Weekly**: Look at your heat map to identify patterns
4. **Adjust Goals**: Modify habits based on what works for you
5. **Backup Regularly**: Keep backups of your data for long-term tracking

## 🔄 Updates

To update the widget:

1. Replace the `index.jsx` file with the new version
2. Refresh Übersicht widgets
3. Your data will be preserved (stored separately)

## 📝 License

MIT License - Feel free to modify and distribute

## 🙏 Credits

Inspired by:
- GitHub contribution graph
- Übersicht widget framework
- Your existing Obs-Plan-widget

---

**Version**: 1.0.0  
**Last Updated**: January 2025
