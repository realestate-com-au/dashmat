import React, {Component, PropTypes} from 'react';
import styles from './Number.css';
import WidgetBox from './WidgetBox.jsx';
import {Bar} from 'react-chartjs';

const BarChart = ({data, title='Bar Chart'}) =>
  <WidgetBox color="#3498db" className={styles.container}>
    <h1 className={styles.heading}>{title}</h1>
    <Bar data={data} width="600" height="250"/>
  </WidgetBox>

BarChart.propTypes = {
  data: PropTypes.shape({
    labels: PropTypes.array,
    datasets: PropTypes.array
  }),
  title: PropTypes.string,
};

export default BarChart;
