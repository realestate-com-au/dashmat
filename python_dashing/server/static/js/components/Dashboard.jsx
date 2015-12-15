import React, {Component, PropTypes} from 'react';
import WidgetBox from './WidgetBox.jsx';
import Number from './Number.jsx';
import styles from './Dashboard.css';
import callAjax from '../utils.js';

export class WidgetLoader extends Component {
  constructor(props) {
    super(props)
    this.state = {data: null}
  }

  loadData() {
    callAjax('/data/' + this.props.module, (data) => {
      data = JSON.parse(data);
      this.setState({data: data});
    })
  }

  componentDidMount() {
    if (this.props.module) {
      setInterval(this.loadData.bind(this), 5000);
      this.loadData();
    }
  }

  render() {
    const type = this.props.type;
    const widgetProps = {
      data: this.state.data,
      options: this.props.options,
      title: this.props.title,
    }
    // TODO: Load dynamically
    if (type == 'Number') {
      return (<Number {...widgetProps} />);
    }
    return (<WidgetBox>Unknown widget type {this.props.type}</WidgetBox>);
  }
}

WidgetLoader.propTypes = {
  type: PropTypes.string.isRequired,
  title: PropTypes.string,
  module: PropTypes.string,
  options: PropTypes.object,
};

export default class Dashboard extends Component {
  render() {
    const modules = this.props.widgets.map((widget, idx) => {
      return (
        <WidgetLoader key={idx} {...widget} />
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
