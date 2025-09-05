import express from 'express'; //node.js framework
import { createServer } from 'http'; //used to create http server
import { Server } from 'socket.io';//for webSocket server

//for the angular connection
import { dirname } from 'path'; //determine the direct name of current module when using ES module
import path from 'path' //works with file and direct paths
import { fileURLToPath } from 'url';


//Setting up the server
const PORT = process.env.PORT || 3000;
const app = express(); //creates an express application
app.use(express.json()); //middle ware to parse JSON requested bodies
const server = createServer(app);// creates an http server from express app
const __dirname = dirname(fileURLToPath(import.meta.url));// gets the direct. name of current module

/*
  * Once a socket connection has been made and data is being recieved from retico 
  * send that data on to the angular client
  */
app.use(express.static(path.join(__dirname, '../vis_tool_angular_&_node/logger_display')));

app.get('/server_logger', (newMessage) => {
  //send file servers the index.html file for the logger display
  newMessage.sendFile(path.join(__dirname, '../vis_tool_angular_&_node/logger_display/index.html'));
});

//Create a WebSocket server using Socket.io
const nodeServer = new Server(server, {
  cors: {
    origin: "http://localhost:4200",//location of angular app
  }
});

server.listen(PORT, () =>{
  console.log(`node.js server is running on http://localhost:${PORT}`);
});

//handles websocket connections
nodeServer.on('connect', (socket)=>{
  console.log('New user connected');
  
  //listen for messages sent to the websocket event 'server_logger'
  socket.on('server_logger', (newMessage) =>{
    console.log('Recieved log: \n', newMessage);
    nodeServer.emit('server_logger', newMessage);
  });

  //when the server disconnects from user
  socket.on('disconnect', () =>{
    console.log('disconnected from user');
  });
});



