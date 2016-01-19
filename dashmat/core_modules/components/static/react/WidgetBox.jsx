import React, {Component, PropTypes} from 'react';
import styles from '/modules/dashmat.server/Dashboard.css';

export default class WidgetBox extends Component {
  constructor(props) {
    super(props);
    this.state = {data: this.props.data, width: this.props.width, height: this.props.height};
  }

  render() {
    if (this.state.data === undefined) {
      return <p>Waiting...</p>;
    }

    const style = {
      backgroundColor: this.props.color
    }

    if (this.state.width !== undefined) {
      if (this.state.width == "auto") {
        style.width = "auto";
      } else {
        style.width = Math.ceil(this.state.width) + "px";
      }
    } else {
      style.maxWidth = "200px";
    }

    if (this.state.height !== undefined) {
      if (this.state.height == "auto") {
        style.height = "auto";
      } else {
        style.height = Math.ceil(this.state.height) + "px";
      }
    }

    let className = styles.widget;
    if (this.props.className) {
      className += ' ' + this.props.className;
    }
    return <div className={className} style={style}>{this.render_inner().props.children}</div>;
  }

  loadData() {
    fetch(this.props.datasource)
      .then(data => data.json())
      .then(data => {
        this.setState({data: data});
      })
  }

  componentDidMount() {
    // Poll every "every" seconds for data
    setInterval(this.loadData.bind(this), this.props.every || 30000);
    this.loadData();
  }
}

WidgetBox.propTypes = {
  width: PropTypes.any,
  height: PropTypes.any,
  every: PropTypes.number,
  children: PropTypes.array,
  color: PropTypes.string,
  className: PropTypes.string,
  datasource: PropTypes.string.isRequired
};

