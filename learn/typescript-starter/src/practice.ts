// TypeScript Practice - Try modifying these yourself!

import { Person, greet, calculateAverage } from './basics.js';

// PRACTICE 1: Create your own interface and function
interface Task {
    title: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high'; // Literal types
}

function describeTask(task: Task): string {
    const status = task.completed ? "✓ Done" : "○ Not done";
    return `${status}: ${task.title} (Priority: ${task.priority})`;
}

// Try creating a task
const myTask: Task = {
    title: "Learn TypeScript",
    completed: false,
    priority: "high"
};

// PRACTICE 2: Working with arrays
const tasks: Task[] = [
    { title: "Read TypeScript docs", completed: true, priority: "medium" },
    { title: "Write some code", completed: false, priority: "high" },
    { title: "Build a project", completed: false, priority: "low" }
];

function getPendingTasks(tasks: Task[]): Task[] {
    return tasks.filter(t => !t.completed);
}

// PRACTICE 3: Generic function (reusable with different types)
function findByProperty<T>(items: T[], property: keyof T, value: unknown): T | undefined {
    return items.find(item => item[property] === value);
}

// Example usage:
const foundTask = findByProperty(tasks, 'title', 'Write some code');

export { Task, describeTask, myTask, tasks, getPendingTasks, findByProperty, foundTask };
