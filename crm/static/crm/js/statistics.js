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

    // Color schemes for consistent visualization
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

        console.log("Ticket data parsed from HTML:", tickets); // Debug output

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
     * Translate status codes to readable Polish labels
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
        
        console.log("Chart data for status:", chartData.tickets); // Debug output
        
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
            
            // Show loading state
            reportBtn.disabled = true;
            reportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generowanie...';
            statusDiv.innerHTML = 'Generowanie raportu, proszę czekać...';
            statusDiv.className = 'mt-3 text-info';
            
            // Get filter values
            const period = document.getElementById('period').value;
            const dateFrom = document.getElementById('date_from').value;
            const dateTo = document.getElementById('date_to').value;
            const organization = document.getElementById('organization').value;
            const agent = document.getElementById('agent').value;
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Create form data
            const formData = new FormData();
            formData.append('period_type', period);
            formData.append('period_start', dateFrom);
            formData.append('period_end', dateTo);
            if (organization) formData.append('organization', organization);
            if (agent) formData.append('agent', agent);
            
            // Send AJAX request
            fetch('/statistics/generate-report/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    statusDiv.innerHTML = `<i class="fas fa-check-circle"></i> Raport został wygenerowany pomyślnie!`;
                    statusDiv.className = 'mt-3 text-success';
                } else {
                    statusDiv.innerHTML = `<i class="fas fa-times-circle"></i> Błąd: ${data.message}`;
                    statusDiv.className = 'mt-3 text-danger';
                }
            })
            .catch(error => {
                statusDiv.innerHTML = `<i class="fas fa-times-circle"></i> Wystąpił błąd podczas generowania raportu.`;
                statusDiv.className = 'mt-3 text-danger';
                console.error('Error generating report:', error);
            })
            .finally(() => {
                // Reset button state
                reportBtn.disabled = false;
                reportBtn.innerHTML = '<i class="fas fa-file-export"></i> Wygeneruj raport z aktualnych filtrów';
            });
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
    };
    
    // Initialize everything
    const charts = initializeAllCharts();
    initializeEventHandlers();
    
    // Make charts available globally for debugging
    window.statsCharts = charts;
});
