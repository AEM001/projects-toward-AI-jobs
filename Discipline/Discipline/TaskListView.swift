import SwiftUI
import SwiftData
import WidgetKit

struct TaskListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \DisciplineTask.createdAt, order: .reverse) private var allTasks: [DisciplineTask]
    
    @State private var newTaskTitle: String = ""
    @State private var selectedDate: Date = Date()
    @State private var editingTask: DisciplineTask? = nil
    @State private var showEditSheet: Bool = false
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
                
                // Refined Calendar - Enlarged
                VStack(spacing: 0) {
                    DatePicker(
                        "",
                        selection: $selectedDate,
                        displayedComponents: .date
                    )
                    .datePickerStyle(.graphical)
                    .padding(.horizontal, 8)
                    .padding(.top, 8)
                    .padding(.bottom, 8)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(Color(nsColor: .controlBackgroundColor))
                            .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
                    )
                    .padding(.horizontal, 8)
                    .padding(.vertical, 8)
                }
                .frame(maxHeight: .infinity)
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
        .sheet(isPresented: $showEditSheet) {
            if let task = editingTask {
                TaskEditSheet(task: task, onSave: {
                    showEditSheet = false
                    editingTask = nil
                    WidgetCenter.shared.reloadAllTimelines()
                })
            }
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
                                showEditSheet = true
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
        if url.absoluteString == "discipline://add" {
            selectedView = .today
            selectedDate = Date()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                isInputFocused = true
            }
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

#Preview {
    TaskListView()
        .modelContainer(for: DisciplineTask.self, inMemory: true)
}
