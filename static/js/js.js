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
$(document).ready(function() {
  $('.an13').click(function() {
      $('.an14').hide();
      $(this).show();
  });
}
);
function clickAn15() {
  var anElement15 = document.querySelector('.an15');
  if (anElement15.style.display === 'none') {
    anElement15.style.display = 'block';
  } else {
    anElement15.style.display = 'none';
  }
}
tinymce.init({
  selector: '#myTextarea',
  height: 351,
  plugins: 'ai tinycomments mentions anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount checklist mediaembed casechange export formatpainter pageembed permanentpen footnotes advtemplate advtable advcode editimage tableofcontents mergetags powerpaste tinymcespellchecker autocorrect a11ychecker typography inlinecss',
  toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table mergetags | align lineheight | tinycomments | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
});
// Initialize chat functionality
$(document).ready(function() {
  var socket = io.connect('http://127.0.0.1:5000');
  var $messages = $('#messages');
  var $inputMessage = $('#input-message');

  $('#chat-icon').click(function(event) {
    event.preventDefault();
    $('#chat-container').toggle();
  });

  var currentUserId = null;
  var messagesCache = {};

  function startChat(userId) {
    // Clear the current messages
    $messages.empty();

    // Load the messages for the selected user
    if (messagesCache[userId]) {

    messagesCache[userId].forEach(message => {
      var messageType = message.sender_id === 1 ? 'admin' : 'user'; // Determine the type of message based on sender_id
      var messageContent = messageType === 'admin' ? $('#myName').text() + ': ' + message.text : message.text;
      var messageElement = $('<li class="message ' + messageType + '"><div class="message-content">' + messageContent + '</div></li>');
      $messages.append(messageElement);
    });
  } else {
    // Load the messages for the selected user
    fetch(`/api/messages?userId=${userId}`)
      .then(response => response.json())
      .then(messages => {
        // Cache and display the messages
        messagesCache[userId] = messages;
        messages.forEach(message => {
          var messageType = message.sender_id === 1 ? 'admin' : 'user'; // Determine the type of message based on sender_id
          var messageContent = messageType === 'admin' ? $('#myName').text() + ': ' + message.text : message.text;
          var messageElement = $('<li class="message ' + messageType + '"><div class="message-content">' + messageContent + '</div></li>');
          $messages.append(messageElement);
        });
      });
  }

    // Update the current user ID
    currentUserId = userId;
  }

  // When sending a message, use the current user ID
  $('#send-button').click(function(e) {
    e.preventDefault();
    var messageText = $('#input-message').val().trim();
    if (messageText) {
      var isAdmin = true; // Set this value based on the current user
      var messageType = isAdmin ? 'admin-message' : 'user-message';
      var messageElement = $('<p class="' + messageType + '">' + messageText + '</p>');
      $messages.append(messageElement);
      $('#input-message').val(''); // Clear the input box after sending the message

      socket.emit('broadcast_message', {
        sender_id: 1, // ID of the admin
        receiver_id: currentUserId, // ID of the selected user
        text: messageText,
        type: messageType // Add the type of message to the data sent to the server
      });
      if (!messagesCache[currentUserId]) {
        messagesCache[currentUserId] = [];
      }
      messagesCache[currentUserId].push({
        sender_id: 1,
        text: messageText,
        type: messageType
      });
    }
  });

  socket.on('receive_message', function(msg) {
    console.log("Message received", msg);
    var messageType = msg.sender_id === 1 ? 'admin' : 'user';
    var messageElement = $('<li class="message ' + messageType + '"><div class="message-content">' + msg.text + '</div></li>');
    $messages.append(messageElement);
    scrollToBottom();
  });


  function scrollToBottom() {
    $messages.scrollTop($messages[0].scrollHeight);
  }

  function loadContactList() {
    fetch('/get-contact-list')
      .then(response => response.json())
      .then(data => {
        let contactList = $('#contact-list');
        contactList.empty();
        data.forEach(contact => {
          if(contact.username !== 'admin') {
            let contactElement = $('<div>').text(contact.username);
            contactList.append(contactElement);
          }
        });
      });
  }

  window.onload = function() {
    fetch('/get-contact-list')
      .then(response => response.json())
      .then(users => {
        const contactList = $('#contact-list');
        users.forEach(user => {
          if(user.username !== 'admin') {
            const userElement = $('<div>').text(user.username).addClass('contact');
            userElement.click(function() {
              startChat(user.id);
            });
            contactList.append(userElement);
          }
        });
      });
  };
});