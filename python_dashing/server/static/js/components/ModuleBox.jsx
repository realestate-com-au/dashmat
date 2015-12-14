import React, {Component, PropTypes} from 'react';
import styles from './Dashboard.css';

export default class ModuleBox extends Component {
  render() {
    const style = {
      backgroundColor: this.props.color,
    };
    let className = styles.module;
    if (this.props.className) {
      className += ' ' + this.props.className;
    }
    return <div className={className} style={style}>{this.props.children}</div>;
  }
}

ModuleBox.propTypes = {
  children: PropTypes.array,
  color: PropTypes.string,
  className: PropTypes.string,
};
