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

export default class Dashboard extends Component {
  render() {
    const modules = this.props.rows.map(module => {
      return (
        <ModuleLoader key={module.id} {...module} />
      );
    });

    return (
      <div className={styles.dashboard}>
        {modules}
      </div>
    );
  }
}

Dashboard.propTypes = {
  rows: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      id: PropTypes.string,
    })
  ).isRequired,
};
