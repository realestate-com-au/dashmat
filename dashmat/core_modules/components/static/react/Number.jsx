import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import WidgetBox from './WidgetBox.jsx';

export default class Number extends Component {
  render() {
    return (
      <WidgetBox {...this.props}>
        <h1 className={styles.heading}>{this.props.title}</h1>
        <span className={styles.value}>{this.props.data}</span>
      </WidgetBox>
    );
  }
}

Number.propTypes = {
  ...WidgetBox.propTypes,
  data: PropTypes.number,
  title: PropTypes.string,
};
