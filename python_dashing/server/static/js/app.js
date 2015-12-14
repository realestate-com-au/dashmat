import React from 'react';
import ReactDOM from 'react-dom';
import Dashboard from './components/Dashboard.jsx';

export default (config) => {
  const element = React.createElement(Dashboard, config);
  ReactDOM.render(element, document.getElementById('page-content'));
}
