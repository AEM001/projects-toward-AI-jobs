// Main entry point - this runs when the page loads

import { alice, greet, scores, calculateAverage, friends } from './basics.js';
import { tasks, describeTask, getPendingTasks, Task } from './practice.js';

function render(): void {
    const output = document.getElementById('output');
    if (!output) return;

    // Example 1: Basic greeting
    const greeting = greet(alice);
    
    // Example 2: Working with arrays
    const avgScore = calculateAverage(scores);
    
    // Example 3: Working with tasks
    const pendingTasks = getPendingTasks(tasks);
    const taskDescriptions = tasks.map(t => describeTask(t));

    output.innerHTML = `
        <h2>👋 ${greeting}</h2>
        
        <section>
            <h3>📊 Scores</h3>
            <p>Scores: ${scores.join(', ')}</p>
            <p>Average: ${avgScore.toFixed(1)}</p>
        </section>
        
        <section>
            <h3>👥 Friends</h3>
            <ul>${friends.map(f => `<li>${f}</li>`).join('')}</ul>
        </section>
        
        <section>
            <h3>📝 All Tasks</h3>
            <ul>${taskDescriptions.map(t => `<li>${t}</li>`).join('')}</ul>
            
            <h4>Pending Tasks (${pendingTasks.length})</h4>
            <ul>${pendingTasks.map(t => `<li>${describeTask(t)}</li>`).join('')}</ul>
        </section>
    `;
}

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', render);
