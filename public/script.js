// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const jobInput = document.querySelector('.job-input');
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navLinks = document.querySelector('.nav-links');

// File handling
let uploadedFiles = [];
let processedFiles = new Set(); // Track files that have been processed

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeJobInput();
    initializeMobileMenu();
    initializeScrollEffects();
    initializeCounterAnimation();
    initializeHeroButtons();
});

// File Upload Functionality
function initializeFileUpload() {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e) {
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

function handleFiles(files) {
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxFileSize = 10 * 1024 * 1024; // 10MB

    Array.from(files).forEach(file => {
        // Create a unique identifier for the file
        const fileId = `${file.name}_${file.size}_${file.lastModified}`;
        
        if (!validTypes.includes(file.type)) {
            alert(`File "${file.name}" is not supported. Please upload PDF files only.`);
            return;
        }
        
        if (file.size > maxFileSize) {
            alert(`File "${file.name}" is too large. Please upload files under 10MB.`);
            return;
        }
        
        // Check if file has already been processed
        if (processedFiles.has(fileId)) {
            alert(`File "${file.name}" has already been uploaded and processed.`);
            return;
        }
        
        // Check if file is already in the upload queue
        if (uploadedFiles.find(f => `${f.name}_${f.size}_${f.lastModified}` === fileId)) {
            alert(`File "${file.name}" is already selected for upload.`);
            return;
        }
        
        // Add file to upload queue
        uploadedFiles.push(file);
    });

    updateUploadDisplay();
    updateScreenButton();
}

function updateUploadDisplay() {
    // Keep the upload area unchanged - don't modify the visual state
    // The original drop zone interface remains visible at all times
    return;
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateUploadDisplay();
    updateScreenButton();
}

// Job Input Functionality
function initializeJobInput() {
    jobInput.addEventListener('input', updateScreenButton);
}

function updateScreenButton() {
    const hasJobDescription = jobInput.value.trim().length > 10;
    const hasFiles = uploadedFiles.length > 0;
    
    // Automatically trigger screening when both conditions are met
    if (hasJobDescription && hasFiles) {
        // Small delay to ensure UI updates are complete
        setTimeout(() => {
            callUploadAPI();
        }, 500);
    }
}

// Screen Resumes Functionality
function screenResumes() {
    // Show loading state in the upload area
    const uploadArea = document.getElementById('uploadArea');
    const originalContent = uploadArea.innerHTML;
    uploadArea.innerHTML = '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i><p>Screening resumes...</p></div>';
    
    // Simulate AI processing
    setTimeout(() => {
        showResults();
        // Restore original upload area content
        uploadArea.innerHTML = originalContent;
        // Re-initialize file upload functionality
        initializeFileUpload();
    }, 2000);
}

function showResults() {
    // Create mock results
    const mockResults = uploadedFiles.map((file, index) => ({
        name: file.name.replace(/\.[^/.]+$/, ""), // Remove extension
        score: Math.floor(Math.random() * 40) + 60, // Score between 60-100
        skills: ['JavaScript', 'React', 'Node.js', 'Python', 'SQL'].slice(0, Math.floor(Math.random() * 3) + 2),
        experience: `${Math.floor(Math.random() * 8) + 2} years`,
        match: ['Strong technical background', 'Relevant experience', 'Good cultural fit'][Math.floor(Math.random() * 3)]
    })).sort((a, b) => b.score - a.score);

    // Create results modal
    const modal = document.createElement('div');
    modal.className = 'results-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Screening Results</h2>
                <i class="fas fa-times modal-close" onclick="closeModal()"></i>
            </div>
            <div class="modal-body">
                <p class="results-summary">Found ${mockResults.length} candidates. Here are the top matches:</p>
                <div class="results-list">
                    ${mockResults.map((result, index) => `
                        <div class="result-item">
                            <div class="result-rank">#${index + 1}</div>
                            <div class="result-info">
                                <h3>${result.name}</h3>
                                <div class="result-score">Match Score: <span class="score-value">${result.score}%</span></div>
                                <div class="result-details">
                                    <span class="experience">${result.experience} experience</span>
                                    <div class="skills">
                                        ${result.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                                    </div>
                                    <div class="match-reason">${result.match}</div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-actions">
                    <button class="btn-primary" onclick="closeModal()">Close</button>
                    <button class="btn-outline" onclick="exportResults()">Export Results</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    
    // Add modal styles if not already added
    if (!document.querySelector('#modal-styles')) {
        const modalStyles = document.createElement('style');
        modalStyles.id = 'modal-styles';
        modalStyles.textContent = `
            .results-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                padding: 1rem;
            }
            
            .modal-content {
                background: white;
                border-radius: 1rem;
                max-width: 800px;
                width: 100%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 2rem 2rem 1rem;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .modal-header h2 {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0;
            }
            
            .modal-close {
                font-size: 1.5rem;
                color: #6b7280;
                cursor: pointer;
                padding: 0.5rem;
            }
            
            .modal-close:hover {
                color: #374151;
            }
            
            .modal-body {
                padding: 1rem 2rem 2rem;
            }
            
            .results-summary {
                color: #6b7280;
                margin-bottom: 1.5rem;
                font-size: 1rem;
            }
            
            .results-list {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .result-item {
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                padding: 1.5rem;
                background: #f8fafc;
                border-radius: 0.75rem;
                border-left: 4px solid #3b82f6;
            }
            
            .result-rank {
                background: #3b82f6;
                color: white;
                width: 2rem;
                height: 2rem;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.875rem;
                flex-shrink: 0;
            }
            
            .result-info {
                flex: 1;
            }
            
            .result-info h3 {
                font-size: 1.125rem;
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 0.5rem;
            }
            
            .result-score {
                margin-bottom: 0.75rem;
                color: #374151;
            }
            
            .score-value {
                font-weight: 700;
                color: #059669;
            }
            
            .result-details {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .experience {
                color: #6b7280;
                font-size: 0.875rem;
            }
            
            .skills {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            
            .skill-tag {
                background: #dbeafe;
                color: #1d4ed8;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.75rem;
                font-weight: 500;
            }
            
            .match-reason {
                color: #059669;
                font-size: 0.875rem;
                font-style: italic;
            }
            
            .modal-actions {
                display: flex;
                gap: 1rem;
                justify-content: flex-end;
                padding-top: 1rem;
                border-top: 1px solid #e5e7eb;
            }
            
            @media (max-width: 640px) {
                .modal-content {
                    margin: 1rem;
                    max-height: calc(100vh - 2rem);
                }
                
                .modal-header, .modal-body {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                
                .result-item {
                    flex-direction: column;
                    text-align: center;
                }
                
                .modal-actions {
                    flex-direction: column;
                }
            }
        `;
        document.head.appendChild(modalStyles);
    }
}

function closeModal() {
    const modal = document.querySelector('.results-modal');
    if (modal) {
        modal.remove();
    }
}

function exportResults() {
    alert('Export functionality would be implemented here. Results would be downloaded as CSV or PDF.');
}

// Mobile Menu Functionality
function initializeMobileMenu() {
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }
}

function toggleMobileMenu() {
    navLinks.classList.toggle('mobile-active');
    
    // Add mobile menu styles if not already added
    if (!document.querySelector('#mobile-menu-styles')) {
        const mobileStyles = document.createElement('style');
        mobileStyles.id = 'mobile-menu-styles';
        mobileStyles.textContent = `
            @media (max-width: 968px) {
                .nav-links.mobile-active {
                    display: flex;
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    background: white;
                    flex-direction: column;
                    padding: 2rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    border-top: 1px solid #e5e7eb;
                }
                
                .nav-links.mobile-active a,
                .nav-links.mobile-active button {
                    margin-bottom: 1rem;
                }
            }
        `;
        document.head.appendChild(mobileStyles);
    }
}

// Scroll Effects
function initializeScrollEffects() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Header background on scroll
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        const header = document.querySelector('.header');
        
        if (currentScroll > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
        }
        
        lastScroll = currentScroll;
    });
}

// Counter Animation
function initializeCounterAnimation() {
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const statsSection = document.querySelector('.stats');
    if (statsSection) {
        observer.observe(statsSection);
    }
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/[^0-9]/g, ''));
        const suffix = counter.textContent.replace(/[0-9,]/g, '');
        let current = 0;
        const increment = target / 100;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target.toLocaleString() + suffix;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current).toLocaleString() + suffix;
            }
        }, 20);
    });
}

// API Call Functions
function callUploadAPI() {
    if (uploadedFiles.length === 0) {
        displayAPIResponse({
            message: "No files uploaded. Please upload resume files first.",
            status: "error"
        });
        return;
    }

    const jobDescription = jobInput.value.trim();
    if (jobDescription.length < 10) {
        displayAPIResponse({
            message: "Please enter a job description (at least 10 characters).",
            status: "error"
        });
        return;
    }

    // Create FormData for file upload
    const formData = new FormData();
    
    // Add job description
    formData.append('job_description', jobDescription);
    
    // Add all uploaded files
    uploadedFiles.forEach(file => {
        formData.append('file', file);
    });

    // Show loading state
    displayAPIResponse({
        message: "Processing resume...",
        status: "loading"
    });

    // Call the FastAPI backend
    fetch('/api/upload-resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayAPIResponse(data);
        // If successful, show the analysis results and mark files as processed
        if (data.status === 'success') {
            showAnalysisResults(data);
            // Mark all uploaded files as processed
            uploadedFiles.forEach(file => {
                const fileId = `${file.name}_${file.size}_${file.lastModified}`;
                processedFiles.add(fileId);
            });
            // Clear the upload queue since files have been processed
            uploadedFiles = [];
        }
    })
    .catch(error => {
        console.error('Error calling API:', error);
        displayAPIResponse({
            message: "Error processing resume. Please try again.",
            status: "error"
        });
    });
}

function displayAPIResponse(data) {
    // Remove the old response display approach - no more popups
    // Just show loading state briefly if needed
    if (data.status === 'loading') {
        const resultSection = document.getElementById('resultSection');
        const resultContent = resultSection.querySelector('.result-content');
        
        resultContent.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <h3>Analyzing Resume...</h3>
                <p>Please wait while we process your resume against the job description.</p>
            </div>
        `;
    }
    
    // If there's an error, show it in the result section
    if (data.status === 'error') {
        const resultSection = document.getElementById('resultSection');
        const resultContent = resultSection.querySelector('.result-content');
        
        resultContent.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Analysis Failed</h3>
                <p>${data.message || 'An error occurred during analysis.'}</p>
                <button class="btn-primary" onclick="location.reload()">Try Again</button>
            </div>
        `;
    }
}

function showAnalysisResults(data) {
    // Display results in the result section instead of a modal
    const resultSection = document.getElementById('resultSection');
    const resultContent = resultSection.querySelector('.result-content');
    
    // Create the results display
    resultContent.innerHTML = `
        <div class="analysis-results">
            <div class="match-score-section">
                <div class="candidate-info">
                    <div class="candidate-name">${data.candidate_name || 'Candidate'}</div>
                    <div class="file-name">${data.filename || 'Uploaded Resume'}</div>
                </div>
                <div class="score-info">
                    <div class="score-number ${getRecommendationClass(data.recommendation)}">${data.match_score || 0}%</div>
                    <div class="recommendation">
                        <span class="recommendation-badge ${getRecommendationClass(data.recommendation)}">
                            ${data.recommendation || 'Analysis Complete'}
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-details">
                <div class="detail-section">
                    <h4><i class="fas fa-chart-line"></i> Summary</h4>
                    <p>${data.summary || 'No summary available.'}</p>
                </div>
                
                <div class="detail-section">
                    <h4><i class="fas fa-lightbulb"></i> Reasoning</h4>
                    <p>${data.reasoning || 'No reasoning provided.'}</p>
                </div>
                
                ${data.strengths && data.strengths.length > 0 ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-check-circle"></i> Strengths</h4>
                        <ul class="strengths-list">
                            ${data.strengths.map(strength => `<li>${strength}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${data.improvement_areas && data.improvement_areas.length > 0 ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-exclamation-triangle"></i> Areas for Improvement</h4>
                        <ul class="improvement-list">
                            ${data.improvement_areas.map(area => `<li>${area}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
            
            <div class="result-footer">
                <div class="timestamp">
                    <i class="fas fa-clock"></i>
                    Analyzed at ${new Date(data.timestamp || Date.now()).toLocaleString()}
                </div>
            </div>
        </div>
    `;
    
    // Scroll to results if needed
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function getRecommendationClass(recommendation) {
    if (!recommendation) return 'neutral';
    
    const lower = recommendation.toLowerCase();
    if (lower.includes('strong') || lower.includes('excellent') || lower.includes('good')) {
        return 'positive';
    } else if (lower.includes('weak') || lower.includes('poor') || lower.includes('not')) {
        return 'negative';
    } else {
        return 'neutral';
    }
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('results-modal')) {
        closeModal();
    }
});

// Close modal with escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Hero Buttons Functionality
function initializeHeroButtons() {
    // Hero buttons have been removed, so this function is no longer needed
    // Keeping the function for potential future use
}
