# 🚀 Quick Start Guide

Get your GitHub-style habit tracker running in 3 minutes!

## Option 1: Automated Installation (Recommended)

```bash
cd /Users/Mac/code/project/habits/HabitTracker.widget
./install.sh
```

The script will:
- ✅ Check for Übersicht
- ✅ Copy widget files to the correct location
- ✅ Optionally install the backend server
- ✅ Set up auto-start (if you choose)

## Option 2: Manual Installation

### Step 1: Install Übersicht

```bash
brew install --cask ubersicht
```

### Step 2: Copy Widget

```bash
cp -r /Users/Mac/code/project/habits/HabitTracker.widget \
  ~/Library/Application\ Support/Übersicht/widgets/
```

### Step 3: Refresh Übersicht

- Open Übersicht
- Click menu bar icon → Refresh All Widgets

## 🎯 First Use

1. **Widget appears** on the right side of your screen
2. **Click habit buttons** at the top to switch between habits
3. **Click any day cell** to mark it as complete/incomplete
4. **Hover over cells** to see date and status
5. **Watch your streak grow!** 🔥

## ⚙️ Customization

### Change Habits

Edit `index.jsx` line 6-12:

```javascript
const HABITS = [
  { id: "exercise", name: "Exercise", color: "#10b981" },
  { id: "reading", name: "Reading", color: "#3b82f6" },
  // Add your own habits here
];
```

### Change Position

Edit `index.jsx` line 11-13:

```javascript
position: fixed;
right: 20px;    // Distance from right edge
top: 50%;       // Vertical position (50% = center)
```

### Change Size

Edit `index.jsx` line 14:

```javascript
width: 800px;   // Make wider or narrower
```

## 📊 Understanding the Heat Map

- **Dark gray squares** = No activity
- **Colored squares** = Activity completed
- **White border** = Today
- **Faded squares** = Future dates (not clickable)

## 🔥 Streak Calculation

Your streak counts **consecutive days from today backwards** where you completed the habit.

Example:
- Today ✓
- Yesterday ✓
- 2 days ago ✓
- 3 days ago ✗ ← Streak breaks here
- **Current Streak: 3 days**

## 💾 Data Location

All your habit data is stored in:
```
~/.habit-tracker-data.json
```

**Backup regularly!**
```bash
cp ~/.habit-tracker-data.json ~/habit-backup.json
```

## 🐛 Troubleshooting

### Widget not showing?
1. Check Übersicht is running
2. Refresh widgets (menu bar → Refresh All Widgets)
3. Check widget is in correct folder

### Clicks not working?
1. Make sure you're clicking on past/present days (not future)
2. Check Übersicht has accessibility permissions
3. Restart Übersicht

### Data not saving?
1. Check file permissions: `ls -la ~/.habit-tracker-data.json`
2. Try manually creating the file: `echo '{}' > ~/.habit-tracker-data.json`
3. Check Übersicht console for errors

## 🎨 Color Meanings

Each habit has its own color:
- 🟢 **Green** (#10b981) - Exercise
- 🔵 **Blue** (#3b82f6) - Reading  
- 🟣 **Purple** (#8b5cf6) - Meditation
- 🟠 **Orange** (#f59e0b) - Coding
- 🌸 **Pink** (#ec4899) - Writing

## 📱 Pro Tips

1. **Start small** - Begin with 1-2 habits
2. **Be consistent** - Check in daily
3. **Review weekly** - Look for patterns in your heat map
4. **Celebrate streaks** - Reward yourself for milestones
5. **Don't break the chain** - Jerry Seinfeld's method works!

## 🔄 Updates

To update the widget:
1. Replace `index.jsx` with new version
2. Refresh Übersicht
3. Your data is preserved (stored separately)

## 📚 More Info

- Full documentation: `README.md`
- Backend API: `BACKEND.md` (optional)
- GitHub heat map style inspired by GitHub contributions graph

---

**Need help?** Check the full README or open an issue.

**Enjoying the tracker?** Share it with friends! 🎉
