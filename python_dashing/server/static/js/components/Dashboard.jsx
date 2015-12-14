import React, {Component, PropTypes} from 'react';
import Number from './Number.jsx';
import styles from './Dashboard.css';

export class Module extends Component {
  render() {
    const type = this.props.type;
    if (type == 'Number') {
      return (<Number {...this.props} />);
    }
    return (<div className={styles.module}>{this.props.id}</div>);
  }
}

Module.propTypes = {
  type: PropTypes.string,
  id: PropTypes.string,
};

export class Row extends Component {
  render() {
    const modules = this.props.modules.map(module => {
      return (
        <Module key={module.id} {...module} />
      );
    });
    return (
      <div className={styles.row}>
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
    const rows = this.props.rows.map((row, idx) => {
      return (<Row key={idx} modules={row.modules}/>);
    });

    return (
      <div className={styles.dashboard}>
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
