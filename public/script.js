// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const jobInput = document.querySelector('.job-input');
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navLinks = document.querySelector('.nav-links');

// File handling
let uploadedFiles = [];
let processedFiles = new Set(); // Track files that have been processed
let previousResults = []; // Store previous analysis results for collapsed display

// Function to sort previous results by score (high to low) then by firstname alphabetically
function sortPreviousResults(results) {
    return [...results].sort((a, b) => {
        // Extract numeric score from string (remove % and convert to number)
        const scoreA = parseFloat(a.score.toString().replace('%', '')) || 0;
        const scoreB = parseFloat(b.score.toString().replace('%', '')) || 0;
        
        // First sort by score (descending - higher scores first)
        if (scoreA !== scoreB) {
            return scoreB - scoreA;
        }
        
        // If scores are equal, sort by first name alphabetically
        const firstNameA = a.candidateName.split(' ')[0].toLowerCase();
        const firstNameB = b.candidateName.split(' ')[0].toLowerCase();
        return firstNameA.localeCompare(firstNameB);
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeJobInput();
    initializeMobileMenu();
    initializeScrollEffects();
    initializeCounterAnimation();
    initializeHeroButtons();
    
    // Initialize upload area state
    updateScreenButton();
    
    // Initialize result section
    const resultSection = document.getElementById('resultSection');
    if (resultSection) {
        const resultContent = resultSection.querySelector('.result-content');
        console.log('🎯 Resume screening app initialized');
    
    // Test API connectivity
    testAPIConnection();
    }
    
    // Temporary test button - remove after debugging
    // const testBtn = document.createElement('button');
    // testBtn.textContent = 'Test Previous Results';
    // testBtn.style.position = 'fixed';
    // testBtn.style.bottom = '20px';
    // testBtn.style.right = '20px';
    // testBtn.style.zIndex = '9999';
    // testBtn.style.padding = '10px 15px';
    // testBtn.style.background = '#10b981';
    // testBtn.style.color = 'white';
    // testBtn.style.border = 'none';
    // testBtn.style.borderRadius = '5px';
    // testBtn.style.cursor = 'pointer';
    // testBtn.style.fontSize = '12px';
    // testBtn.onclick = testPreviousResults;
    // document.body.appendChild(testBtn);
});

// File Upload Functionality
function initializeFileUpload() {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        const hasJobDescription = jobInput.value.trim().length > 10;
        
        if (!hasJobDescription) {
            showUploadTooltip();
            return;
        }
        
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
    // Check if job description is provided first
    const hasJobDescription = jobInput.value.trim().length > 10;
    
    if (!hasJobDescription) {
        showUploadTooltip();
        return;
    }
    
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

function showUploadTooltip() {
    // Remove any existing tooltip
    const existingTooltip = document.querySelector('.upload-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'upload-tooltip';
    tooltip.innerHTML = `
        <div class="tooltip-content">
            <i class="fas fa-info-circle"></i>
            <span>Please enter a job description first</span>
        </div>
        <div class="tooltip-arrow"></div>
    `;
    
    // Position tooltip relative to upload area
    const uploadAreaRect = uploadArea.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    // Position tooltip above the upload area
    tooltip.style.position = 'fixed';
    tooltip.style.left = `${uploadAreaRect.left + (uploadAreaRect.width / 2) - 100}px`;
    tooltip.style.top = `${uploadAreaRect.top - 10}px`;
    tooltip.style.zIndex = '10000';
    
    // Add tooltip to page
    document.body.appendChild(tooltip);
    
    // Auto-remove tooltip after 3 seconds
    setTimeout(() => {
        if (tooltip && tooltip.parentNode) {
            tooltip.remove();
        }
    }, 3000);
    
    // Remove tooltip when user clicks anywhere
    const removeTooltip = () => {
        if (tooltip && tooltip.parentNode) {
            tooltip.remove();
        }
        document.removeEventListener('click', removeTooltip);
    };
    
    setTimeout(() => {
        document.addEventListener('click', removeTooltip);
    }, 100);
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
    
    // Update upload area visual state based on job description
    if (hasJobDescription) {
        uploadArea.classList.remove('disabled');
    } else {
        uploadArea.classList.add('disabled');
    }
    
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

    // IMPORTANT: Save existing results BEFORE showing loading state
    const resultSection = document.getElementById('resultSection');
    const resultContent = resultSection.querySelector('.result-content');
    const existingResult = resultContent.querySelector('.analysis-results');
    
    if (existingResult) {
        console.log('💾 Saving existing result before API call');
        
        // Use the improved getCurrentAnalysisResult function instead of manual extraction
        const currentResult = getCurrentAnalysisResult();
        
        if (currentResult) {
            console.log('💾 Saving complete current result to previous results:', currentResult);
            previousResults.push(currentResult);
        } else {
            console.log('⚠️ Could not extract current result data, trying fallback method');
            
            // Fallback: Extract key information from current result to store as previous
            const candidateNameEl = existingResult.querySelector('.candidate-name');
            const scoreEl = existingResult.querySelector('.match-score'); // Fixed selector
            const recommendationEl = existingResult.querySelector('.recommendation-badge');
            const fileNameEl = existingResult.querySelector('.file-name');
            
            const candidateName = candidateNameEl?.textContent || 'Unknown Candidate';
            const score = scoreEl?.textContent || '0%';
            const recommendation = recommendationEl?.textContent || 'N/A';
            const fileName = fileNameEl?.textContent || 'Unknown File';
            
            console.log('💾 Fallback: Saving basic info to previous results:', { candidateName, score, recommendation, fileName });
            
            previousResults.push({
                candidateName,
                score,
                recommendation,
                fileName,
                summary: 'Previous analysis - details not available',
                reasoning: 'Previous analysis - details not available',
                strengths: [],
                improvements: [],
                timestamp: new Date().toLocaleString()
            });
        
        }
        
        console.log('📊 Previous results array now has:', previousResults.length, 'items');
    } else {
        console.log('🆕 No existing result to save - this appears to be the first analysis');
    }

    // Show loading state (this will clear the existing content)
    displayAPIResponse({
        message: "Processing resume...",
        status: "loading"
    });

    // Try PythonAnywhere first, fallback to localhost if needed
    const apiUrl = 'http://localhost:8000/api/upload-resume'; // Uncomment for local testing
    
    console.log('📡 Calling API:', apiUrl);
    
    fetch(apiUrl, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('📡 API Response status:', response.status);
        console.log('📡 API Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('📡 API Response data:', data);
        displayAPIResponse(data);
        
        // If successful, show the analysis results and mark files as processed
        if (data.status === 'success') {
            console.log('✅ API call successful');
            console.log('📊 Data fields available:', Object.keys(data));
            
            // Handle multiple files response
            if (data.results && data.results.length > 0) {
                console.log('📊 Multiple files processed:', data.results.length);
                
                // Show results for all files, with highest score candidate in main area
                showMultipleAnalysisResults(data);
                
                // Mark all uploaded files as processed
                uploadedFiles.forEach(file => {
                    const fileId = `${file.name}_${file.size}_${file.lastModified}`;
                    processedFiles.add(fileId);
                });
            } else {
                // Single file response (backward compatibility)
                const analysisData = {
                    candidate_name: data.candidate_name || 'Unknown Candidate',
                    match_score: data.match_score || 0,
                    recommendation: data.recommendation || 'No recommendation',
                    filename: data.filename || 'Unknown File',
                    summary: data.summary || 'No summary available',
                    reasoning: data.reasoning || 'No reasoning provided',
                    strengths: data.strengths || [],
                    improvement_areas: data.improvement_areas || [],
                    timestamp: data.timestamp || new Date().toISOString()
                };
                
                console.log('📊 Processed single file analysis data:', analysisData);
                showAnalysisResults(analysisData);
                
                // Mark uploaded file as processed
                uploadedFiles.forEach(file => {
                    const fileId = `${file.name}_${file.size}_${file.lastModified}`;
                    processedFiles.add(fileId);
                });
            }
            
            // Clear the upload queue since files have been processed
            uploadedFiles = [];
            
            // Show processing summary if multiple files
            if (data.total_files > 1) {
                console.log(`📈 Processing summary: ${data.successful_files}/${data.total_files} files processed successfully`);
                if (data.failed_files > 0) {
                    console.warn(`⚠️ ${data.failed_files} files failed to process:`, data.failed_results);
                }
            }
        } else {
            console.error('❌ API returned error status:', data.status);
            console.error('❌ API error message:', data.message);
        }
    })
    .catch(error => {
        console.error('❌ Network/API Error:', error);
        console.error('❌ Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        displayAPIResponse({
            message: `Network error: ${error.message}. Please check your connection and try again.`,
            status: "error"
        });
    });
}

function displayAPIResponse(data) {
    const resultSection = document.getElementById('resultSection');
    const resultContent = resultSection.querySelector('.result-content');
    
    // Just show loading state briefly if needed
    if (data.status === 'loading') {
        // Sort previous results for consistent display during loading
        const sortedPreviousResults = sortPreviousResults(previousResults);
        
        // Create the candidate list HTML for left sidebar (only if there are multiple candidates)
        const candidateListHtml = sortedPreviousResults.length > 0 ? `
            <div class="results-left-panel">
                <div class="results-left-content">
                    <div class="previous-results-list">
                        ${sortedPreviousResults.map((result, index) => {
                            const originalIndex = previousResults.findIndex(r => 
                                r.candidateName === result.candidateName && 
                                r.score === result.score && 
                                r.timestamp === result.timestamp
                            );
                            return `
                                <div class="previous-result-item" onclick="expandPreviousResult(${originalIndex})">
                                    <div class="previous-score ${getScoreClass(result.score)}">${result.score}</div>
                                    <div class="previous-candidate-name">${result.candidateName}</div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        ` : '';
        
        // Create the loading content
        const loadingContentHtml = `
            <div class="results-right-panel">
                <div class="results-right-content">
                    <div class="analysis-results">
                        <div class="loading-state">
                            <i class="fas fa-spinner fa-spin"></i>
                            <h3>Analyzing Resume...</h3>
                            <p>Please wait while we process your resume against the job description.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Show loading state with appropriate layout
        if (sortedPreviousResults.length > 0) {
            // Multiple candidates: use two-column layout with candidate list on left
            resultContent.innerHTML = `
                <div class="results-two-column-layout">
                    ${candidateListHtml}
                    ${loadingContentHtml}
                </div>
            `;
        } else {
            // Single candidate: use full-width layout
            resultContent.innerHTML = loadingContentHtml;
        }
    }
    
    // If there's an error, show it in the result section
    if (data.status === 'error') {
        // Sort previous results for consistent display during error
        const sortedPreviousResults = sortPreviousResults(previousResults);
        
        // Create the candidate list HTML for left sidebar (only if there are multiple candidates)
        const candidateListHtml = sortedPreviousResults.length > 0 ? `
            <div class="results-left-panel">
                <div class="results-left-content">
                    <div class="previous-results-list">
                        ${sortedPreviousResults.map((result, index) => {
                            const originalIndex = previousResults.findIndex(r => 
                                r.candidateName === result.candidateName && 
                                r.score === result.score && 
                                r.timestamp === result.timestamp
                            );
                            return `
                                <div class="previous-result-item" onclick="expandPreviousResult(${originalIndex})">
                                    <div class="previous-score ${getScoreClass(result.score)}">${result.score}</div>
                                    <div class="previous-candidate-name">${result.candidateName}</div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        ` : '';
        
        // Create the error content
        const errorContentHtml = `
            <div class="results-right-panel">
                <div class="results-right-content">
                    <div class="analysis-results">
                        <div class="error-state">
                            <i class="fas fa-exclamation-triangle"></i>
                            <h3>Analysis Failed</h3>
                            <p>${data.message || 'An error occurred during analysis.'}</p>
                            <button class="btn-primary" onclick="location.reload()">Try Again</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Show error state with appropriate layout
        if (sortedPreviousResults.length > 0) {
            // Multiple candidates: use two-column layout with candidate list on left
            resultContent.innerHTML = `
                <div class="results-two-column-layout">
                    ${candidateListHtml}
                    ${errorContentHtml}
                </div>
            `;
        } else {
            // Single candidate: use full-width layout
            resultContent.innerHTML = errorContentHtml;
        }
    }
}

// Function to normalize data format for consistent display
function normalizeAnalysisData(data) {
    // Check if this is from previous results (has candidateName) or API response (has candidate_name)
    if (data.candidateName) {
        // This is from previous results, already in our format
        let matchScore = data.score;
        // Handle different score formats
        if (typeof matchScore === 'string') {
            matchScore = matchScore.replace('%', ''); // Remove % for consistent display
        }
        
        console.log('🔄 Normalizing previous result data:', {
            original_score: data.score,
            normalized_score: matchScore,
            candidate: data.candidateName
        });
        
        return {
            candidate_name: data.candidateName,
            filename: data.fileName,
            match_score: matchScore,
            recommendation: data.recommendation,
            summary: data.summary,
            reasoning: data.reasoning,
            strengths: data.strengths,
            improvement_areas: data.improvements,
            timestamp: data.timestamp
        };
    } else {
        // This is from API response, use as-is
        console.log('🔄 Using API response data as-is:', data);
        return data;
    }
}

function showMultipleAnalysisResults(data) {
    console.log('🔍 showMultipleAnalysisResults called with:', data);
    
    // Results are already sorted by score (highest first) from backend
    const results = data.results;
    const highestScoreCandidate = results[0]; // First result has highest score
    const otherCandidates = results.slice(1); // Rest go to previous results
    
    console.log('🏆 Highest score candidate:', highestScoreCandidate.candidate_name, highestScoreCandidate.match_score);
    console.log('📊 Other candidates:', otherCandidates.length);
    
    // Add other candidates to previous results (they're already sorted)
    otherCandidates.forEach(result => {
        const previousResult = {
            candidateName: result.candidate_name,
            fileName: result.filename,
            score: `${result.match_score}`,
            recommendation: result.recommendation,
            summary: result.summary,
            reasoning: result.reasoning,
            strengths: result.strengths,
            improvements: result.improvement_areas,
            timestamp: result.timestamp
        };
        previousResults.push(previousResult);
    });
    
    console.log('📊 Added', otherCandidates.length, 'candidates to previous results');
    
    // Convert highest score candidate to the expected format and display
    const displayData = {
        candidate_name: highestScoreCandidate.candidate_name,
        filename: highestScoreCandidate.filename,
        match_score: highestScoreCandidate.match_score,
        recommendation: highestScoreCandidate.recommendation,
        summary: highestScoreCandidate.summary,
        reasoning: highestScoreCandidate.reasoning,
        strengths: highestScoreCandidate.strengths,
        improvement_areas: highestScoreCandidate.improvement_areas,
        timestamp: highestScoreCandidate.timestamp
    };
    
    // Display the highest scoring candidate in the main area
    showAnalysisResults(displayData);
}

function showAnalysisResults(data) {
    console.log('🔍 showAnalysisResults called with:', data);
    
    // Normalize data format
    const normalizedData = normalizeAnalysisData(data);
    console.log('🔄 Normalized data:', normalizedData);
    
    // Display results in the result section instead of a modal
    const resultSection = document.getElementById('resultSection');
    const resultContent = resultSection.querySelector('.result-content');
    
    console.log('📍 Result section found:', !!resultSection);
    console.log('📍 Result content found:', !!resultContent);
    
    // Previous results have already been saved before the API call
    console.log('📊 Previous results available for display:', previousResults.length, 'items');
    
    // Sort previous results by match score (high to low), then by firstname alphabetically
    const sortedPreviousResults = sortPreviousResults(previousResults);
    
    console.log('📊 Sorted previous results:', sortedPreviousResults.map(r => `${r.candidateName}: ${r.score}`));

    // Add current result to display list
    const currentResult = {
        candidateName: normalizedData.candidate_name || 'Candidate',
        score: `${normalizedData.match_score || 0}`,
        recommendation: normalizedData.recommendation || 'Analysis Complete',
        fileName: normalizedData.filename || 'Uploaded Resume',
        summary: normalizedData.summary || 'No summary available',
        reasoning: normalizedData.reasoning || 'No reasoning provided',
        strengths: normalizedData.strengths || [],
        improvements: normalizedData.improvement_areas || [],
        timestamp: normalizedData.timestamp || new Date().toISOString(),
        isCurrent: true
    };
    
    // Combine current result with previous results
    const allResults = [currentResult, ...sortedPreviousResults];
    const sortedAllResults = sortPreviousResults(allResults);
    
    // Create the results display with all results including current one
    const allResultsHtml = sortedAllResults.length > 0 ? `
        <div class="previous-results">
            <div class="previous-results-list">
                ${sortedAllResults.map((result, index) => {
                    if (result.isCurrent) {
                        // Current result - no click handler, special styling
                        return `
                            <div class="previous-result-item current-result">
                                <div class="previous-score ${getScoreClass(result.score)}">${result.score}</div>
                                <div class="previous-candidate-name">${result.candidateName}</div>
                            </div>
                        `;
                    } else {
                        // Previous result - with click handler
                        const originalIndex = previousResults.findIndex(r => 
                            r.candidateName === result.candidateName && 
                            r.score === result.score && 
                            r.timestamp === result.timestamp
                        );
                        return `
                            <div class="previous-result-item" onclick="expandPreviousResult(${originalIndex})">
                                <div class="previous-score ${getScoreClass(result.score)}">${result.score}</div>
                                <div class="previous-candidate-name">${result.candidateName}</div>
                            </div>
                        `;
                    }
                }).join('')}
            </div>
        </div>
    ` : '';
    
    if (previousResults.length > 0) {
        console.log('✅ Previous results section will be displayed with', previousResults.length, 'items');
        console.log('🔧 Previous results HTML preview:', allResultsHtml.substring(0, 200) + '...');
    } else {
        console.log('ℹ️ No previous results to display');
    }
    
    console.log('🔧 Setting innerHTML with previous results:', previousResults.length > 0);
    
    // Create the candidate list HTML for left sidebar (only if there are multiple candidates)
    const candidateListHtml = sortedAllResults.length > 1 ? `
        <div class="results-left-panel">
            <div class="results-left-content">
                <div class="previous-results-list">
                    ${sortedAllResults.map((result, index) => {
                        if (result.isCurrent) {
                            // Current result - no click handler, special styling
                            return `
                                <div class="previous-result-item current-result">
                                    <div class="previous-score ${getScoreClass(result.score)}">${result.score}</div>
                                    <div class="previous-candidate-name">${result.candidateName}</div>
                                </div>
                            `;
                        } else {
                            // Previous result - with click handler
                            const originalIndex = previousResults.findIndex(r => 
                                r.candidateName === result.candidateName && 
                                r.score === result.score && 
                                r.timestamp === result.timestamp
                            );
                            return `
                                <div class="previous-result-item" onclick="expandPreviousResult(${originalIndex})">
                                    <div class="previous-score ${getScoreClass(result.score)}">${result.score}</div>
                                    <div class="previous-candidate-name">${result.candidateName}</div>
                                </div>
                            `;
                        }
                    }).join('')}
                </div>
            </div>
        </div>
    ` : '';
    
    // Create the main analysis content
    const analysisContentHtml = `
        <div class="results-right-panel">
            <div class="results-right-content">
                <div class="analysis-results">
                    <div class="match-score-section">
                        <div class="candidate-info">
                            <div class="candidate-name">${normalizedData.candidate_name || 'Candidate'}</div>
                            <div class="file-name">${normalizedData.filename || 'Uploaded Resume'}</div>
                        </div>
                        <div class="score-info">
                            <div class="match-score ${getScoreClass(normalizedData.match_score)}">${normalizedData.match_score || 0}</div>
                        </div>
                    </div>
                    
                    <div class="analysis-details">
                        <div class="detail-section">
                            <h4><i class="fas fa-chart-line"></i> Summary</h4>
                            <p>${normalizedData.summary || 'No summary available.'}</p>
                        </div>
                        
                        <div class="detail-section">
                            <h4><i class="fas fa-lightbulb"></i> Reasoning</h4>
                            <p>${normalizedData.reasoning || 'No reasoning provided.'}</p>
                        </div>
                        
                        ${normalizedData.strengths && normalizedData.strengths.length > 0 ? `
                            <div class="detail-section">
                                <h4><i class="fas fa-check-circle"></i> Strengths</h4>
                                <ul class="strengths-list">
                                    ${normalizedData.strengths.map(strength => `<li>${strength}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${normalizedData.improvement_areas && normalizedData.improvement_areas.length > 0 ? `
                            <div class="detail-section">
                                <h4><i class="fas fa-exclamation-triangle"></i> Areas for Improvement</h4>
                                <ul class="improvement-list">
                                    ${normalizedData.improvement_areas.map(area => `<li>${area}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="result-footer">
                        <div class="timestamp">
                            <i class="fas fa-clock"></i>
                            Analyzed at ${new Date(normalizedData.timestamp || Date.now()).toLocaleString()}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Set the HTML with the new layout
    if (sortedAllResults.length > 1) {
        // Multiple candidates: use two-column layout with candidate list on left
        resultContent.innerHTML = `
            <div class="results-two-column-layout">
                ${candidateListHtml}
                ${analysisContentHtml}
            </div>
        `;
    } else {
        // Single candidate: use full-width layout
        resultContent.innerHTML = analysisContentHtml;
    }
    
    console.log('🔧 HTML has been set. Checking if previous results are visible...');
    
    // Verify the previous results section was added
    setTimeout(() => {
        const addedPreviousSection = resultContent.querySelector('.previous-results');
        console.log('🔍 Previous results section in DOM:', !!addedPreviousSection);
        if (addedPreviousSection) {
            console.log('🔍 Previous results items count:', addedPreviousSection.querySelectorAll('.previous-result-item').length);
        }
    }, 100);
    
    // Scroll to results if needed
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Function to extract current analysis result data from the DOM
function getCurrentAnalysisResult() {
    const analysisResults = document.querySelector('.analysis-results');
    if (!analysisResults || analysisResults.querySelector('.loading-state') || analysisResults.querySelector('.error-state')) {
        return null; // No valid analysis result currently displayed
    }
    
    const candidateNameEl = analysisResults.querySelector('.candidate-name');
    const fileNameEl = analysisResults.querySelector('.file-name');
    const scoreEl = analysisResults.querySelector('.match-score');
    const recommendationBadgeEl = analysisResults.querySelector('.recommendation-badge');
    
    // Extract detailed information - be more specific about which detail sections
    const detailSections = analysisResults.querySelectorAll('.detail-section');
    let summaryEl = null, reasoningEl = null, strengthsEls = [], improvementsEls = [];
    
    detailSections.forEach((section, index) => {
        const heading = section.querySelector('h4');
        if (heading) {
            const headingText = heading.textContent.toLowerCase();
            if (headingText.includes('summary')) {
                summaryEl = section.querySelector('p');
            } else if (headingText.includes('reasoning')) {
                reasoningEl = section.querySelector('p');
            } else if (headingText.includes('strengths')) {
                strengthsEls = section.querySelectorAll('li');
            } else if (headingText.includes('improvement')) {
                improvementsEls = section.querySelectorAll('li');
            }
        }
    });
    
    if (!candidateNameEl || !scoreEl) {
        console.error('❌ Essential elements missing for getCurrentAnalysisResult');
        console.log('candidateNameEl:', candidateNameEl);
        console.log('scoreEl:', scoreEl);
        return null;
    }
    
    const result = {
        candidateName: candidateNameEl.textContent.trim(),
        fileName: fileNameEl ? fileNameEl.textContent.trim() : '',
        score: scoreEl.textContent.trim(),
        recommendation: recommendationBadgeEl ? recommendationBadgeEl.textContent.trim() : '',
        summary: summaryEl ? summaryEl.textContent.trim() : '',
        reasoning: reasoningEl ? reasoningEl.textContent.trim() : '',
        strengths: Array.from(strengthsEls).map(el => el.textContent.trim()).filter(text => text.length > 0),
        improvements: Array.from(improvementsEls).map(el => el.textContent.trim()).filter(text => text.length > 0),
        timestamp: new Date().toLocaleString()
    };
    
    console.log('💾 Extracted current analysis result:', result);
    return result;
}

function expandPreviousResult(index) {
    console.log('🔍 Expanding previous result at index:', index);
    const clickedResult = previousResults[index];
    if (!clickedResult) {
        console.error('❌ No result found at index:', index);
        return;
    }

    // First, check if there's currently displayed analysis result that needs to be saved
    const currentAnalysisResult = getCurrentAnalysisResult();
    if (currentAnalysisResult) {
        console.log('💾 Saving current analysis result to previous results');
        // Add current result to previous results (but not the clicked one)
        const newPreviousResults = [...previousResults];
        newPreviousResults.push(currentAnalysisResult);
        
        // Remove the clicked result from previous results
        newPreviousResults.splice(index, 1);
        
        // Update the previousResults array
        previousResults.length = 0;
        previousResults.push(...newPreviousResults);
    } else {
        console.log('🗑️ No current analysis to save, just removing clicked result from previous');
        // Just remove the clicked result from previous results
        previousResults.splice(index, 1);
    }

    // Display the clicked result in the main analysis area
    console.log('📺 Displaying clicked result in main area:', clickedResult.candidateName);
    showAnalysisResults(clickedResult);
}

// clearPreviousResults function removed since we no longer have a delete button

function getScoreClass(score) {
    // Convert score to number if it's a string
    const numScore = typeof score === 'string' ? parseFloat(score.replace('%', '')) : score;
    
    if (numScore >= 90) return 'score-excellent';  // 90-100: 深绿色
    else if (numScore >= 80) return 'score-good';      // 80-89: 绿色
    else if (numScore >= 70) return 'score-fair';      // 70-79: 浅绿色
    else if (numScore >= 60) return 'score-average';   // 60-69: 黄色
    else if (numScore >= 50) return 'score-below';     // 50-59: 橙色
    else return 'score-poor';                          // 0-49: 红色
}

function getRecommendationClass(recommendation) {
    // Keep this for backward compatibility, but we'll primarily use getScoreClass
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
        // Try both close functions to handle different modal types
        if (typeof closePreviousResultModal === 'function') {
            closePreviousResultModal();
        }
        if (typeof closeModal === 'function') {
            closeModal();
        }
    }
});

// Close modal with escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Try both close functions to handle different modal types
        if (typeof closePreviousResultModal === 'function') {
            closePreviousResultModal();
        }
        if (typeof closeModal === 'function') {
            closeModal();
        }
    }
});

// Hero Buttons Functionality
function initializeHeroButtons() {
    // Hero buttons have been removed, so this function is no longer needed
    // Keeping the function for potential future use
}

// Test function to simulate multiple results (for debugging)
function testPreviousResults() {
    console.log('Testing previous results functionality...');
    
    // Simulate first result
    showAnalysisResults({
        candidate_name: 'John Smith',
        match_score: 85,
        recommendation: 'Good Match',
        filename: 'john_smith_resume.pdf',
        summary: 'Strong technical background with relevant experience.',
        reasoning: 'Good match for the position requirements.',
        strengths: ['JavaScript', 'React', 'Node.js'],
        improvement_areas: ['Could use more leadership experience'],
        timestamp: new Date().toISOString()
    });
    
    // Add a button to test second result
    setTimeout(() => {
        const testBtn = document.createElement('button');
        testBtn.textContent = 'Test Second Result';
        testBtn.style.position = 'fixed';
        testBtn.style.top = '10px';
        testBtn.style.right = '10px';
        testBtn.style.zIndex = '9999';
        testBtn.style.padding = '10px';
        testBtn.style.background = '#3b82f6';
        testBtn.style.color = 'white';
        testBtn.style.border = 'none';
        testBtn.style.borderRadius = '5px';
        testBtn.style.cursor = 'pointer';
        
        testBtn.onclick = () => {
            showAnalysisResults({
                candidate_name: 'Jane Doe',
                match_score: 92,
                recommendation: 'Strong Match',
                filename: 'jane_doe_resume.pdf',
                summary: 'Excellent candidate with strong technical skills.',
                reasoning: 'Perfect match for the position requirements.',
                strengths: ['Python', 'Machine Learning', 'Leadership'],
                improvement_areas: ['Could improve communication skills'],
                timestamp: new Date().toISOString()
            });
            testBtn.remove();
        };
        
        document.body.appendChild(testBtn);
    }, 1000);
}

// Add test button to page (remove in production)
window.testPreviousResults = testPreviousResults;

// Test API connectivity
function testAPIConnection() {
    console.log('🔌 Testing API connectivity...');
    
    fetch('http://localhost:8000/api/health', {
        method: 'GET'
    })
    .then(response => {
        console.log('🔌 Health check status:', response.status);
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(`Health check failed: ${response.status}`);
        }
    })
    .then(data => {
        console.log('✅ API is healthy:', data);
    })
    .catch(error => {
        console.error('❌ API health check failed:', error);
        console.log('🔧 Trying alternative endpoint...');
        
        // Try the info endpoint as backup
        fetch('http://localhost:8000/api/info')
        .then(response => {
            console.log('🔌 Info endpoint status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('✅ API info:', data);
        })
        .catch(error2 => {
            console.error('❌ All API endpoints failed:', error2);
            console.log('💡 Suggestion: Check if the backend service is running on PythonAnywhere');
        });
    });
}
