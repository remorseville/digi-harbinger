


// Add an event listener to the button
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

/* ---------- DATA SUBMISSION HANDLER ---------- */
document.getElementById('api_key_us_form').addEventListener('submit', function(event) {
	event.preventDefault();

	// GET FORM DATA
	const apiKey = document.getElementById('api_key_us').value;

	// FETCH REQUEST TO SAVE DATA
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

	// GET FORM DATA
	const apiKey = document.getElementById('api_key_eu').value;

	// FETCH REQUEST TO SAVE DATA
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


// Fetch -  NOT USED
function fetch_status() {
    fetch('/verify', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},

		})
		.then(response => response.json())
		.then(data => {
			console.log("Server response:", data);
		})
		.catch(error => {
			console.error("Error:", error);
			alert("An error occurred while. Try again.");
		});
}


/* ---------- LOADING OVERLAY CONFIGS ---------- */
var configs = {
	"overlayBackgroundColor": "#2d2d2d",
	"overlayOpacity": 0.4,
	"spinnerIcon": "ball-clip-rotate",
	"spinnerColor": "#000",
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


/* ---------- LOADING OVERLAY ---------- */
function loading() {
	JsLoadingOverlay.show(configs);
}

window.onload = function() {
    loading();
    setTimeout(function(){JsLoadingOverlay.hide();},1000);
    fetchDirectory();
};


/* ---------- PAGE RELOAD HANDLER ---------- */
window.addEventListener('pageshow', function(event) {
	if (event.persisted) {
		location.reload()
		JsLoadingOverlay.hide();
	}
});


/* ---------- SELECT ADD_USER AND DELETE_USER TOGETHER ---------- */
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


/* ---------- "SELECT ALL" FUNCTIONALITY ---------- */
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


/* ---------- ENSURE "SELECT ALL" IS UNCHECKED WHEN ANY OTHER IS UNCHECKED ---------- */
// US
testCheckboxes.forEach(checkbox => {
	checkbox.addEventListener('change', function() {
		if (!this.checked) {
			selectAllCheckbox.checked = false;
		} else {
			// OTHERWISE, "CHECK ALL" IF CHECKED
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
			// OTHERWISE, "CHECK ALL" IF CHECKED
			const allChecked_EU = Array.from(testCheckboxes_EU).every(cb => cb.checked);
			selectAllCheckbox_EU.checked = allChecked_EU;
		}
	});
});


/* ---------- ADD EVENT LISTENER - CHECKBOX - BASED ON DATA-GROUP ATTRIBUTE ---------- */
document.querySelectorAll('input[type="checkbox"][data-group]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const group = this.dataset.group; // GET GROUP NAME
        if (group == "domains" || group == "organizations" || group == "eu_organizations" || group == "eu_domains"){
            const isChecked = this.checked; // GET CHECKED STATE

            // FIND ALL IN SAME GROUP AND SET CHECKED STATE
            document.querySelectorAll(`input[type="checkbox"][data-group="${group}"]`).forEach(groupCheckbox => {
                groupCheckbox.checked = isChecked;
            });
        };
    });
});




/* ---------- CHECK IF INPUT IS BLANK HELPER ---------- */
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


/* ---------- TITLE BAR / HUD ---------- */
const elementToWrap = document.getElementById('title');
const newDiv = document.createElement('div');
elementToWrap.parentNode.insertBefore(newDiv, elementToWrap);
newDiv.appendChild(elementToWrap);
newDiv.setAttribute('id', 'title-bar-div');
newDiv.setAttribute('class', 'title-bar');


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

/* ---------- MODAL SVG BUTTON ---------- */
var modalBtnSvg = document.getElementById("modalBtnSvg");
modalBtnSvg.addEventListener('mouseover', function() {
    modalBtnSvg.style.fill = 'black';
 });

modalBtnSvg.addEventListener('mouseout', function() {
    modalBtnSvg.style.fill = 'grey';
});

// CLOSE FUNCTION
span.onclick = function() {
  modal.style.display = "none";
  modalContainer.style.display = "none";
}


/* ---------- MAIN ---------- */
async function runTestsUS() {
    const status = document.getElementById('status');
	if (status == null  ) {
		alert("Save ENV variables before you continue.");
	} else {
		const form = document.getElementById('testForm');
		const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#selectAll)');
		console.log(checkboxes)
		const selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);

		if (checkboxes.length !== 0){
		    const response = await fetch('/report?us_mode=true', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_tests: selectedTests
                }),
            })
            .then(loading());

            const data = await response;
            window.location.replace("../report?sort=original");
            JsLoadingOverlay.hide();

        } else {
            alert("No tests selected!");
        }
	}
}

async function runTestsEU() {
    const status = document.getElementById('eu_status');
	if (status == null  ) {
		alert("Save ENV variables before you continue.");
	} else {
		const form = document.getElementById('eu_testForm');
		const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked:not(#eu_selectAll)');
		console.log(checkboxes)
		const selectedTests = Array.from(checkboxes).map(checkbox => checkbox.value);

		if (checkboxes.length !== 0){
		    const response = await fetch('/report?us_mode=false', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_tests: selectedTests
                }),
            })
            .then(loading());

            const data = await response;
            window.location.replace("../report?sort=original");
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



// TABS CONTROL
function openTab(evt, tabName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }


 // FETCH REPORT DIRECTORY LIST

function fetchDirectory() {
  fetch('/list-directory')
    .then(response => response.json())
    .then(data => {
        const fileList = document.getElementById('file-list');

        // ERROR HANDLING
        if (data.error) {
            fileList.innerHTML = `<li>${data.error}</li>`;
            return;
        }

        // POPULATE CLICKABLE LINKS
        data.files.forEach(file => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = `/report?id=${file}`; // SAVED FILEPATH
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


