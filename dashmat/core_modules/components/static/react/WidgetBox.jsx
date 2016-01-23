import React, {Component, PropTypes} from 'react';
import styles from '/modules/dashmat.server/Dashboard.css';

export default class WidgetBox extends Component {
  makeStyle() {
    const style = {
      backgroundColor: this.props.color
    }

    if (this.props.width !== undefined) {
      if (this.props.width == "auto") {
        style.width = "auto";
      } else {
        style.width = Math.ceil(this.props.width) + "px";
      }
    } else {
      style.maxWidth = "200px";
    }

    if (this.props.height !== undefined) {
      if (this.props.height == "auto") {
        style.height = "auto";
      } else {
        style.height = Math.ceil(this.props.height) + "px";
      }
    }
  }

  render() {
    if (this.props.data === undefined) {
      return <p>Waiting...</p>;
    }

    let className = styles.widget;
    if (this.props.className) {
      className += ' ' + this.props.className;
    }
    return <div className={className} style={this.makeStyle()}>{this.props.children}</div>;
  }
}

WidgetBox.propTypes = {
  data: PropTypes.any,
  width: PropTypes.any,
  height: PropTypes.any,
  color: PropTypes.string,
  children: PropTypes.any,
  className: PropTypes.string
};

