# AI Resume Screening App

A modern, responsive web application for AI-powered resume screening, similar to ResumeScreening.ai. Built with Node.js, Express, and vanilla JavaScript.

## Features

- **Modern Design**: Clean, professional interface with responsive design
- **File Upload**: Drag & drop or click to upload PDF, DOC, DOCX files
- **Interactive Demo**: Live job description input and resume upload simulation
- **AI Results Simulation**: Mock AI screening results with candidate scoring
- **Mobile Responsive**: Optimized for all device sizes
- **Smooth Animations**: Counter animations, scroll effects, and transitions

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm (comes with Node.js)

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd /Users/pat/Projects/resume-screening-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   
   Or for production:
   ```bash
   npm start
   ```

4. Open your browser and visit:
   ```
   http://localhost:3000
   ```

## Project Structure

```
resume-screening-app/
├── package.json          # Dependencies and scripts
├── server.js             # Express server setup
├── README.md            # This file
└── public/              # Static files
    ├── index.html       # Main HTML file
    ├── styles.css       # CSS styling
    └── script.js        # JavaScript functionality
```

## Features Implemented

### Frontend Features
- ✅ Responsive navigation with mobile menu
- ✅ Hero section with interactive demo
- ✅ File upload with drag & drop support
- ✅ Job description textarea with auto-resize
- ✅ Statistics section with animated counters
- ✅ Features grid with hover effects
- ✅ Benefits section with icons
- ✅ Customer testimonials
- ✅ FAQ section
- ✅ Professional footer

### Interactive Features
- ✅ File validation (PDF, DOC, DOCX only, 10MB max)
- ✅ Real-time upload progress display
- ✅ Dynamic "Screen Resumes" button state
- ✅ Mock AI results with candidate scoring
- ✅ Results modal with export option
- ✅ Smooth scrolling navigation
- ✅ Mobile-responsive design

## Technology Stack

- **Backend**: Node.js, Express.js
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with Flexbox/Grid
- **Icons**: Font Awesome 6
- **Fonts**: Inter (Google Fonts)

## Customization

### Colors
The app uses a blue-based color scheme. Main colors:
- Primary Blue: `#3b82f6`
- Dark Blue: `#1d4ed8`
- Gray: `#6b7280`
- Dark Gray: `#1f2937`

### Adding Real AI Functionality

To add real AI resume screening:

1. Replace the mock `screenResumes()` function in `script.js`
2. Add backend API endpoints for file processing
3. Integrate with AI services (OpenAI, Google Cloud AI, etc.)
4. Add database for storing results

### Example Backend Integration

```javascript
// In server.js - add API endpoints
app.post('/api/screen-resumes', upload.array('resumes'), async (req, res) => {
  // Process uploaded files
  // Call AI service
  // Return results
});
```

## Performance Features

- Optimized CSS with efficient selectors
- Lazy loading animations
- Minimal JavaScript bundle
- Compressed assets serving
- Mobile-first responsive design

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## License

MIT License - feel free to use for your projects!

## Future Enhancements

- [ ] User authentication system
- [ ] Real AI integration (OpenAI, etc.)
- [ ] Database for storing jobs and results
- [ ] Advanced filtering and sorting
- [ ] Email notifications
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] API for third-party integrations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

Built with ❤️ using modern web technologies
