import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import ModuleBox from './ModuleBox.jsx';

export default class Number extends Component {
  render() {
    return (
      <ModuleBox color="#3498db" className={styles.container}>
        <h1 className={styles.heading}>{this.props.title}</h1>
        <span className={styles.value}>{this.props.data}</span>
      </ModuleBox>
    );
  }
}

Number.propTypes = {
  id: PropTypes.string,
  data: PropTypes.number,
  title: PropTypes.string,
};
