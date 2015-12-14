import React, {Component, PropTypes} from 'react';
import ModuleBox from './ModuleBox.jsx';
import Number from './Number.jsx';
import styles from './Dashboard.css';

export class ModuleLoader extends Component {
  render() {
    const type = this.props.type;
    // TODO: Load dynamically
    if (type == 'Number') {
      return (<Number {...this.props} />);
    }
    return (<ModuleBox>Unknown module type {this.props.type}</ModuleBox>);
  }
}

ModuleLoader.propTypes = {
  type: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  data: PropTypes.any,
};

export class Row extends Component {
  render() {
    const modules = this.props.modules.map(module => {
      return (
        <ModuleLoader key={module.id} {...module} />
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
  ).isRequired,
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
  ).isRequired,
};
