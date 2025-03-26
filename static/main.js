
// report.html is generated on the fly by pytesthtml. This removes an annoying column that was not needed.
function removeLastColumn() {
  var allRows = document.getElementById('results-table').rows;
 for (var i=0; i< allRows.length; i++) {
   allRows[i].deleteCell(-1);
 }
}

// Randomizer for report.html <title> elements - See below "ascii_titles"
function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}


// On load listener to process a bunch
window.addEventListener("load", (event) => {
  removeLastColumn();                                     // Removes the last column

  const elementToWrap = document.getElementById('title'); // Creates and inserts a "return to homepage" href on report.html
  const newDiv = document.createElement('div');
  elementToWrap.parentNode.insertBefore(newDiv, elementToWrap);
  const link = document.createElement('a');
  newDiv.appendChild(link);
  newDiv.appendChild(elementToWrap);
  newDiv.setAttribute('id', 'title-bar-div2'); 
  newDiv.setAttribute('class', 'sticky-nav title-bar');
  newDiv.setAttribute('z-index', '20');
  link.setAttribute('id', 'home-link');
  link.setAttribute('href', './');
  link.setAttribute('z-index', '30');
  link.innerHTML = "Return to Home";

  // Insert of favicon to 'report.html'
  document.head.insertAdjacentHTML('beforeend', `
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
  `);
 
  // Random ascii <title> elements for 'report.html'
  const ascii_titles = ["[¬º-°]¬", "(◕ᴥ◕ʋ)", "(⊙_◎)", "ʕっ•ᴥ•ʔっ", "._.)/\\(._.", "(๑•̀ㅂ•́)ง✧", "(っ•́｡•́)♪♬", "(∩｀-´)⊃━☆ﾟ.*･｡ﾟ" ]
  title = document.getElementById('head-title');
  title.innerHTML = getRandomItem(ascii_titles) ;
  
});
