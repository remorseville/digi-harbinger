document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const intervalInput = document.getElementById('interval');
    const repetitionsInput = document.getElementById('repetitions');
    const statusDisplay = document.getElementsByClassName('statusDisplay');
    
    
    let statusCheckInterval;
    
    startBtn.addEventListener('click', startScheduler);
    stopBtn.addEventListener('click', stopScheduler);
    
    
    function startScheduler() {
        const interval = parseInt(intervalInput.value);
        const repetitions = parseInt(repetitionsInput.value);

        const tabcontent = document.getElementsByClassName("tabcontent");

        let activeTab = Array.from(tabcontent).find(el => 
            window.getComputedStyle(el).display !== 'none'
        );
        
        let form;
        let checkboxes;
        let selectedTests;

        switch (activeTab.id) {
            case "CIS":
               form = document.getElementById('cis_testForm');
	           checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#cis_selectAll)');
	           selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);
               if (checkboxes.length !== 0) {

                break;
               } else {
                alert('No tests selected!');
                return;
               }
            case "CC_US":
              form = document.getElementById('testForm');
	           checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#selectAll)');
	           selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);
               if (checkboxes.length !== 0) {

                break;
               } else {
                alert('No tests selected!');
                return;
               }
           
            case "CC_EU":
              form = document.getElementById('eu_testForm');
	           checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#eu_selectAll)');
	           selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);
               if (checkboxes.length !== 0) {

                break;
               } else {
                alert('No tests selected!');
                return;
               }
            default:
              null;
          }

        fetch('/start-tests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interval: interval,
                repetitions: repetitions, 
                selected_tests: selectedTests,
                region: activeTab.id
            })
        })
        .then(response => response.json())
        .then(data => {
            updateStatus(data.status);
            startBtn.disabled = true;
            stopBtn.disabled = false; 
            startStatusPolling();  
            
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
            
            notifications.hideStatusBanner();
        });
    }


    function formatDurationCompact(seconds) {
        if (seconds < 60) {
            return seconds + "s";
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return minutes + "m" + (remainingSeconds > 0 ? " " + remainingSeconds + "s" : "");
        }
    }
    
    let count = 0
    function updateStatus(status) {
        if (status.running) {
            const nextRun = status.next_run; //? new Date(status.next_run).toLocaleTimeString() : 'N/A';
            const nextRunTime = status.next_run_time ? new Date(status.next_run_time).toLocaleTimeString() : "N/A";
            for (let i = 0; i < statusDisplay.length; i++) {
                statusDisplay[i].classList.remove('fail-status');
                statusDisplay[i].classList.add('success-status');
                statusDisplay[i].innerHTML = `<strong>Running</strong>`;
              }
            
            if (nextRun === 0){ 
                
                if (count > 2){
                    count = 0
                }
                let array = ["Processing.", "Processing..", "Processing..."]
                
                notifications.updateStatusBanner(`
                    Run: ${status.current_iteration}/${status.total_iterations} ${array[count]}
    
                `, 'info');
                count = count +1
            } else {
                let time = formatDurationCompact(nextRun)
                notifications.updateStatusBanner(`
                    Run: ${status.current_iteration}/${status.total_iterations} Next Run: ${nextRunTime}  (${time})
    
                `, 'info');
            }
    
        } else {

            for (let i = 0; i < statusDisplay.length; i++) {
                statusDisplay[i].innerHTML = `Not running`;
                statusDisplay[i].classList.remove('success-status');
                statusDisplay[i].classList.add('fail-status');
              }
            startBtn.disabled = false;
            stopBtn.disabled = true;
            notifications.hideStatusBanner();
        }
    }
    
    function startStatusPolling() {
        let notificationShown = false;
        let wasEverRunning = false;  // Track if it was ever running
        
        statusCheckInterval = setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateStatus(data);
                    if (data.running === true) {
                        wasEverRunning = true;  // Mark as running at least once
                    }
                    
                    if (data.running === false && !notificationShown && wasEverRunning) {
                        notifications.show("All Finished!", "info");
                        notificationShown = true;
                        clearInterval(statusCheckInterval);
                        repetitions = 0;
                    }
                });
        }, 1000);
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
    startStatusPolling();
});

