#region header

// Arkane.NotificationsWsl.Interface - NotificationSocketListener.cs
// 
// Created by: Alistair J R Young (avatar) at 2022/06/22 12:54 PM.

#endregion

#region using

using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;

#endregion

namespace Arkane.NotificationsWsl.Interface
{
    public static class NotificationSocketListener
    {
        // Thread signal.
        internal static ManualResetEvent allDone = new ManualResetEvent (initialState: false);

        private static Socket? listener;
        private static string  endpointPath = string.Empty;

        public static string EndpointPath { get; } = NotificationSocketListener.endpointPath;

        public static void StartListening ()
        {
            // Establish the local endpoint for the socket.
            NotificationSocketListener.endpointPath =
                Path.Combine (path1: Environment.GetFolderPath (folder: Environment.SpecialFolder.UserProfile),
                              path2: "wslnote.sock");

            var endpoint = new UnixDomainSocketEndPoint (path: NotificationSocketListener.endpointPath);

            // Create a Unix socket.
            NotificationSocketListener.listener = new Socket (addressFamily: AddressFamily.Unix,
                                                              socketType: SocketType.Stream,
                                                              protocolType: ProtocolType.Unspecified);

            // Bind the socket to the local endpoint and listen for incoming connections.
            try
            {
                NotificationSocketListener.listener.Bind (localEP: endpoint);
                NotificationSocketListener.listener.Listen (backlog: 128);

                while (true)
                {
                    // Set the event to nonsignaled state.
                    NotificationSocketListener.allDone.Reset ();

                    // Start an asynchronous socket to listen for connections.
                    NotificationSocketListener.listener.BeginAccept (callback: NotificationSocketListener.AcceptCallback,
                                                                     state: NotificationSocketListener.listener);

                    // Wait until a connection is made before continuing.
                    NotificationSocketListener.allDone.WaitOne ();
                }
            }
            catch (Exception e)
            {
                Console.WriteLine (value: e.ToString ());
            }
        }

        public static void AcceptCallback (IAsyncResult ar)
        {
            // Signal the main thread to continue.
            NotificationSocketListener.allDone.Set ();

            // Get the socket that handles the client request.
            var    listener = (Socket)ar.AsyncState;
            Socket handler  = listener.EndAccept (asyncResult: ar);

            // Create the state object.
            var state = new StateObject ();
            state.workSocket = handler;

            // Begin receiving.
            handler.BeginReceive (buffer: state.buffer,
                                  offset: 0,
                                  size: StateObject.BufferSize,
                                  socketFlags: 0,
                                  callback: NotificationSocketListener.ReadCallback,
                                  state: state);
        }

        public static void ReadCallback (IAsyncResult ar)
        {
            var content = string.Empty;

            // Retrieve the state object and the handler socket  
            // from the asynchronous state object.  
            var    state   = (StateObject)ar.AsyncState;
            Socket handler = state.workSocket!;

            // Read data from the client socket.
            var bytesRead = handler.EndReceive (asyncResult: ar);

            if (bytesRead > 0)
            {
                // There  might be more data, so store the data received so far.  
                state.sb.Append (value: Encoding.ASCII.GetString (bytes: state.buffer, index: 0, count: bytesRead));

                // Check for end-of-file tag. If it is not there, read
                // more data.  
                content = state.sb.ToString ();

                if (content.IndexOf (value: '\u0004') > -1)

                    // All the data has been read from the
                    // client. Display it on the console.  
                    Console.WriteLine (format: "Read {0} bytes from socket.\nData: \n\n{1}", arg0: content.Length, arg1: content);
                else

                    // Not all data received. Get more.  
                    handler.BeginReceive (buffer: state.buffer,
                                          offset: 0,
                                          size: StateObject.BufferSize,
                                          socketFlags: 0,
                                          callback: NotificationSocketListener.ReadCallback,
                                          state: state);
            }
        }
    }
}
