const express = require('express');
const cors = require('cors');
const app = express();

app.use(express.json());
// CRITICAL: Enable CORS for the lab diagnostic
app.use(cors());

let tasks_db = [];

app.post('/tasks', (req, res) => {
    const task = {
        title: req.body.title,
        status: req.body.status
    };
    tasks_db.push(task);
    res.status(201).json({ message: "Task saved" });
});

app.get('/tasks', (req, res) => {
    res.json(tasks_db);
});

app.listen(8001, () => {
    console.log('Server running on http://localhost:8001');
});