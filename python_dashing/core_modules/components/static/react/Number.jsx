import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import WidgetBox from './WidgetBox.jsx';

export default class Number extends Component {
  render() {
    return (
      <WidgetBox color="#3498db" className={styles.container}>
        <h1 className={styles.heading}>{this.props.title}</h1>
        <span className={styles.value}>{this.props.data}</span>
      </WidgetBox>
    );
  }
}

Number.propTypes = {
  data: PropTypes.number,
  title: PropTypes.string,
};
