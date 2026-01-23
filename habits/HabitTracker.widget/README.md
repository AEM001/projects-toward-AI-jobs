# 🔥 Habit Tracker 2026

GitHub风格的习惯追踪器，桌面widget + 网页编辑界面。

## 📦 安装

```bash
# Widget已安装在
~/Library/Application Support/Übersicht/widgets/HabitTracker.widget/

# 刷新Übersicht即可看到widget
```

## 🎯 使用

### 桌面Widget
- 显示最近3个月的习惯热力图（上月、本月、下月）
- 只读模式，点击"Edit Habits"按钮打开网页编辑

### 网页编辑界面
- 访问：`http://127.0.0.1:8788`
- 显示2026全年热力图
- 可编辑过去7天的打卡记录
- 超过7天的记录自动锁定

## 💾 数据位置

```
~/.habit-tracker-data.json
```

所有习惯数据存储在此文件，可手动备份。

## 🔧 后端服务

后端服务器自动启动（LaunchAgent），提供API和网页界面。

**重启服务：**
```bash
launchctl kickstart -k gui/$(id -u)/local.habittracker.server
```

**查看日志：**
```bash
tail -f /tmp/habittracker.out.log
tail -f /tmp/habittracker.err.log
```

## 📝 习惯列表

- **Coding** (蓝色)
- **No Scrolling** (绿色)  
- **Journal** (紫色)

修改习惯：编辑 `index.jsx` 和 `web/index.html` 中的 `HABITS` 数组。

---

**Version**: 2.0.0  
**Year**: 2026
