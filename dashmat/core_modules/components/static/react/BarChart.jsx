import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import WidgetBox from './WidgetBox.jsx';
import {Bar} from 'react-chartjs';

export default class BarChart extends Component {
  render() {
    return (
      <WidgetBox {...this.props}>
        <h1 className={styles.heading}>{this.props.title}</h1>
        <Bar data={this.props.data} width="600" height="250"/>
      </WidgetBox>
    )
  }
}

BarChart.propTypes = {
  ...WidgetBox.propTypes,

  data: PropTypes.shape({
    labels: PropTypes.array,
    datasets: PropTypes.array
  }),

  title: PropTypes.string,
};

