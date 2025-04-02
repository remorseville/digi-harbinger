document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const intervalInput = document.getElementById('interval');
    const repetitionsInput = document.getElementById('repetitions');
    const statusDisplay = document.getElementById('statusDisplay');
    
    let statusCheckInterval;
    
    startBtn.addEventListener('click', startScheduler);
    stopBtn.addEventListener('click', stopScheduler);
    

    


    
    function startScheduler() {
        const interval = parseInt(intervalInput.value);
        const repetitions = parseInt(repetitionsInput.value);
        const form = document.getElementById('cis_testForm');
	    const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#cis_selectAll)');
	    const selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);
        console.log(selectedTests)
        const fileList = document.getElementById('file-list');
        
        
        fetch('/start-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interval: interval,
                repetitions: repetitions, 
                selected_tests: selectedTests,
            })
        })
        .then(response => response.json())
        .then(data => {
            updateStatus(data.status);
            startBtn.disabled = true;
            stopBtn.disabled = false; 
            startStatusPolling();
            notifications.show(
				'View your report\n', 
				'info', 
				{ text: `ds`, url: `dss` }, 
				60000
			);
        });
    }
    
    function stopScheduler() {
        fetch('/stop', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            updateStatus(data.status);
            startBtn.disabled = false;
            stopBtn.disabled = true;
            stopStatusPolling();
        });
    }
    
    function updateStatus(status) {
        if (status.running) {
            const nextRun = status.next_run; //? new Date(status.next_run).toLocaleTimeString() : 'N/A';
            const nextRunTime = status.next_run_time ? new Date(status.next_run_time).toLocaleTimeString() : "N/A";
            statusDisplay.classList.remove('fail-status');
            statusDisplay.classList.add('success-status');
            statusDisplay.innerHTML = `
                
                    <strong>Running</strong> 
                
            `;
            document.getElementById('output').innerHTML = `
                <strong>Run:</strong> ${status.current_iteration}/${status.total_iterations}

            `;
            
            document.getElementById('next_run').innerHTML = `
                
                <strong>Next Run:</strong> ${nextRunTime}         

            `;
            document.getElementById('next_run_seconds').innerHTML = `
                
                (${nextRun} <strong>Seconds</strong>)

            `;
        } else {
            statusDisplay.innerHTML = `    
                    Not running
            `;
            statusDisplay.classList.remove('success-status');
            statusDisplay.classList.add('fail-status');
            document.getElementById('output').innerHTML = "";
            document.getElementById('next_run').innerHTML = "";
            document.getElementById('next_run_seconds').innerHTML = "";


        }
    }
    
    function startStatusPolling() {
        let notificationShown = false; // Track if notification was shown
        statusCheckInterval = setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateStatus(data);
                    if (data.running === false && !notificationShown) {
                        notifications.show("All Finished!", "info");
                        notificationShown = true; // Mark as shown
                        clearInterval(statusCheckInterval); // Stop polling (optional)
                        repetitions = 0;
                        document.getElementById('output').innerHTML = "";
                    }
                });
        }, 5000);  // Update every 5 seconds
    }
    
    function stopStatusPolling() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }
    }
    
    // Initial status check
    fetch('/status')
        .then(response => response.json())
        .then(updateStatus);
});