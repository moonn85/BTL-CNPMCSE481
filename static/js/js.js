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

tinymce.init({
  selector: '#myTextarea',
  height: 351,
  plugins: 'ai tinycomments mentions anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount checklist mediaembed casechange export formatpainter pageembed permanentpen footnotes advtemplate advtable advcode editimage tableofcontents mergetags powerpaste tinymcespellchecker autocorrect a11ychecker typography inlinecss',
  toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table mergetags | align lineheight | tinycomments | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
});