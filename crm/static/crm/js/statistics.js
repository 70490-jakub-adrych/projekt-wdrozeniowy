/**
 * Statistics Dashboard JavaScript
 * Handles chart rendering and interactive functionality for the statistics dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Chart.js global defaults
    Chart.defaults.font.family = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.color = '#666';
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;

    // Update color schemes for consistency with dashboard
    const colorSchemes = {
        status: {
            backgroundColor: [
                '#007bff', // New - primary - light blue
                '#17a2b8', // In Progress - info - teal
                '#ffc107', // Unresolved - warning - yellow
                '#28a745', // Resolved - success - green
                '#6c757d'  // Closed - secondary - gray
            ],
            borderColor: '#fff',
            borderWidth: 1
        },
        priority: {
            backgroundColor: [
                '#6c757d', // Low - secondary - gray
                '#17a2b8', // Medium - info -   teal
                '#ffc107', // High - warning -  yellow
                '#dc3545'  // Critical - danger - red
            ],
            borderColor: '#fff',
            borderWidth: 1
        },
        category: {
            backgroundColor: [
                '#fd7e14', // Hardware - orange
                '#20c997', // Software - teal
                '#6f42c1', // Network - purple
                '#e83e8c', // Account - pink
                '#6c757d'  // Other - secondary
            ],
            borderColor: '#fff',
            borderWidth: 1
        },
        timeline: {
            borderColor: '#007bff',
            backgroundColor: 'rgba(0,123,255,0.2)',
            pointBackgroundColor: '#007bff',
            pointBorderColor: '#fff',
            pointRadius: 4
        }
    };

    /**
     * Get and parse data from hidden elements in the HTML
     */
    const getChartData = () => {
        // Extract ticket count data with better error handling for missing elements
        const tickets = {
            new: parseInt(document.querySelector('[data-new-tickets]')?.getAttribute('data-new-tickets')) || 0,
            inProgress: parseInt(document.querySelector('[data-in-progress-tickets]')?.getAttribute('data-in-progress-tickets')) || 0,
            unresolved: parseInt(document.querySelector('[data-unresolved-tickets]')?.getAttribute('data-unresolved-tickets')) || 0,
            resolved: parseInt(document.querySelector('[data-resolved-tickets]')?.getAttribute('data-resolved-tickets')) || 0,
            closed: parseInt(document.querySelector('[data-closed-tickets]')?.getAttribute('data-closed-tickets')) || 0
        };

        // Enhanced debug output to help troubleshoot
        console.log("Ticket data parsed from HTML:", tickets);
        console.log("Debug ticket counts from HTML:", document.getElementById('debug-ticket-counts')?.textContent);
        
        // Parse JSON data for distributions
        let priorityDistribution = [];
        let categoryDistribution = [];
        let ticketsByDate = [];

        try {
            const priorityData = document.querySelector('[data-priority-distribution]').getAttribute('data-priority-distribution');
            priorityDistribution = JSON.parse(priorityData.replace(/'/g, '"')) || [];
        } catch (e) {
            console.error('Error parsing priority distribution data:', e);
        }

        try {
            const categoryData = document.querySelector('[data-category-distribution]').getAttribute('data-category-distribution');
            categoryDistribution = JSON.parse(categoryData.replace(/'/g, '"')) || [];
        } catch (e) {
            console.error('Error parsing category distribution data:', e);
        }

        try {
            const timelineData = document.querySelector('[data-tickets-by-date]').getAttribute('data-tickets-by-date');
            ticketsByDate = JSON.parse(timelineData.replace(/'/g, '"')) || [];
        } catch (e) {
            console.error('Error parsing timeline data:', e);
        }

        const period = document.querySelector('[data-period]').getAttribute('data-period') || 'month';

        return {
            tickets,
            priorityDistribution,
            categoryDistribution,
            ticketsByDate,
            period
        };
    };

    /**
     * Format dates based on period type
     */
    const formatDate = (dateString, period) => {
        const date = new Date(dateString);
        switch (period) {
            case 'day':
                return date.toLocaleDateString('pl-PL', { hour: '2-digit', minute: '2-digit' });
            case 'week':
                return `Tydz. ${getWeekNumber(date)} (${date.toLocaleDateString('pl-PL', { month: 'short', day: 'numeric' })})`;
            case 'month':
                return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'short' });
            case 'year':
                return date.getFullYear().toString();
            default:
                return date.toLocaleDateString('pl-PL');
        }
    };

    /**
     * Get week number from date
     */
    const getWeekNumber = (date) => {
        const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
        const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
        return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
    };

    /**
     * Translate status codes to readable Polish labels with correct pluralization
     */
    const getStatusLabel = (status) => {
        const labels = {
            'new': 'Nowe',
            'in_progress': 'W trakcie',
            'unresolved': 'Nierozwiązane',
            'resolved': 'Rozwiązane',
            'closed': 'Zamknięte'
        };
        return labels[status] || status;
    };

    /**
     * Translate priority codes to readable Polish labels
     */
    const getPriorityLabel = (priority) => {
        const labels = {
            'low': 'Niski',
            'medium': 'Średni',
            'high': 'Wysoki',
            'critical': 'Krytyczny'
        };
        return labels[priority] || priority;
    };

    /**
     * Translate category codes to readable Polish labels
     */
    const getCategoryLabel = (category) => {
        const labels = {
            'hardware': 'Sprzęt',
            'software': 'Oprogramowanie',
            'network': 'Sieć',
            'account': 'Konto',
            'other': 'Inne'
        };
        return labels[category] || category;
    };

    /**
     * Initialize the status distribution chart
     */
    const initStatusChart = (chartData) => {
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        
        // Extra detailed debug output for troubleshooting
        console.log("Chart data for status:", chartData.tickets);
        console.log("Unresolved tickets count:", chartData.tickets.unresolved);
        
        const statusData = {
            labels: ['Nowe', 'W trakcie', 'Nierozwiązane', 'Rozwiązane', 'Zamknięte'],
            datasets: [{
                data: [
                    chartData.tickets.new,
                    chartData.tickets.inProgress,
                    chartData.tickets.unresolved,
                    chartData.tickets.resolved,
                    chartData.tickets.closed
                ],
                backgroundColor: colorSchemes.status.backgroundColor,
                borderColor: colorSchemes.status.borderColor,
                borderWidth: colorSchemes.status.borderWidth
            }]
        };
        
        // Debug the final data that goes into the chart
        console.log("Final chart data:", statusData);
        
        return new Chart(statusCtx, {
            type: 'doughnut',
            data: statusData,
            options: {
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    };

    /**
     * Initialize the priority distribution chart
     */
    const initPriorityChart = (chartData) => {
        const priorityCtx = document.getElementById('priorityChart').getContext('2d');
        
        // Define priority order to match the color scheme
        const priorityOrder = ['low', 'medium', 'high', 'critical'];
        
        // Group and sort data according to priority order
        let priorityMap = {};
        chartData.priorityDistribution.forEach(item => {
            priorityMap[item.priority] = item.count;
        });
        
        // Transform data for the chart (in correct order)
        const priorityLabels = [];
        const priorityValues = [];
        const priorityColors = [];
        
        priorityOrder.forEach((priority, index) => {
            if (priorityMap[priority] !== undefined) {
                priorityLabels.push(getPriorityLabel(priority));
                priorityValues.push(priorityMap[priority]);
                priorityColors.push(colorSchemes.priority.backgroundColor[index]);
            }
        });

        const priorityData = {
            labels: priorityLabels,
            datasets: [{
                data: priorityValues,
                backgroundColor: priorityColors,
                borderColor: colorSchemes.priority.borderColor,
                borderWidth: colorSchemes.priority.borderWidth
            }]
        };
        
        return new Chart(priorityCtx, {
            type: 'pie',
            data: priorityData,
            options: {
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    };

    /**
     * Initialize the category distribution chart
     */
    const initCategoryChart = (chartData) => {
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        
        // Transform data for the chart
        const categoryLabels = [];
        const categoryValues = [];
        
        chartData.categoryDistribution.forEach(item => {
            categoryLabels.push(getCategoryLabel(item.category));
            categoryValues.push(item.count);
        });

        const categoryData = {
            labels: categoryLabels,
            datasets: [{
                data: categoryValues,
                backgroundColor: colorSchemes.category.backgroundColor.slice(0, categoryLabels.length),
                borderColor: colorSchemes.category.borderColor,
                borderWidth: colorSchemes.category.borderWidth
            }]
        };
        
        return new Chart(categoryCtx, {
            type: 'pie',
            data: categoryData,
            options: {
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    };

    /**
     * Initialize the timeline chart
     */
    const initTimelineChart = (chartData) => {
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        
        // Transform data for the chart
        const labels = [];
        const values = [];
        
        chartData.ticketsByDate.forEach(item => {
            labels.push(formatDate(item.date, chartData.period));
            values.push(item.count);
        });
        
        const timelineData = {
            labels: labels,
            datasets: [{
                label: 'Liczba zgłoszeń',
                data: values,
                borderColor: colorSchemes.timeline.borderColor,
                backgroundColor: colorSchemes.timeline.backgroundColor,
                pointBackgroundColor: colorSchemes.timeline.pointBackgroundColor,
                pointBorderColor: colorSchemes.timeline.pointBorderColor,
                pointRadius: colorSchemes.timeline.pointRadius,
                fill: true,
                tension: 0.3
            }]
        };
        
        return new Chart(timelineCtx, {
            type: 'line',
            data: timelineData,
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                return `Zgłoszeń: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
    };

    /**
     * Update period-dependent form fields
     */
    const updateDateFields = (period) => {
        const today = new Date();
        let dateFrom = document.getElementById('date_from');
        let dateTo = document.getElementById('date_to');
        
        // Format date as YYYY-MM-DD
        const formatDateInput = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        
        switch (period) {
            case 'day':
                dateFrom.value = formatDateInput(today);
                dateTo.value = formatDateInput(today);
                break;
            case 'week': {
                // Get first day of current week (Monday)
                const firstDay = new Date(today);
                const dayOfWeek = today.getDay() || 7; // Make Sunday = 7
                firstDay.setDate(today.getDate() - dayOfWeek + 1);
                
                // Get last day of current week (Sunday)
                const lastDay = new Date(firstDay);
                lastDay.setDate(firstDay.getDate() + 6);
                
                dateFrom.value = formatDateInput(firstDay);
                dateTo.value = formatDateInput(lastDay);
                break;
            }
            case 'month': {
                // First day of current month
                const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
                
                // Last day of current month
                const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
                
                dateFrom.value = formatDateInput(firstDay);
                dateTo.value = formatDateInput(lastDay);
                break;
            }
            case 'year': {
                // First day of current year
                const firstDay = new Date(today.getFullYear(), 0, 1);
                
                // Last day of current year
                const lastDay = new Date(today.getFullYear(), 11, 31);
                
                dateFrom.value = formatDateInput(firstDay);
                dateTo.value = formatDateInput(lastDay);
                break;
            }
        }
    };

    /**
     * Handle generating statistics report
     */
    const handleGenerateReport = () => {
        const reportBtn = document.getElementById('generateReportBtn');
        const statusDiv = document.getElementById('reportStatus');
        
        if (!reportBtn || !statusDiv) return;
        
        reportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Show format selection modal first
            showReportFormatModal();
        });
    };
    
    /**
     * Show modal for report format selection
     */
    const showReportFormatModal = () => {
        // Create modal HTML
        const modalHtml = `
            <div class="modal fade" id="reportFormatModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Wybierz format raportu</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="reportFormat" id="formatExcel" value="xlsx" checked>
                                <label class="form-check-label" for="formatExcel">
                                    <i class="fas fa-file-excel text-success"></i> Excel (.xlsx) - Zalecany
                                </label>
                                <small class="form-text text-muted d-block">Plik Excel z formatowaniem i wykresami</small>
                            </div>
                            <div class="form-check mt-3">
                                <input class="form-check-input" type="radio" name="reportFormat" id="formatCsv" value="csv">
                                <label class="form-check-label" for="formatCsv">
                                    <i class="fas fa-file-csv text-info"></i> CSV (.csv)
                                </label>
                                <small class="form-text text-muted d-block">Plik CSV do importu w innych aplikacjach</small>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
                            <button type="button" class="btn btn-primary" id="confirmGenerateReport">
                                <i class="fas fa-download"></i> Generuj i pobierz
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if present
        const existingModal = document.getElementById('reportFormatModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('reportFormatModal'));
        modal.show();
        
        // Handle confirm button
        document.getElementById('confirmGenerateReport').addEventListener('click', function() {
            const selectedFormat = document.querySelector('input[name="reportFormat"]:checked').value;
            modal.hide();
            generateReport(selectedFormat);
        });
    };
    
    /**
     * Generate and download report
     */
    const generateReport = (format) => {
        const reportBtn = document.getElementById('generateReportBtn');
        const statusDiv = document.getElementById('reportStatus');
        
        // Show loading state
        reportBtn.disabled = true;
        reportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generowanie...';
        statusDiv.innerHTML = `<i class="fas fa-info-circle"></i> Generowanie raportu ${format.toUpperCase()}, proszę czekać...`;
        statusDiv.className = 'mt-3 text-info';
        
        // Get filter values
        const period = document.getElementById('period').value;
        const dateFrom = document.getElementById('date_from').value;
        const dateTo = document.getElementById('date_to').value;
        const organization = document.getElementById('organization').value;
        const agent = document.getElementById('agent').value;
        
        console.log('Report generation parameters:', {
            period, dateFrom, dateTo, organization, agent, format
        });
        
        // Validate required fields
        if (!dateFrom || !dateTo) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Błąd: Wymagane są daty początkowa i końcowa';
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-file-export"></i> Wygeneruj raport z aktualnych filtrów';
            return;
        }
        
        // Validate date range
        if (new Date(dateFrom) > new Date(dateTo)) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Błąd: Data początkowa nie może być późniejsza niż końcowa';
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-file-export"></i> Wygeneruj raport z aktualnych filtrów';
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        if (!csrfToken) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Błąd: Brak tokenu CSRF. Odśwież stronę i spróbuj ponownie.';
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-file-export"></i> Wygeneruj raport z aktualnych filtrów';
            return;
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('period_type', period);
        formData.append('period_start', dateFrom);
        formData.append('period_end', dateTo);
        formData.append('format', format);
        if (organization) formData.append('organization', organization);
        if (agent) formData.append('agent', agent);
        
        console.log('Sending request to /statistics/generate-report/ with data:', {
            period_type: period,
            period_start: dateFrom,
            period_end: dateTo,
            format: format,
            organization: organization || 'none',
            agent: agent || 'none'
        });
        
        // Send request with timeout
        const timeoutId = setTimeout(() => {
            statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Ostrzeżenie: Generowanie raportu trwa dłużej niż oczekiwano. Proszę czekać...';
            statusDiv.className = 'mt-3 text-warning';
        }, 10000); // Show warning after 10 seconds
        
        fetch('/statistics/generate-report/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            clearTimeout(timeoutId);
            console.log('Response status:', response.status);
            console.log('Response headers:', [...response.headers.entries()]);
            console.log('Response ok:', response.ok);
            
            // Always get the response as a blob first
            return response.blob().then(blob => {
                const contentType = response.headers.get('content-type');
                const contentDisposition = response.headers.get('content-disposition');
                
                console.log('Content-Type:', contentType);
                console.log('Content-Disposition:', contentDisposition);
                console.log('Blob size:', blob.size);
                console.log('Blob type:', blob.type);
                
                if (!response.ok) {
                    // For error responses, try to read the blob as text to get error message
                    return blob.text().then(text => {
                        console.error('Server error response:', text);
                        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                        
                        try {
                            const errorData = JSON.parse(text);
                            if (errorData.message) {
                                errorMessage = errorData.message;
                            }
                        } catch (e) {
                            if (text && text.length > 0) {
                                errorMessage = text.substring(0, 200) + (text.length > 200 ? '...' : '');
                            }
                        }
                        
                        throw new Error(errorMessage);
                    });
                }
                
                // Check if this is an error response disguised as a successful response
                if (contentType && contentType.includes('application/json')) {
                    // It's a JSON error response
                    return blob.text().then(text => {
                        try {
                            const errorData = JSON.parse(text);
                            console.error('Server returned JSON error:', errorData);
                            throw new Error(errorData.message || 'Unknown server error');
                        } catch (parseError) {
                            console.error('Error parsing JSON response:', parseError);
                            throw new Error('Invalid JSON response from server');
                        }
                    });
                }
                
                // Check if blob is empty
                if (blob.size === 0) {
                    throw new Error('Otrzymano pusty plik');
                }
                
                // Check for file download indicators
                const isExcelFile = contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
                const isCsvFile = contentType && (contentType.includes('text/csv') || contentType.includes('application/csv'));
                const hasAttachmentHeader = contentDisposition && contentDisposition.includes('attachment');
                
                // If it's clearly a file download OR we have attachment header, proceed with download
                if (isExcelFile || isCsvFile || hasAttachmentHeader || blob.size > 1000) {
                    // Extract filename from Content-Disposition header
                    let filename = `raport_statystyk_${dateFrom}_${dateTo}.${format}`;
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                        if (filenameMatch && filenameMatch[1]) {
                            filename = filenameMatch[1].replace(/['"]/g, '');
                        }
                    }
                    
                    console.log('Downloading file:', filename);
                    
                    // Create download link
                    try {
                        // Create a new blob with the correct MIME type if needed
                        let downloadBlob = blob;
                        if (format === 'xlsx' && !blob.type.includes('spreadsheet')) {
                            downloadBlob = new Blob([blob], { 
                                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
                            });
                        } else if (format === 'csv' && !blob.type.includes('csv')) {
                            downloadBlob = new Blob([blob], { 
                                type: 'text/csv' 
                            });
                        }
                        
                        const url = window.URL.createObjectURL(downloadBlob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        
                        // Clean up
                        setTimeout(() => {
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                        }, 100);
                        
                        console.log('File download triggered successfully');
                        return { success: true, filename: filename };
                    } catch (downloadError) {
                        console.error('Error creating download:', downloadError);
                        throw new Error(`Błąd pobierania pliku: ${downloadError.message}`);
                    }
                } else {
                    // Unknown response type, try to read as text for debugging
                    return blob.text().then(text => {
                        console.error('Unexpected response - not a file download');
                        console.error('Response text (first 500 chars):', text.substring(0, 500));
                        
                        // Last resort: if it looks like binary data, try to download it anyway
                        if (text.charCodeAt(0) === 0x50 && text.charCodeAt(1) === 0x4B) {
                            console.log('Detected ZIP/Excel magic bytes, forcing download');
                            const binaryBlob = new Blob([blob], { 
                                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
                            });
                            
                            const filename = `raport_statystyk_${dateFrom}_${dateTo}.${format}`;
                            const url = window.URL.createObjectURL(binaryBlob);
                            const a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = url;
                            a.download = filename;
                            document.body.appendChild(a);
                            a.click();
                            
                            setTimeout(() => {
                                window.URL.revokeObjectURL(url);
                                document.body.removeChild(a);
                            }, 100);
                            
                            return { success: true, filename: filename };
                        } else {
                            throw new Error(`Nieoczekiwany typ odpowiedzi. Sprawdź logi serwera.`);
                        }
                    });
                }
            });
        })
        .then(result => {
            if (result && result.success) {
                statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Raport został wygenerowany i pobrany: ${result.filename}`;
                statusDiv.className = 'mt-3 text-success';
                console.log('Report generation successful:', result.filename);
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error generating report:', error);
            
            let errorMessage = error.message || 'Nieznany błąd';
            
            // Add specific error details for debugging
            if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                errorMessage += ' (Błąd połączenia sieciowego)';
            } else if (error.message.includes('timeout')) {
                errorMessage += ' (Przekroczono limit czasu)';
            } else if (error.message.includes('SyntaxError')) {
                errorMessage = 'Błąd przetwarzania odpowiedzi serwera. Sprawdź format pliku.';
            }
            
            statusDiv.innerHTML = `
                <i class="fas fa-times-circle"></i> Błąd: ${errorMessage}
                <br><small class="text-muted">
                    Sprawdź konsolę przeglądarki (F12) aby uzyskać więcej informacji.
                    Jeśli problem się powtarza, skontaktuj się z administratorem.
                </small>
            `;
            statusDiv.className = 'mt-3 text-danger';
        })
        .finally(() => {
            // Reset button state
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-file-export"></i> Wygeneruj raport z aktualnych filtrów';
        });
    };
    
    // Initialize all charts with data from the DOM
    const initializeAllCharts = () => {
        const chartData = getChartData();
        
        // Initialize charts
        const charts = {
            statusChart: initStatusChart(chartData),
            priorityChart: initPriorityChart(chartData),
            categoryChart: initCategoryChart(chartData),
            timelineChart: initTimelineChart(chartData)
        };
        
        return charts;
    };
    
    // Initialize event handlers for the filter form
    const initializeEventHandlers = () => {
        // Period selector changes date ranges
        const periodSelector = document.getElementById('period');
        if (periodSelector) {
            periodSelector.addEventListener('change', function() {
                updateDateFields(this.value);
            });
        }
        
        // Handle report generation
        handleGenerateReport();
        
        // Handle organization report generation
        const orgReportBtn = document.getElementById('generateOrganizationReportBtn');
        if (orgReportBtn) {
            orgReportBtn.addEventListener('click', function() {
                generateOrganizationReport();
            });
        }
    };
    
    /**
     * Generate organization time report
     */
    const generateOrganizationReport = () => {
        const reportBtn = document.getElementById('generateOrganizationReportBtn');
        const statusDiv = document.getElementById('reportStatus');
        
        // Show loading state
        reportBtn.disabled = true;
        reportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generowanie...';
        statusDiv.innerHTML = '<i class="fas fa-info-circle"></i> Generowanie raportu organizacji, proszę czekać...';
        statusDiv.className = 'mt-3 text-info';
        
        // Get filter values
        const dateFrom = document.getElementById('date_from').value;
        const dateTo = document.getElementById('date_to').value;
        
        // Validate required fields
        if (!dateFrom || !dateTo) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Błąd: Wymagane są daty początkowa i końcowa';
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-building"></i> Raport czasów organizacji';
            return;
        }
        
        // Validate date range
        if (new Date(dateFrom) > new Date(dateTo)) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Błąd: Data początkowa nie może być późniejsza niż końcowa';
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-building"></i> Raport czasów organizacji';
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        if (!csrfToken) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Błąd: Brak tokenu CSRF. Odśwież stronę i spróbuj ponownie.';
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-building"></i> Raport czasów organizacji';
            return;
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('period_start', dateFrom);
        formData.append('period_end', dateTo);
        formData.append('format', 'xlsx');
        
        // Send request
        fetch('/statistics/organization-time-report/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Błąd serwera');
                });
            }
            
            // Get filename from Content-Disposition header
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'raport_organizacji.xlsx';
            if (disposition && disposition.includes('filename=')) {
                const filenameMatch = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }
            
            return response.blob().then(blob => ({ blob, filename }));
        })
        .then(({ blob, filename }) => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Show success message
            statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Raport został wygenerowany i pobrany!';
            statusDiv.className = 'mt-3 text-success';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-building"></i> Raport czasów organizacji';
        })
        .catch(error => {
            console.error('Report generation error:', error);
            statusDiv.innerHTML = `<i class="fas fa-times-circle"></i> Błąd: ${error.message}`;
            statusDiv.className = 'mt-3 text-danger';
            reportBtn.disabled = false;
            reportBtn.innerHTML = '<i class="fas fa-building"></i> Raport czasów organizacji';
        });
    };
    
    // Initialize everything
    const charts = initializeAllCharts();
    initializeEventHandlers();
    
    // Make charts available globally for debugging
    window.statsCharts = charts;
});
