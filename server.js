
const express = require('express');
const multer = require('multer');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

app.use(express.json());
app.use('/static', express.static('static'));

const UPLOAD_DIRECTORY = './static/uploads';
let currentUrl = "https://faizu.serveo.net/chat";

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    fs.mkdirSync(UPLOAD_DIRECTORY, { recursive: true });
    cb(null, UPLOAD_DIRECTORY);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  },
});
const upload = multer({ storage });

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.post('/api', async (req, res) => {
  const { message } = req.body;
  if (!currentUrl) {
    return res.status(404).json({ error: 'No URL set yet' });
  }
  try {
    const response = await axios.post(`${currentUrl}/chat`, { message });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  res.json({ file_path: `/static/uploads/${req.file.filename}` });
});

app.post('/update', (req, res) => {
  const { url } = req.body;
  currentUrl = url;
  res.json({ status: 'updated', new_url: currentUrl });
});

app.get('/go', (req, res) => {
  if (currentUrl) {
    res.redirect(currentUrl);
  } else {
    res.status(404).json({ error: 'No URL set yet' });
  }
});

app.get('/latest', (req, res) => {
  if (currentUrl) {
    res.json({ url: currentUrl });
  } else {
    res.status(404).json({ error: 'No URL set yet' });
  }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
