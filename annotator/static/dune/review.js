var dropdown = document.querySelector('.dropdown');
dropdown.addEventListener('click', function(event) {
  event.stopPropagation();
  dropdown.classList.toggle('is-active');
});

function last(l){
    return l[l.length - 1];
}
function addAspect(clickedButton) {
	sentence_index = last(clickedButton.id.split("-"))
	document.getElementById("aspect2-" + sentence_index).style="display:block"
	clickedButton.style="display:none"

}
