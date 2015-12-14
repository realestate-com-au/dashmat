import React, {Component, PropTypes} from 'react';

export class Module extends Component {
  render() {
    return (<div>{this.props.id}</div>);
  }
}

export class Row extends Component {
  render() {
    const modules = this.props.modules.map(module => {
      return (
        <div key={module.id}>{module.type}</div>
      );
    });
    return (
      <div class="row">
        {modules}
      </div>
    )
  }
}

Row.propTypes = {
  modules: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      id: PropTypes.string,
    })
  ),
};


export default class Dashboard extends Component {
  render() {
    const rows = this.props.rows.map(row => {
      return (<Row modules={row.modules}/>);
    });

    return (
      <div>
        <h1>Hello World</h1>
        {rows}
      </div>
    );
  }
}

Dashboard.propTypes = {
  rows: PropTypes.arrayOf(
    PropTypes.shape(Row.PropTypes)
  ),
};
