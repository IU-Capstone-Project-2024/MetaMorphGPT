import React, { useState } from 'react';
import './App.css';
import Modal from 'react-modal';
import plusIcon from './plus-icon.png';

Modal.setAppElement('#root');

function App() {
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const openSignupModal = () => {
    setIsSignupModalOpen(true);
  };

  const closeSignupModal = () => {
    setIsSignupModalOpen(false);
  };

  const openLoginModal = () => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = () => {
    setIsLoginModalOpen(false);
  };

  const handleSignup = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    try {
      const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          email, 
          password,
          username: email,  // Присваиваем email в качестве имени пользователя
          is_active: true,
          is_superuser: false,
          is_verified: false,
          status_id: 0
        }),
      });
      if (response.ok) {
        alert("Registration successful!");
        closeSignupModal();
      } else {
        const data = await response.json();
        alert(data.detail);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Registration failed!");
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch("http://localhost:8000/auth/jwt/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
	credentials: 'include',
        body: new URLSearchParams({
          grant_type: '',
          username: email,
          password: password,
          scope: '',
          client_id: '',
          client_secret: ''
        })
      });
      if (response.ok) {
        alert("Login successful!");
        closeLoginModal();
      } else {
        const data = await response.json();
        alert(data.detail);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Login failed!");
    }
  };

  return (
    <div className="App">
      <aside className="sidebar">
        <h2 className="sidebar-title">AI Lab</h2>
        <button className="create-button">
          <img src={plusIcon} alt="Plus Icon" className="plus-icon" />
          Create
        </button>
        <nav className="model-list">
          <button className="model-button">Model 1</button>
          <button className="model-button">Model 2</button>
          <button className="model-button">Model 3</button>
          <button className="model-button">Model 4</button>
        </nav>
        <div className="auth-buttons">
          <button className="auth-button" onClick={openLoginModal}>Sign in</button>
          <button className="auth-button signup" onClick={openSignupModal}>Sign up</button>
        </div>
      </aside>
      <main className="main-content">
        <h1 className="main-title">MetaMorphGPT</h1>
      </main>
      <Modal
        isOpen={isSignupModalOpen}
        onRequestClose={closeSignupModal}
        contentLabel="Sign Up Modal"
        className="Modal"
        overlayClassName="Overlay"
      >
        <div className="modal-content">
          <button className="close-button" onClick={closeSignupModal}>&times;</button>
          <h2 className="modal-title">MetaMorphGPT</h2>
          <p className="modal-subtitle">Create an account</p>
          <form className="modal-form" onSubmit={handleSignup}>
            <label>
              <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label>
              <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
            <label>
              <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            </label>
            <button type="submit" className="signup-button">Sign up</button>
          </form>
          <p className="modal-footer">
            Already have an account? <a href="#" onClick={() => {closeSignupModal(); openLoginModal();}}>Log in</a>
          </p>
        </div>
      </Modal>
      <Modal
        isOpen={isLoginModalOpen}
        onRequestClose={closeLoginModal}
        contentLabel="Log In Modal"
        className="Modal"
        overlayClassName="Overlay"
      >
        <div className="modal-content">
          <button className="close-button" onClick={closeLoginModal}>&times;</button>
          <h2 className="modal-title">MetaMorphGPT</h2>
          <p className="modal-subtitle">Log in to your account</p>
          <form className="modal-form" onSubmit={handleLogin}>
            <label>
              <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label>
              <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
            <button type="submit" className="signup-button">Sign in</button>
          </form>
          <p className="modal-footer">
            Don't have an account? <a href="#" onClick={() => {closeLoginModal(); openSignupModal();}}>Sign up</a>
          </p>
        </div>
      </Modal>
    </div>
  );
}

export default App;
