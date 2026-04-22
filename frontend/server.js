const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

const API_URL = process.env.API_URL || "http://localhost:8000";

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// Health check (REQUIRED for deploy)
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Submit job (aligned with pipeline)
app.post('/jobs', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`, {}, { timeout: 5000 });
    res.json(response.data);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: err.message });
  }
});

// Check status
app.get('/jobs/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`, { timeout: 5000 });
    res.json(response.data);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => {
  console.log('Frontend running on port 3000');
});