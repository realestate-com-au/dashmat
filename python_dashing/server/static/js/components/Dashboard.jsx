import React, {Component, PropTypes} from 'react';
import WidgetBox from './WidgetBox.jsx';
import Number from './Number.jsx';
import BarChart from './BarChart.jsx';
import styles from './Dashboard.css';
import {resolve} from '../utils.js';

export class WidgetLoader extends Component {
  render() {
    const type = this.props.type;
    const widgetProps = {
      data: this.props.data,
      options: this.props.options,
      title: this.props.title,
    };
    // TODO: Load dynamically
    if (type == 'Number') {
      return (<Number {...widgetProps} />);
    }
    if (type == 'BarChart') {
      return (<BarChart {...widgetProps} />);
    }
    return (<WidgetBox>Unknown widget type {this.props.type}</WidgetBox>);
  }
}

WidgetLoader.propTypes = {
  type: PropTypes.string.isRequired,
  title: PropTypes.string,
  options: PropTypes.object,
  data: PropTypes.any,
  // Actually used in Dashboard, not here
  datasource: PropTypes.string,
};

export default class Dashboard extends Component {
  constructor(props) {
    super(props);
    this.state = {data: {}};
  }

  loadData() {
    fetch('/data')
      .then(data => data.json())
      .then(data => {
        this.setState({data: data});
      })
  }

  componentDidMount() {
    // Poll every 5 seconds for data
    setInterval(this.loadData.bind(this), 5000);
    this.loadData();
  }

  render() {
    const modules = this.props.widgets.map((widget, idx) => {
      let data = null;
      if (widget.datasource) {
        data = resolve(this.state.data, widget.datasource);
      }
      return (
        <WidgetLoader key={idx} data={data} {...widget} />
      );
    });
    return (
      <div className={styles.dashboard}>
        {modules}
      </div>
    )
  }
}

Dashboard.propTypes = {
  widgets: PropTypes.arrayOf(
    PropTypes.shape(WidgetLoader.propTypes)
  ).isRequired,
};
