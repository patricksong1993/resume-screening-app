const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware for parsing JSON and handling file uploads
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Serve the main HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// // Mock endpoint for file upload
// app.post('/api/upload-files', (req, res) => {
//   // Simulate processing delay
//   setTimeout(() => {
//     res.json({
//       message: "Files uploaded successfully!",
//       status: "success",
//       filesProcessed: req.body.files ? req.body.files.length : 0,
//       timestamp: new Date().toISOString()
//     });
//   }, 1000);
// });

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
