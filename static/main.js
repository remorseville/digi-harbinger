

function removeLastColumn() {
  var allRows = document.getElementById('results-table').rows;
 for (var i=0; i< allRows.length; i++) {
   allRows[i].deleteCell(-1);
 }
}

window.addEventListener("load", (event) => {
  removeLastColumn();
  const elementToWrap = document.getElementById('title');
  const newDiv = document.createElement('div');
  elementToWrap.parentNode.insertBefore(newDiv, elementToWrap);

  const link = document.createElement('a');
  newDiv.appendChild(link);
  newDiv.appendChild(elementToWrap);
  link.setAttribute('id', 'home-link'); // Set an ID
  link.setAttribute('href', './');
  link.setAttribute('z-index', '10');
  link.innerHTML = "Return to Home";


  newDiv.setAttribute('id', 'title-bar-div2'); // Set an ID
  newDiv.setAttribute('class', 'title-bar'); // Add a class
});
