import React, {PropTypes} from 'react';
import styles from './Number.css';
import WidgetBox from './WidgetBox.jsx';

export default class Number extends WidgetBox {
  render_inner() {
    return (
      <div>
        <h1 className={styles.heading}>{this.props.title}</h1>
        <span className={styles.value}>{this.state.data}</span>
      </div>
    );
  }
}

Number.propTypes = {
  ...WidgetBox.propTypes,
  data: PropTypes.number,
  title: PropTypes.string,
};
