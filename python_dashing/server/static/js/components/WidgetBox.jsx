import React, {Component, PropTypes} from 'react';
import styles from './Dashboard.css';

export default class WidgetBox extends Component {
  render() {
    const style = {
      backgroundColor: this.props.color,
    };
    let className = styles.widget;
    if (this.props.className) {
      className += ' ' + this.props.className;
    }
    return <div className={className} style={style}>{this.props.children}</div>;
  }
}

WidgetBox.propTypes = {
  children: PropTypes.array,
  color: PropTypes.string,
  className: PropTypes.string,
};
