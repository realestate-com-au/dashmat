import React, {Component, PropTypes} from 'react';
import WidgetBox from './WidgetBox.jsx';
import Number from './Number.jsx';
import styles from './Dashboard.css';

export class WidgetLoader extends Component {
  render() {
    const type = this.props.type;
    // TODO: Load dynamically
    if (type == 'Number') {
      return (<Number {...this.props} />);
    }
    return (<WidgetBox>Unknown widget type {this.props.type}</WidgetBox>);
  }
}

WidgetLoader.propTypes = {
  type: PropTypes.string.isRequired,
  data: PropTypes.any,
};

export class Row extends Component {
  render() {
    const modules = this.props.widgets.map((widget, idx) => {
      return (
        <WidgetLoader key={idx} {...widget} />
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
  widgets: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
    })
  ).isRequired,
};


export default class Dashboard extends Component {
  render() {
    const rows = this.props.rows.map((row, idx) => {
      return (<Row key={idx} widgets={row}/>);
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
    Row.propTypes['widgets']
  ).isRequired,
};
