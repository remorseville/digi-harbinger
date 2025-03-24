


/* ---------- Keypair Gen Handling  ---------- */
document.getElementById('gen_keypair_button').addEventListener('click', function() {
    // Fetch data from the Flask endpoint
    fetch('/keypair')
        .then(response => response.json())
        .then(data => {
            // Update the text areas with the results
            document.getElementById('csr_result').value = data.csr;
            document.getElementById('key_result').value = data.key;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('csr_result').value = 'Failed to fetch data.';
            document.getElementById('key_result').value = 'Failed to fetch data.';
        });
        });

/* ---------- Data Submission Handling ---------- */
document.getElementById('api_key_us_form').addEventListener('submit', function(event) {
	event.preventDefault();

	// Get form data
	const apiKey = document.getElementById('api_key_us').value;

	// Fetch request to save
	fetch('/submit_?id=api_key_us', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				//org_id: orgId,
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

	// Get form data
	const apiKey = document.getElementById('api_key_eu').value;

	// Fetch request to save
	fetch('/submit_?id=api_key_eu', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				//org_id: orgId,
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



/* ---------- Loading overlay configs ---------- */
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


/* ---------- Loading overlay ---------- */
function loading() {
	JsLoadingOverlay.show(configs);
}

window.onload = function() {
    loading();
    setTimeout(function(){JsLoadingOverlay.hide();},1000);
    fetchDirectory();
};


/* ---------- Page Reload Handler ---------- */
window.addEventListener('pageshow', function(event) {
	if (event.persisted) {
		location.reload()
		JsLoadingOverlay.hide();
	}
});


/* ---------- Select add_user and delete_user together ---------- */
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


/* ---------- "Select All" Functionality ---------- */
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


/* ---------- ensure "Select all" is unchecked when any other is unchecked ---------- */
// US
testCheckboxes.forEach(checkbox => {
	checkbox.addEventListener('change', function() {
		if (!this.checked) {
			selectAllCheckbox.checked = false;
		} else {
			// Otherwise, check all if checked
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
			// Otherwise, check all if checked
			const allChecked_EU = Array.from(testCheckboxes_EU).every(cb => cb.checked);
			selectAllCheckbox_EU.checked = allChecked_EU;
		}
	});
});


/* ---------- add event listener - checkbox - based on data-group attribute ---------- */
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


/* ---------- check if input is blank helper ---------- */
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


/* ---------- title bar / hud ---------- */
const elementToWrap = document.getElementById('title');
const newDiv = document.createElement('div');
elementToWrap.parentNode.insertBefore(newDiv, elementToWrap);
newDiv.appendChild(elementToWrap);
newDiv.setAttribute('id', 'title-bar-div');
newDiv.setAttribute('class', 'title-bar');


/* ---------- modal ---------- */
var modal = document.getElementById("settingsModal");
var modalContainer = document.getElementById("modalContainer");
var btn = document.getElementById("modalBtn");

// CLOSE ELEMENT
var span = document.getElementsByClassName("close")[0] ;


/* ---------- modal svg button ---------- */
var modalBtnSvg = document.getElementById("modalBtnSvg");
modalBtnSvg.addEventListener('mouseover', function() {
    modalBtnSvg.style.fill = 'black';
 });

modalBtnSvg.addEventListener('mouseout', function() {
    modalBtnSvg.style.fill = 'grey';
});

// Close Function
span.onclick = function() {
  modal.style.display = "none";
  modalContainer.style.display = "none";
}


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

            let response_data = await response;
            window.location.href = "/report?sort=original";
            JsLoadingOverlay.hide();

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

            let data = await response;
            window.location.href = "/report?sort=original";
            JsLoadingOverlay.hide();

        } else {
            alert("No tests selected!");
        }
	}
}


function openPage(pageName,elmnt,color) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }
  document.getElementById(pageName).style.display = "block";
  elmnt.style.backgroundColor = color;
}

$('ul li').on('click', function() {
	$('li').removeClass('active');
	$(this).addClass('active');
});



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
        const fileList = document.getElementById('file-list');

        // error handling
        if (data.error) {
            fileList.innerHTML = `<li>${data.error}</li>`;
            return;
        }

        // populate clickable links
        data.files.forEach(file => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = `/report?id=${file}`; // saved filepath
            link.textContent = file;
            listItem.appendChild(link);
            fileList.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error('Error fetching directory listing:', error);
        document.getElementById('file-list').innerHTML = '<li>Failed to load directory listing.</li>';
    });
    }


