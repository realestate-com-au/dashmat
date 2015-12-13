import React from 'react';
import ReactDOM from 'react-dom';
import Dashboard from './components/Dashboard.jsx';

export default () => {
  console.log('test');
  const element = React.createElement(Dashboard);
  ReactDOM.render(element, document.getElementById('page-content'));
  console.log(document.getElementById('page-content'));
}
