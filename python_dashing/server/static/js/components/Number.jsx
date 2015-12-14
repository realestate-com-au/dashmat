import React, {Component, PropTypes} from 'react';

export default class Number extends Component {
  render() {
    return (<div>{this.props.id}</div>)
  }
}

Number.propTypes = {
  id: PropTypes.string,
  value: PropTypes.number,
};
