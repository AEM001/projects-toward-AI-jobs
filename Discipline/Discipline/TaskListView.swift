import SwiftUI
import SwiftData
import WidgetKit
import AppKit

struct TaskListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \DisciplineTask.createdAt, order: .reverse) private var allTasks: [DisciplineTask]
    
    @State private var newTaskTitle: String = ""
    @State private var selectedDate: Date = Date()
    @State private var editingTask: DisciplineTask? = nil
    @State private var selectedView: SidebarItem = .today
    @FocusState private var isInputFocused: Bool
    
    enum SidebarItem: Hashable {
        case today
        case history
        case upcoming
    }
    
    var tasksForSelectedDate: [DisciplineTask] {
        return allTasks.filter { task in
            Calendar.current.isDate(task.createdAt, inSameDayAs: selectedDate)
        }.sorted { t1, t2 in
            if t1.isCompleted != t2.isCompleted {
                return !t1.isCompleted
            }
            return t1.createdAt < t2.createdAt
        }
    }
    
    var isToday: Bool {
        Calendar.current.isDateInToday(selectedDate)
    }
    
    var body: some View {
        NavigationSplitView {
            VStack(spacing: 0) {
                List(selection: $selectedView) {
                    Section {
                        NavigationLink(value: SidebarItem.today) {
                            Label("Today", systemImage: "sun.max.fill")
                        }
                        .foregroundStyle(.orange)
                        
                        NavigationLink(value: SidebarItem.upcoming) {
                            Label("Upcoming", systemImage: "calendar")
                        }
                        .foregroundStyle(.blue)
                        
                        NavigationLink(value: SidebarItem.history) {
                            Label("History", systemImage: "clock.arrow.circlepath")
                        }
                        .foregroundStyle(.secondary)
                    }
                }
                .listStyle(.sidebar)
                
                Divider()
                
                // Calendar
                CalendarSidebarView(selectedDate: $selectedDate)
            }
            .background(Color(nsColor: .windowBackgroundColor))
            .navigationSplitViewColumnWidth(min: 220, ideal: 260, max: 300)
        } detail: {
            switch selectedView {
            case .today:
                taskDetailView
            case .upcoming:
                UpcomingView(allTasks: allTasks, onSelectDate: { date in
                    selectedDate = date
                    selectedView = .today
                })
            case .history:
                HistoryView()
            }
        }
        .onOpenURL { url in
            handleDeepLink(url)
        }
        .onReceive(DistributedNotificationCenter.default().publisher(for: Notification.Name("com.albert.Discipline.addTask"))) { _ in
            NSApp.activate()
            if let window = NSApp.windows.first(where: { $0.title == "Discipline" || (!$0.title.isEmpty && $0.isVisible) }) {
                window.makeKeyAndOrderFront(nil)
            }
            selectedView = .today
            selectedDate = Date()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                isInputFocused = true
            }
        }
        .sheet(item: $editingTask) { task in
            TaskEditSheet(task: task, onSave: {
                editingTask = nil
                WidgetCenter.shared.reloadAllTimelines()
            })
        }
    }
    
    var taskDetailView: some View {
        VStack(spacing: 0) {
            // Header
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(isToday ? "Today" : formatDate(selectedDate))
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundStyle(Color(nsColor: .labelColor))
                    
                    Text(formatShortDate(selectedDate))
                        .font(.subheadline)
                        .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                }
                
                Spacer()
                
                if !isToday {
                    Button("Back to Today") {
                        withAnimation {
                            selectedDate = Date()
                        }
                    }
                    .buttonStyle(.link)
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 24)
            .padding(.bottom, 16)
            
            // Task Input
            HStack(spacing: 12) {
                Image(systemName: "plus.circle.fill")
                    .font(.title2)
                    .foregroundStyle(.blue)
                
                TextField("Add a new task...", text: $newTaskTitle)
                    .textFieldStyle(.plain)
                    .font(.body)
                    .foregroundStyle(Color(nsColor: .labelColor))
                    .focused($isInputFocused)
                    .onSubmit(addTask)
            }
            .padding(14)
            .background(Color(nsColor: .controlBackgroundColor))
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(nsColor: .separatorColor), lineWidth: 1)
            )
            .padding(.horizontal, 24)
            .padding(.bottom, 16)
            
            // Task List
            if tasksForSelectedDate.isEmpty {
                VStack(spacing: 16) {
                    Spacer()
                    Image(systemName: "checkmark.circle")
                        .font(.system(size: 48))
                        .foregroundStyle(Color(nsColor: .tertiaryLabelColor))
                    Text("No tasks")
                        .font(.title3)
                        .fontWeight(.medium)
                        .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                    Text(isToday ? "What would you like to accomplish?" : "No tasks for this day")
                        .font(.body)
                        .foregroundStyle(Color(nsColor: .tertiaryLabelColor))
                    Spacer()
                }
                .frame(maxWidth: .infinity)
            } else {
                List {
                    ForEach(tasksForSelectedDate) { task in
                        TaskRow(
                            task: task,
                            onDelete: { deleteTask(task) },
                            onEdit: {
                                editingTask = task
                            }
                        )
                        .listRowSeparator(.hidden)
                        .listRowInsets(EdgeInsets(top: 4, leading: 24, bottom: 4, trailing: 24))
                    }
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
            }
        }
        .background(Color(nsColor: .textBackgroundColor))
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE, M-d"
        return formatter.string(from: date)
    }
    
    private func formatShortDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE, M-d"
        return formatter.string(from: date)
    }
    
    private func addTask() {
        guard !newTaskTitle.isEmpty else { return }
        withAnimation {
            let newTask = DisciplineTask(title: newTaskTitle)
            let calendar = Calendar.current
            let components = calendar.dateComponents([.year, .month, .day], from: selectedDate)
            if let taskDate = calendar.date(from: components) {
                newTask.createdAt = taskDate
            }
            modelContext.insert(newTask)
            newTaskTitle = ""
            WidgetCenter.shared.reloadAllTimelines()
        }
    }
    
    private func deleteTask(_ task: DisciplineTask) {
        withAnimation {
            modelContext.delete(task)
            WidgetCenter.shared.reloadAllTimelines()
        }
    }
    
    private func handleDeepLink(_ url: URL) {
        NSApp.activate()
        if let window = NSApp.windows.first(where: { $0.title == "Discipline" || (!$0.title.isEmpty && $0.isVisible) }) {
            window.makeKeyAndOrderFront(nil)
        } else if let window = NSApp.windows.first(where: { !$0.title.isEmpty }) {
            window.makeKeyAndOrderFront(nil)
        }
        
        if url.host == "add" {
            selectedView = .today
            selectedDate = Date()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                isInputFocused = true
            }
        } else if url.host == "open" {
            selectedView = .today
            selectedDate = Date()
        }
    }
}

// MARK: - Upcoming View
struct UpcomingView: View {
    let allTasks: [DisciplineTask]
    let onSelectDate: (Date) -> Void
    
    var upcomingTasks: [(date: Date, tasks: [DisciplineTask])] {
        let today = Calendar.current.startOfDay(for: Date())
        let futureTasks = allTasks.filter { task in
            Calendar.current.startOfDay(for: task.createdAt) > today
        }
        
        let grouped = Dictionary(grouping: futureTasks) { task in
            Calendar.current.startOfDay(for: task.createdAt)
        }
        
        return grouped.sorted { $0.key < $1.key }
            .map { (date: $0.key, tasks: $0.value.sorted { $0.createdAt < $1.createdAt }) }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Upcoming")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundStyle(Color(nsColor: .labelColor))
                Spacer()
            }
            .padding(.horizontal, 24)
            .padding(.top, 24)
            .padding(.bottom, 16)
            
            if upcomingTasks.isEmpty {
                VStack(spacing: 16) {
                    Spacer()
                    Image(systemName: "calendar.badge.clock")
                        .font(.system(size: 48))
                        .foregroundStyle(Color(nsColor: .tertiaryLabelColor))
                    Text("No upcoming tasks")
                        .font(.title3)
                        .fontWeight(.medium)
                        .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                    Text("Select a future date to add tasks")
                        .font(.body)
                        .foregroundStyle(Color(nsColor: .tertiaryLabelColor))
                    Spacer()
                }
                .frame(maxWidth: .infinity)
            } else {
                List {
                    ForEach(upcomingTasks, id: \.date) { group in
                        Section {
                            ForEach(group.tasks) { task in
                                HStack(spacing: 12) {
                                    Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                                        .foregroundStyle(task.isCompleted ? .green : Color(nsColor: .tertiaryLabelColor))
                                    Text(task.title)
                                        .strikethrough(task.isCompleted)
                                        .foregroundStyle(task.isCompleted ? Color(nsColor: .secondaryLabelColor) : Color(nsColor: .labelColor))
                                    Spacer()
                                }
                            }
                        } header: {
                            Button(action: { onSelectDate(group.date) }) {
                                HStack {
                                    Text(formatDate(group.date))
                                        .font(.headline)
                                        .foregroundStyle(Color(nsColor: .labelColor))
                                    Spacer()
                                    Text("\(group.tasks.count)")
                                        .font(.caption)
                                        .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 2)
                                        .background(Color(nsColor: .quaternaryLabelColor))
                                        .cornerRadius(8)
                                }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .listStyle(.inset)
                .scrollContentBackground(.hidden)
            }
        }
        .background(Color(nsColor: .textBackgroundColor))
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE, M-d"
        return formatter.string(from: date)
    }
}

struct TaskRow: View {
    @Bindable var task: DisciplineTask
    let onDelete: () -> Void
    let onEdit: () -> Void
    @State private var isHovered = false
    
    var body: some View {
        HStack(spacing: 12) {
            Button(action: {
                withAnimation(.snappy) {
                    task.isCompleted.toggle()
                    task.completedAt = task.isCompleted ? Date() : nil
                    WidgetCenter.shared.reloadAllTimelines()
                }
            }) {
                Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundStyle(task.isCompleted ? .green : Color(nsColor: .tertiaryLabelColor))
            }
            .buttonStyle(.plain)
            
            Text(task.title)
                .font(.body)
                .strikethrough(task.isCompleted)
                .foregroundStyle(task.isCompleted ? Color(nsColor: .secondaryLabelColor) : Color(nsColor: .labelColor))
            
            Spacer()
            
            if isHovered {
                HStack(spacing: 8) {
                    Button(action: onEdit) {
                        Image(systemName: "pencil")
                            .foregroundStyle(.blue)
                    }
                    .buttonStyle(.plain)
                    .help("Edit")
                    
                    Button(action: onDelete) {
                        Image(systemName: "trash")
                            .foregroundStyle(.red)
                    }
                    .buttonStyle(.plain)
                    .help("Delete")
                }
            }
        }
        .padding(.vertical, 10)
        .padding(.horizontal, 12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(isHovered ? Color(nsColor: .selectedContentBackgroundColor).opacity(0.3) : Color.clear)
        )
        .contentShape(Rectangle())
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.15)) {
                isHovered = hovering
            }
        }
    }
}

struct TaskEditSheet: View {
    @Bindable var task: DisciplineTask
    let onSave: () -> Void
    @Environment(\.dismiss) private var dismiss
    
    @State private var editedTitle: String = ""
    @State private var editedDate: Date = Date()
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Edit Task")
                .font(.headline)
                .foregroundStyle(Color(nsColor: .labelColor))
            
            VStack(alignment: .leading, spacing: 6) {
                Text("Title")
                    .font(.caption)
                    .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                TextField("Task title", text: $editedTitle)
                    .textFieldStyle(.roundedBorder)
            }
            
            VStack(alignment: .leading, spacing: 6) {
                Text("Date")
                    .font(.caption)
                    .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                DatePicker("", selection: $editedDate, displayedComponents: .date)
                    .labelsHidden()
            }
            
            HStack(spacing: 12) {
                Button("Cancel") { dismiss() }
                    .keyboardShortcut(.cancelAction)
                
                Button("Save") {
                    task.title = editedTitle
                    task.createdAt = editedDate
                    onSave()
                }
                .buttonStyle(.borderedProminent)
                .keyboardShortcut(.defaultAction)
                .disabled(editedTitle.isEmpty)
            }
        }
        .padding(24)
        .frame(width: 320)
        .onAppear {
            editedTitle = task.title
            editedDate = task.createdAt
        }
    }
}

// MARK: - Custom Calendar Sidebar
struct CalendarSidebarView: View {
    @Binding var selectedDate: Date
    @State private var displayedMonth: Date = Date()
    
    private let calendar = Calendar.current
    
    var body: some View {
        VStack(spacing: 8) {
            monthHeader
            weekdayHeader
            dayGrid
            todayButton
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color(nsColor: .controlBackgroundColor))
                .shadow(color: Color.black.opacity(0.06), radius: 3, x: 0, y: 1)
        )
        .padding(.horizontal, 10)
        .padding(.vertical, 10)
        .onChange(of: selectedDate) { _, newDate in
            if !calendar.isDate(newDate, equalTo: displayedMonth, toGranularity: .month) {
                withAnimation { displayedMonth = newDate }
            }
        }
    }
    
    // MARK: Month Header
    private var monthHeader: some View {
        HStack {
            Button(action: { changeMonth(-1) }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(Color(nsColor: .secondaryLabelColor))
            }
            .buttonStyle(.plain)
            
            Spacer()
            
            Text(monthTitle)
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(Color(nsColor: .labelColor))
            
            Spacer()
            
            Button(action: { changeMonth(1) }) {
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(Color(nsColor: .secondaryLabelColor))
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 4)
    }
    
    // MARK: Weekday Header
    private var weekdayHeader: some View {
        let days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        return LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 0), count: 7), spacing: 0) {
            ForEach(days, id: \.self) { day in
                Text(day)
                    .font(.system(size: 10, weight: .medium))
                    .foregroundStyle(Color(nsColor: .tertiaryLabelColor))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 4)
            }
        }
    }
    
    // MARK: Day Grid
    private var dayGrid: some View {
        let columns = Array(repeating: GridItem(.flexible(), spacing: 0), count: 7)
        return LazyVGrid(columns: columns, spacing: 2) {
            ForEach(Array(daysInMonth.enumerated()), id: \.offset) { _, date in
                CalendarDayCell(
                    date: date,
                    selectedDate: $selectedDate,
                    calendar: calendar
                )
            }
        }
    }
    
    // MARK: Today Button
    @ViewBuilder
    private var todayButton: some View {
        let showButton = !calendar.isDate(displayedMonth, equalTo: Date(), toGranularity: .month) || !calendar.isDateInToday(selectedDate)
        if showButton {
            Button(action: {
                withAnimation {
                    selectedDate = Date()
                    displayedMonth = Date()
                }
            }) {
                Text("Today")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(Color.accentColor)
            }
            .buttonStyle(.plain)
            .padding(.top, 2)
        }
    }
    
    // MARK: Helpers
    private var monthTitle: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMMM yyyy"
        return formatter.string(from: displayedMonth)
    }
    
    private var daysInMonth: [Date?] {
        let range = calendar.range(of: .day, in: .month, for: displayedMonth)!
        let firstDay = calendar.date(from: calendar.dateComponents([.year, .month], from: displayedMonth))!
        let firstWeekday = calendar.component(.weekday, from: firstDay)
        
        var days: [Date?] = Array(repeating: nil, count: firstWeekday - 1)
        for day in range {
            if let date = calendar.date(byAdding: .day, value: day - 1, to: firstDay) {
                days.append(date)
            }
        }
        while days.count % 7 != 0 {
            days.append(nil)
        }
        return days
    }
    
    private func changeMonth(_ offset: Int) {
        withAnimation {
            if let newMonth = calendar.date(byAdding: .month, value: offset, to: displayedMonth) {
                displayedMonth = newMonth
            }
        }
    }
}

// MARK: - Calendar Day Cell
struct CalendarDayCell: View {
    let date: Date?
    @Binding var selectedDate: Date
    let calendar: Calendar
    
    var body: some View {
        if let date = date {
            let dayNum = calendar.component(.day, from: date)
            let isSelected = calendar.isDate(date, inSameDayAs: selectedDate)
            let isToday = calendar.isDateInToday(date)
            
            Button(action: {
                withAnimation(.easeInOut(duration: 0.15)) {
                    selectedDate = date
                }
            }) {
                dayLabel(dayNum: dayNum, isSelected: isSelected, isToday: isToday)
            }
            .buttonStyle(.plain)
        } else {
            Text("")
                .frame(width: 26, height: 26)
        }
    }
    
    private func dayLabel(dayNum: Int, isSelected: Bool, isToday: Bool) -> some View {
        let textColor: Color = isSelected ? .white : (isToday ? .accentColor : Color(nsColor: .labelColor))
        let fontWeight: Font.Weight = isToday ? .bold : .regular
        let bgColor: Color = isSelected ? .accentColor : .clear
        let strokeColor: Color = (isToday && !isSelected) ? .accentColor : .clear
        
        return Text("\(dayNum)")
            .font(.system(size: 12, weight: fontWeight))
            .foregroundStyle(textColor)
            .frame(width: 26, height: 26)
            .background(Circle().fill(bgColor))
            .overlay(Circle().stroke(strokeColor, lineWidth: 1))
    }
}

#Preview {
    TaskListView()
        .modelContainer(for: DisciplineTask.self, inMemory: true)
}
