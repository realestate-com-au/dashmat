import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import ModuleBox from './ModuleBox.jsx';

export default class Number extends Component {
  render() {
    return (
      <ModuleBox color="#3498db">
        <h1 className={styles.heading}>{this.props.title}</h1>
        <span className={styles.value}>{this.props.value}</span>
      </ModuleBox>
    );
  }
}

Number.propTypes = {
  id: PropTypes.string,
  value: PropTypes.number,
  title: PropTypes.string,
};
