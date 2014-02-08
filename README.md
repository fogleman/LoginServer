## Login Server

Online multiplayer game login server for secure user authentication. Written in Python using Flask.

https://craft.michaelfogleman.com/

### User Registration

   * The user visits the web front-end of the login server to register for a new account.
   * After registering and logging in, the user can manage “identity tokens.”
   * The user creates an identity token which is copied and pasted into the game client.
   * An identity token looks like: 717e3c1a034247ef91e6b78dd8088b77
   * The game client saves the username and identity token to use for future logins.
   * The user can revoke any identity token at any time. The identity tokens are more secure than regular passwords and the user doesn’t need to reuse or make up a new password.

### Login Process

   * Game Client contacts Login Server over secure HTTPS.
   * Game Client sends stored username and identity token to Login Server.
   * Login Server checks for matching identity token in database (they are salted and hashed just like passwords).
   * If the identity token is valid, the Login Server creates a new, short-lived access token. This is sent back to the Game Client.
   * The Game Client sends the access token to the Game Server (this connection is plain text because we don’t need / want encrypted communication for game play). Access tokens can only be used once and expire in one minute.
   * The Game Server sends the access token to the Login Server.
   * If the access token is valid, unexpired and unused, the Login Server confirms a successful login and sends user information to the Game Server, such as a distinct user ID.
   * The Game Server can then use the user information as needed. The user is now logged in.

### Implementation Details

   * The Game Client is written in C. It uses libcurl to easily perform HTTPS POSTs to the Login Server. It uses plain sockets for communication with the Game Server.
   * The Game Server is written in Python. It uses the requests module to communicate with the Login Server.
   * The Login Server is written in Python and uses the Flask web framework.
