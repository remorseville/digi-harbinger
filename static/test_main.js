
/** 
Keypair Gen Handling

	Fetch request to flask endpoint, creating a key and CSR. No parameters used.
	Returns PEM text to display on "CSR/Key" tab within app

*/ 
document.getElementById('gen_keypair_button').addEventListener('click', function() {
    fetch('/keypair')
        .then(response => response.json())
        .then(data => {
            document.getElementById('csr_result').value = data.csr;
            document.getElementById('key_result').value = data.key;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('csr_result').value = 'Failed to fetch data.';
            document.getElementById('key_result').value = 'Failed to fetch data.';
        });
        });


/** 
API Key Submission Handling

	Fetch request to flask endpoint, saving submitted API key. Used for CCUS, CCEU and CIS tabs. 
	3 version below. One for each API.
	
*/
document.getElementById('api_key_us_form').addEventListener('submit', function(event) {
	event.preventDefault();
	const apiKey = document.getElementById('api_key_us').value;

	fetch('/submit_?id=api_key_us', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				api_key: apiKey
			}),
		})
		.then(response => response.json())
		.then(data => {
			console.log("Server response:", data);
			alert("API Key Submitted Successfully!");
			window.location.reload();
		})
		.catch(error => {
			console.error("Error:", error);
			alert("An error occurred while. Try again.");
		});
});


document.getElementById('api_key_eu_form').addEventListener('submit', function(event) {
	event.preventDefault();
	const apiKey = document.getElementById('api_key_eu').value;

	fetch('/submit_?id=api_key_eu', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				api_key: apiKey
			}),
		})
		.then(response => response.json())
		.then(data => {
			console.log("Server response:", data);
			alert("API Key Submitted Successfully!");
			window.location.reload();
		})
		.catch(error => {
			console.error("Error:", error);
			alert("An error occurred while. Try again.");
		});
});


document.getElementById('api_key_cis_form').addEventListener('submit', function(event) {
	event.preventDefault();
	const apiKey = document.getElementById('api_key_cis').value;

	fetch('/submit_?id=api_key_cis', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				api_key: apiKey
			}),
		})
		.then(response => response.json())
		.then(data => {
			console.log("Server response:", data);
			alert("API Key Submitted Successfully!");
			window.location.reload();
		})
		.catch(error => {
			console.error("Error:", error);
			alert("An error occurred while. Try again.");
		});
});


/**
Loading Overlay Configurations
	
*/
var configs = {
	"overlayBackgroundColor": "#2d2d2d",
	"overlayOpacity": 0.4,
	"spinnerIcon": "timer",
	"spinnerColor": "#1976d2",
	"spinnerSize": "2x",
	"overlayIDName": "overlay",
	"spinnerIDName": "spinner",
	"offsetX": 0,
	"offsetY": 0,
	"containerID": null,
	"lockScroll": false,
	"overlayZIndex": 9998,
	"spinnerZIndex": 9999
};

function loading() {
	JsLoadingOverlay.show(configs);
}



/**
On-Load Windows Function

	1. Add the overlay and removes after a few seconds.
	2. fetchDirectory is what populates the files shows on the reports tab.
	3. updateOutput is our notication listener
	4. Lister for the test scheduler button. 

*/
window.onload = function() {
    loading();
    setTimeout(function(){JsLoadingOverlay.hide();},1000);
    fetchDirectory();
	setInterval(fetchDirectory, 30000);

	updateOutput();
	setInterval(updateOutput, 1000);
	

	var coll = document.getElementsByClassName("collapsible");
	var i;

	for (i = 0; i < coll.length; i++) {
		coll[i].addEventListener("click", function() {
			this.classList.toggle("active");
			var content = this.nextElementSibling;
			if (content.style.maxHeight) {
				content.style.maxHeight = null;
			} else {
				content.style.maxHeight = content.scrollHeight + "px";
			}
		});
	}
};



/**
Page Reload Event Listener

	If the page is reloaded, the overlay is removed

*/
window.addEventListener('pageshow', function(event) {
	if (event.persisted) {
		location.reload()
		JsLoadingOverlay.hide();
	}
});


/**
Form Handling - User Tests

	For the CCUS and CCEU tabs. There's certain testing scenario's where if one is ran, another needs to be included. 
	"add user" and "delete user" is a prime example. If we create a user, we're deleting it right after.
	2 versions below for CCUS and CCEU APIs'
*/
// US
const selectAddUser = document.getElementById('test_add_user');
const selectDeleteUser = document.getElementById('test_delete_user');

selectAddUser.addEventListener('change', function() {
		if (!this.checked) {
			selectDeleteUser.checked = false;
		} else {
			selectDeleteUser.checked = true;
		}
});

selectDeleteUser.addEventListener('change', function() {
		if (!this.checked) {
			selectAddUser.checked = false;
		} else {
			selectAddUser.checked = true;
		}
});

// EU
const selectAddUser_EU = document.getElementById('eu_test_add_user');
const selectDeleteUser_EU = document.getElementById('eu_test_delete_user');

selectAddUser_EU.addEventListener('change', function() {
		if (!this.checked) {
			selectDeleteUser_EU.checked = false;
		} else {
			selectDeleteUser_EU.checked = true;
		}
});

selectDeleteUser_EU.addEventListener('change', function() {
		if (!this.checked) {
			selectAddUser_EU.checked = false;
		} else {
			selectAddUser_EU.checked = true;
		}
});


/**
Form Handling - Select All Feature

	Select all handling for the CCUS, CCEU and CIS forms (tabs)
	3 versions below for CCUS, CCEU and CIS APIs'
*/
// US
const selectAllCheckbox = document.getElementById('selectAll');
const testCheckboxes = document.querySelectorAll('input[name="test"]');

selectAllCheckbox.addEventListener('change', function() {
	testCheckboxes.forEach(checkbox => {
		checkbox.checked = selectAllCheckbox.checked;
	});
});

// EU
const selectAllCheckbox_EU = document.getElementById('eu_selectAll');
const testCheckboxes_EU = document.querySelectorAll('input[name="eu_test"]');

selectAllCheckbox_EU.addEventListener('change', function() {
	testCheckboxes_EU.forEach(checkbox => {
		checkbox.checked = selectAllCheckbox_EU.checked;
	});
});

// CIS
const selectAllCheckbox_CIS = document.getElementById('cis_selectAll');
const testCheckboxes_CIS = document.querySelectorAll('input[name="cis_test"]');

selectAllCheckbox_CIS.addEventListener('change', function() {
	testCheckboxes_CIS.forEach(checkbox => {
		checkbox.checked = selectAllCheckbox_CIS.checked;
	});
});


/**
Form Handling - Select All Unchecked

	Ensure "Select all" is unchecked when any other is unchecked for the CCUS, CCEU and CIS forms (tabs)
	3 versions below for CCUS, CCEU and CIS APIs'
*/
// US
testCheckboxes.forEach(checkbox => {
	checkbox.addEventListener('change', function() {
		if (!this.checked) {
			selectAllCheckbox.checked = false;
		} else {
			const allChecked = Array.from(testCheckboxes).every(cb => cb.checked);
			selectAllCheckbox.checked = allChecked;
		}
	});
});

// EU
testCheckboxes_EU.forEach(checkbox => {
	checkbox.addEventListener('change', function() {
		if (!this.checked) {
			selectAllCheckbox_EU.checked = false;
		} else {
			const allChecked_EU = Array.from(testCheckboxes_EU).every(cb => cb.checked);
			selectAllCheckbox_EU.checked = allChecked_EU;
		}
	});
});

// CIS
testCheckboxes_CIS.forEach(checkbox => {
	checkbox.addEventListener('change', function() {
		if (!this.checked) {
			selectAllCheckbox_CIS.checked = false;
		} else {
			const allChecked_CIS = Array.from(testCheckboxes_CIS).every(cb => cb.checked);
			selectAllCheckbox_CIS.checked = allChecked_CIS;
		}
	});
});


/**
Form Handling - Group Checkbox Event Listener

	Based on the "data-group" attribute that is set when the lists are populated our flask server. 
	Similar to the "add/delete user" tests, if one test is selected, there are others that need to be as well. 
	This is used for org and domain tests.

*/
document.querySelectorAll('input[type="checkbox"][data-group]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const group = this.dataset.group; // get group name
        if (group == "domains" || group == "organizations" || group == "eu_organizations" || group == "eu_domains"){
            const isChecked = this.checked; // get checked state
            // Find all in the same group and check state
            document.querySelectorAll(`input[type="checkbox"][data-group="${group}"]`).forEach(groupCheckbox => {
                groupCheckbox.checked = isChecked;
            });
        };
    });
});


/* ---------- Check if input is blank helper ---------- */
function isInputBlank(inputId) {
	const inputValue = document.getElementById(inputId);
	if (inputValue == null) {
		return true;
	} else if (inputValue.value == "") {
		return true;
	} else {
		return false;
	}
};


/* ---------- Title bar / hud ---------- */
const elementToWrap = document.getElementById('title');
const newDiv = document.createElement('div');
elementToWrap.parentNode.insertBefore(newDiv, elementToWrap);
newDiv.appendChild(elementToWrap);
newDiv.setAttribute('id', 'title-bar-div');
newDiv.setAttribute('class', 'title-bar');



/* ---------- Main ---------- */
async function runTestsUS() {
    let status = document.getElementById('status');
	if (status == null  ) {
		alert("Save ENV variables before you continue.");
	} else {
		let form = document.getElementById('testForm');
		let checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#selectAll)');
		let selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);

		let org_select = document.getElementById('org_dropdown');
		let org_value = org_select.value
		let org = org_select.options[org_select.selectedIndex].text;


		if (checkboxes.length !== 0){
		    let response = await fetch('/report?us_mode=true&org=' + org_value, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_tests: selectedTests
                }),
            })
            .then(loading());

            let response_data = await response.json();
            
            JsLoadingOverlay.hide();
			notifications.show("All Finished!", "passed");
			notifications.show(
				'View your report\n', 
				'info', 
				{ text: `${response_data["report"]}`, url: `/report?id=${response_data["report"]}` }, 
				15000
			);

        } else {
            alert("No tests selected!");
        }
	}
}

async function runTestsEU() {
    let status = document.getElementById('eu_status');
	if (status == null  ) {
		alert("Save ENV variables before you continue.");
	} else {
		let form = document.getElementById('eu_testForm');
		let checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#eu_selectAll)');
		let selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);

		let org_select = document.getElementById('eu_org_dropdown');
		let org_value = org_select.value
		let org = org_select.options[org_select.selectedIndex].text;

		
		if (checkboxes.length !== 0){
		    let response = await fetch('/report?us_mode=false&org=' + org_value, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_tests: selectedTests,
                }),
            })
            .then(loading());

            let response_data = await response.json();
            
            JsLoadingOverlay.hide();
			notifications.show("All Finished!", "passed");
			notifications.show(
				'View your report\n', 
				'info', 
				{ text: `${response_data["report"]}`, url: `/report?id=${response_data["report"]}` }, 
				15000
			);
			

        } else {
            alert("No tests selected!");
        }
	}
}


async function runTestsCIS() {
    let status = document.getElementById('cis_status');
	if (status == null  ) {
		alert("Save ENV variables before you continue.");
	} else {
		let form = document.getElementById('cis_testForm');
		let checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#cis_selectAll)');
		let selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);

		
		if (checkboxes.length !== 0){
		    let response = await fetch('/report?api=cis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_tests: selectedTests,
                }),
            })
            .then(loading());

            let response_data = await response.json();
            
            JsLoadingOverlay.hide();
			notifications.show("All Finished!", "passed");
			notifications.show(
				'View your report\n', 
				'info', 
				{ text: `${response_data["report"]}`, url: `/report?id=${response_data["report"]}` }, 
				15000
			);

        } else {
            alert("No tests selected!");
        }
	}
}





// Tabs Control
function openTab(evt, tabName) {

    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }


 // Fetch Directory Report List

 function fetchDirectory() {
	fetch('/list-directory')
	  .then(response => response.json())
	  .then(data => {
		  const fileListContainer = document.getElementById('file-list');
		  fileListContainer.innerHTML = ''; 
  
		  // error handling
		  if (data.error) {
			  fileListContainer.innerHTML = `<div>${data.error}</div>`;
			  return;
		  }
  
		  // Categorize files by prefix
		  const categorizedFiles = {
			  CCUS: [],
			  CCEU: [],
			  CIS: [],
			  other: []
		  };
  
		  data.files.forEach(file => {
			  if (file.startsWith('CCUS')) {
				  categorizedFiles.CCUS.push(file);
			  } else if (file.startsWith('CCEU')) {
				  categorizedFiles.CCEU.push(file);
			  } else if (file.startsWith('CIS')) {
				  categorizedFiles.CIS.push(file);
			  } else {
				  categorizedFiles.other.push(file);
			  }
		  });
  
		  // Create columns container
		  const columnsContainer = document.createElement('div');
		  columnsContainer.style.display = 'flex';
		  columnsContainer.style.gap = '20px';
		  
		  // Create columns for each category
		  ['CCUS', 'CCEU', 'CIS'].forEach(prefix => {
			  if (categorizedFiles[prefix].length > 0) {
				  const fieldset = document.createElement('fieldset');
				  const legend = document.createElement('legend');
				  legend.innerHTML = prefix

				  const column = document.createElement('div');
				  column.style.flex = '1';
				  
				  //const header = document.createElement('h3');
				  //header.textContent = prefix;
				  //column.appendChild(header);
				  
				  
				  const list = document.createElement('ul');
				  list.style.listStyleType = 'none';
				  list.style.padding = '0';
				  
				  categorizedFiles[prefix].forEach(file => {
					  const listItem = document.createElement('li');
					  const link = document.createElement('a');
					  link.href = `/report?id=${file}`;
					  link.textContent = file;
					  listItem.appendChild(link);
					  list.appendChild(listItem);
				  });
				  
				  column.appendChild(list);
				  fieldset.appendChild(legend);
				  fieldset.appendChild(column);
				  columnsContainer.appendChild(fieldset);
			  }
		  });
  
		  // Add other files if they exist
		  if (categorizedFiles.other.length > 0) {
			  const otherColumn = document.createElement('div');
			  otherColumn.style.flex = '1';
			  
			  const header = document.createElement('h3');
			  header.textContent = 'Other Files';
			  otherColumn.appendChild(header);
			  
			  const list = document.createElement('ul');
			  list.style.listStyleType = 'none';
			  list.style.padding = '0';
			  
			  categorizedFiles.other.forEach(file => {
				  const listItem = document.createElement('li');
				  const link = document.createElement('a');
				  link.href = `/report?id=${file}`;
				  link.textContent = file;
				  listItem.appendChild(link);
				  list.appendChild(listItem);
			  });
			  
			  otherColumn.appendChild(list);
			  columnsContainer.appendChild(otherColumn);
		  }
  
		  fileListContainer.appendChild(columnsContainer);
	  })
	  .catch(error => {
		  console.error('Error fetching directory listing:', error);
		  document.getElementById('file-list').innerHTML = '<div>Failed to load directory listing.</div>';
	  });
  }




async function tlsChecker() {
    const common_name = document.getElementById("tls_check_label_input");
    const tls_div = document.getElementById("tls_check_div");
	const tls_ocsp_check = document.getElementById("tls_ocsp_check").checked;

	loading()

	if (tls_ocsp_check) {
		try {
			const response = await fetch('/ocsp?cn=' + encodeURIComponent(common_name.value), {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' }
			});
			
			if (!response.ok) throw new Error('Network error');
			
			const htmlContent = await response.text();
			tls_div.innerHTML = htmlContent;
			
			// Replace all images with SVGs
			replaceCertificateIcons(tls_div);
			JsLoadingOverlay.hide();
			
		} catch (error) {
			console.error('Error:', error);
			tls_div.innerHTML = '<p>Error loading OCSP information</p>';
			JsLoadingOverlay.hide();
		}

	}
	else {

		try {
			const response = await fetch('/help?cn=' + encodeURIComponent(common_name.value), {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' }
			});
			
			if (!response.ok) throw new Error('Network error');
			
			const htmlContent = await response.text();
			tls_div.innerHTML = htmlContent;
			
			// Replace all images with SVGs
			replaceCertificateIcons(tls_div);
			JsLoadingOverlay.hide();
			
		} catch (error) {
			console.error('Error:', error);
			tls_div.innerHTML = '<p>Error loading TLS information</p>';
			JsLoadingOverlay.hide();
		}
    }
}

function replaceCertificateIcons(container) {
    container.querySelectorAll('img').forEach(img => {
        const icon = document.createElement('span');
        icon.className = 'material-icons cert-icon';
        
        if (img.src.includes('server-cert')) {
            icon.textContent = 'verified_user';
            icon.style.color = '#4CAF50';
        } else if (img.src.includes('intermediate-cert')) {
            icon.textContent = 'security';
            icon.style.color = '#2196F3';
        } else {
            icon.textContent = 'link';
            icon.style.color = '#9E9E9E';
        }
        
        img.replaceWith(icon);
    });
}



/** NEW-ish */


function clearOutput() {

    fetch('/reset')
}


function updateOutput() {
    fetch('/output')
        .then(response => response.text())
        .then(text => {
            // 1. Fix JSON formatting
            const validJsonText = text
                .replace(/'/g, '"') // Replace single quotes
                .replace(/True/g, 'true') // Fix Python booleans
                .replace(/False/g, 'false');

            // 2. Split and parse objects
            const parsedData = validJsonText.split('}{')
                .map((obj, index, arr) => {
                    if (arr.length === 1) return obj;
                    return index === 0 ? obj + '}' :
                        index === arr.length - 1 ? '{' + obj :
                        '{' + obj + '}';
                })
                .map(obj => {
                    try {
                        return JSON.parse(obj);
                    } catch (e) {
                        return null;
                    }
                })
                .filter(Boolean);

            // 3. Filter for "call" phase only
            const callEntries = parsedData.filter(entry => entry.when === 'call');
            fetch('/status')
                .then(response => response.json())
                .then(data => {

                    // 4. Display results
                    if (callEntries.length > 0) {

                        callEntries.map(entry =>
                            notifications.show(data["current_iteration"] + ": " + entry.node, entry.outcome),

                        ).join('');
                    }
                });
            clearOutput();
			


        })
        .catch(error => {
            console.error('Error:', error);
            
        });
}


/* ---------- MODAL ---------- */
var modal = document.getElementById("settingsModal");
var modalContainer = document.getElementById("modalContainer");
var btn = document.getElementById("modalBtn");

// CLOSE ELEMENT
var span = document.getElementsByClassName("close")[0] ;



btn.onclick = function() {
  modal.style.display = "block";
  modalContainer.style.display = "block";
}


// CLOSE FUNCTION
span.onclick = function() {
  modal.style.display = "none";
  modalContainer.style.display = "none";
}
