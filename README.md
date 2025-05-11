# Encrypto

Encrypto is a web application designed to provide users with an interactive platform to explore cryptographic algorithms, experiment with encryption and decryption, and communicate securely through a built-in chat feature. The app is built with modern web technologies and offers a user-friendly interface for both beginners and advanced users interested in cryptography.

## Features

- **Cryptographic Algorithms**: Experiment with popular cryptographic algorithms such as AES, RSA, SHA-256, and more.
- **Encryption and Decryption**: Encrypt and decrypt messages or files using various algorithms.
- **Secure Chat**: Communicate with others securely using end-to-end encryption.
- **Algorithm Visualization**: Visualize how cryptographic algorithms work step-by-step.
- **Cross-Platform Support**: Accessible on both desktop and mobile devices.
- **User Authentication**: Secure login and registration system to protect user data.
- **Dark Mode**: Toggle between light and dark themes for better usability.

## How to Use

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yassincodes404/Encrypto
    cd Encrypto
    ```

2. **Install Dependencies**:
    Ensure you have Node.js and npm installed. Then run:
    ```bash
    npm install
    ```

3. **Run the Application**:
    Start the development server:
    ```bash
    npm start
    ```
    Open your browser and navigate to `http://localhost:3000`.

4. **Explore Features**:
    - Navigate to the "Algorithms" section to experiment with cryptographic algorithms.
    - Use the "Chat" feature to communicate securely with other users.
    - Access the "Help" section for detailed instructions on using the app.

## Development

### Prerequisites

- **Node.js**: Ensure you have Node.js (v14 or later) installed.
- **npm**: Comes bundled with Node.js.
- **Git**: For version control.

### Frameworks and Libraries

- **Frontend**:
  - React.js: For building the user interface.
  - Tailwind CSS: For styling the application.
- **Backend**:
  - Node.js: For server-side logic.
  - Express.js: For handling API requests.
- **Database**:
  - MongoDB: For storing user data and chat messages.
- **Authentication**:
  - JSON Web Tokens (JWT): For secure user authentication.
- **Python**:
  - Flask: For additional backend functionality.
  - Flask-SocketIO: For real-time communication.
  - Flask-SQLAlchemy: For database management.
  - Flask-Login: For user session management.
  - Werkzeug: For password hashing and security utilities.

### Development Steps

1. **Set Up Environment Variables**:
    Create a `.env` file in the root directory and add the following:
    ```
    MONGO_URI=your_mongodb_connection_string
    JWT_SECRET=your_jwt_secret
    ```

2. **Run the Backend**:
    Start the backend server:
    ```bash
    npm run server
    ```

3. **Run the Frontend**:
    Start the frontend development server:
    ```bash
    npm start
    ```

4. **Build for Production**:
    To create a production build, run:
    ```bash
    npm run build
    ```

## Dependencies

- **React**: `^18.0.0`
- **Express**: `^4.18.0`
- **MongoDB**: `^5.0.0`
- **Tailwind CSS**: `^3.0.0`
- **jsonwebtoken**: `^9.0.0`
- **bcrypt**: `^5.0.0`
- **Flask**: `^2.0.0`
- **Flask-SocketIO**: `^5.0.0`
- **Flask-SQLAlchemy**: `^2.5.0`
- **Flask-Login**: `^0.5.0`
- **Werkzeug**: `^2.0.0`

## Contributing

We welcome contributions! Please fork the repository, create a new branch, and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact us at `support@encryptoapp.com`.
