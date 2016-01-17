import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import WidgetBox from './WidgetBox.jsx';
import {Bar} from 'react-chartjs';

export default class BarChart extends WidgetBox {
  render_inner() {
    return (
      <div>
        <h1 className={styles.heading}>{this.props.title}</h1>
        <Bar data={this.state.data} width="600" height="250"/>
      </div>
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

