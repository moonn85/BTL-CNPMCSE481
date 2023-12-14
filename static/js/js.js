function clickAn(clickedElement) {
  var anElement = clickedElement.nextElementSibling;
  if (anElement) {
    anElement.style.display = (anElement.style.display === 'none' ? 'block' : 'none');
  }
}

function clickAn13() {
  var anElement = document.querySelector('.an13');
  if (anElement) {
    anElement.style.display = (anElement.style.display === 'none' ? 'block' : 'none');
  }
}
function clickAn14() {
  var anElement14 = document.querySelector('.an14');
  if (anElement14.style.display === 'none') {
    anElement14.style.display = 'block';
  } else {
    anElement14.style.display = 'none';
  }
}

function clickAn14_s() {
  var anElement14 = document.querySelector('.an14');
  if (anElement14.style.display === 'none') {
    anElement14.style.display = 'block';
  } else {
    anElement14.style.display = 'none';
  }
  var anElement14_s = document.querySelector('.an14_s');
  if (anElement14_s.style.display === 'none') {
    anElement14_s.style.display = 'block';
  } else {
    anElement14_s.style.display = 'none';
  }  
}

tinymce.init({
  selector: '#myTextarea',
  height: 351,
  plugins: 'ai tinycomments mentions anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount checklist mediaembed casechange export formatpainter pageembed permanentpen footnotes advtemplate advtable advcode editimage tableofcontents mergetags powerpaste tinymcespellchecker autocorrect a11ychecker typography inlinecss',
  toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table mergetags | align lineheight | tinycomments | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
});