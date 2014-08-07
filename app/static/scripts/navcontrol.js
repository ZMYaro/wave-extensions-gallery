window.addEventListener('load', function () {
	var navButton = document.getElementById('navButton');
	navButton.addEventListener('click', function () {
		document.body.classList.toggle('showNav');
	});
}, false);