import React from 'react';
import ReactDOM from 'react-dom';
import './App.scss';
import App from './App.jsx';

window.pywebview = {
  api: {}
};

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
