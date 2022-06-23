using System;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;

namespace Arkane.NotificationsWsl.Interface
{
    /// <summary>
    ///     State class for reading client data asynchronously.
    /// </summary>
    internal class StateObject
    {
        // Size of receive buffer.
        internal const int BufferSize = 4096;

        // Receive buffer.
        internal byte[] buffer = new byte[BufferSize];

        // Received data string.
        internal StringBuilder sb = new StringBuilder(BufferSize);

        // Client socket.
        internal Socket? workSocket = null;
    }
}
