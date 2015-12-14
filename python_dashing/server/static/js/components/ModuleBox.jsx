import React, {Component, PropTypes} from 'react';
import styles from './Dashboard.scss';

export default class ModuleBox extends Component {
  render() {
    const style = {
      backgroundColor: this.props.color,
    };
    return <div className={styles.module} style={style}>{this.props.children}</div>;
  }
}

ModuleBox.propTypes = {
  children: PropTypes.array,
  color: PropTypes.string,
};
