import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import './utils/testApi'

// Ensure DOM is loaded and add error handling
console.log('🚀 Starting React application...');
const rootElement = document.getElementById('root');

if (!rootElement) {
  console.error('❌ Root element not found!');
} else {
  console.log('✅ Root element found, creating React root...');
  try {
    const root = ReactDOM.createRoot(rootElement);
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
    console.log('✅ React application mounted successfully!');
  } catch (error) {
    console.error('❌ Failed to mount React application:', error);
  }
} 