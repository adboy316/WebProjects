document.addEventListener('DOMContentLoaded', () => {

  // Connect to websocket
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  // On socket connection
  socket.on('connect', function () {
    /* Update all existing users on connection  */
    socket.emit('user login');
    // * Update all existing channels on connection * /
    socket.emit('update channels')
  });


  /* Event listeneres */

  /*  Form submission emits a "chat message" event */
  $(function () {
    $('#chat').submit(function (e) {
      e.preventDefault(); // prevents page reloading
      const chat_message = $('#m').val();
      var usr = document.querySelector('#messages').dataset.user;
      var chn = document.querySelector('#channel-content').dataset.chan;
      socket.emit('chat message', { 'chat_message': chat_message, 'usr': usr, 'chn': chn });
      $('#m').val('');
      return false;
    });
  });

  /*  Channel creation */
  $(function () {
    $('#channel_form').submit(function (e) {
      e.preventDefault(); // prevents page reloading
      const channel_name = $('#channel_name').val();
      socket.emit('create channel', { 'channel_name': channel_name });
      $('#channel_name').val('');
      return false;
    });
  });




  socket.on('message', function (data) {
    console.log('Incoming message:', data);
  });

  /* Socket handlers */

  /* Responds to user_login socket. Loops through all users and displays them.  */
  socket.on('login success', data => {
    const li = document.createElement('li');
    var all_users = []
    console.log(data);
    for (var key in data) {
      all_users.push(key);
    }

    li.innerHTML = `Users Online: ${all_users}`;
    $("#online_users").html(li)
  });


  /* Responds to update_channels. Displays all channels */
  socket.on('broadcast channels', data => {
    // Clear and Append all channels 
    clearBox("nav");

    for (var key in data) {
      channel_name = key;
      // do something with "key" and "value" variables
      var li = document.createElement('li');
      var newlink = document.createElement('a');
      newlink.setAttribute('href', "#");
      newlink.classList.add("nav-link");
      newlink.setAttribute("id", "nav-link");
      newlink.dataset.page = channel_name;
      newlink.title = channel_name;
      // newlink.onclick= load_page("hey");
      li.appendChild(newlink);
      newlink.innerHTML = channel_name;
      document.querySelector('#nav').append(li);
      //window.location.reload(true);
    }
  });

  /* When a new message is announced, add to the unordered list #messages */
  socket.on('receive message', data => {

    const li = document.createElement('li');
    li.innerHTML = `${data.usr}  : ${data.chat_message}`;
    document.querySelector('#messages').append(li);
  });



  socket.on('update channel data', function (data) {
    console.log('Incoming message:', data); 
    load_page(data);
});

  // socket.on('update channel data', data => {

  //   text_messages = data.all_messages;
  //   console.log(text_messages);
  //   console.log(user + ": " + message)
    
  
  //   clearBox("messages");

  //   for (var i in text_messages) {
      

  //     var user = text_messages[i].user;
  //     var message = text_messages[i].message;
      
  //     const li = document.createElement('li');
  //     li.innerHTML = `${user}  : ${message}`;
  //     document.querySelector('#messages').append(li);
      

     
  //   }

  //   console.log(data.all_messages)
  // });




});



/* Functions */
function clearBox(elementID) {
  document.getElementById(elementID).innerHTML = "";
}

// Renders contents of new page in main view.
function load_page(data) {
  console.log(data.channel_info);
  name = data.channel_info.channel_name;
  const request = new XMLHttpRequest();
  request.open('GET', `/${name}`);
  request.onload = () => {
    const response = request.responseText;
    document.querySelector('#channel-content').innerHTML = response;

    const users_li = document.createElement('li');
    users_li.innerHTML = data.channel_info.users;

    channel_div = document.querySelector('#channel-content')
    channel_div.append(users_li);
    channel_div.dataset.chan = name;
  };
  request.send();
}

function isEmpty(obj) {
  return !obj || Object.keys(obj).length === 0;
}



// // Listen for enter key, and send message when pressed
// function enterKeyListener() {
//   var input = document.getElementById("msg");
//   // Execute a function when the user releases a key on the keyboard
//   input.addEventListener("keyup", function (event) {
//     // Number 13 is the "Enter" key on the keyboard
//     if (event.keyCode === 13) {
//       // Cancel the default action, if needed
//       event.preventDefault();
//       // Trigger the button element with a click
//       document.getElementById("button").click();
//     }
//   });
// }

