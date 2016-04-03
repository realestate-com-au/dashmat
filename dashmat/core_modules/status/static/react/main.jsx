import React, {Component, PropTypes} from 'react';
import styles from './Status.css';
import moment from 'moment';

export class Status extends Component {
  constructor(props) {
    super(props);
    this.state = {
      offline: false,
    };
  }

  componentDidMount() {
    setInterval(this.check.bind(this), 1000);
  }

  check() {
    const lastUpdated = moment(this.props.lastUpdated);
    const now = moment();
    const minutes = now.diff(lastUpdated, 'minutes');
    this.setState({offline: minutes > 1});
  }

  render() {
    if (this.props.error || this.state.offline) {
      return (
        <div className={styles.container}>
          Offline
        </div>
      );
    }
    return <div style={{display: 'none'}} />;
  }
}

Status.propTypes = {
  lastUpdated: PropTypes.instanceOf(Date),
  error: PropTypes.bool,
};
